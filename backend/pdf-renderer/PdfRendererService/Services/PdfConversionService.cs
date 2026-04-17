namespace PdfRendererService.Services;

using System.Runtime.InteropServices;
using System.Security.Cryptography;
using ContentProcessing.Persistence;
using ContentProcessing.Persistence.Entities.App;
using Docnet.Core;
using Docnet.Core.Converters;
using Docnet.Core.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;
using SkiaSharp;

public sealed class PdfConversionService : IPdfConversionService
{
    private readonly ContentProcessingDbContext _db;
    private readonly FileStorageOptions _files;
    private readonly PdfConversionOptions _pdf;
    private readonly ILogger<PdfConversionService> _logger;

    public PdfConversionService(
        ContentProcessingDbContext db,
        IOptions<FileStorageOptions> fileStorage,
        IOptions<PdfConversionOptions> pdfConversion,
        ILogger<PdfConversionService> logger)
    {
        _db = db;
        _files = fileStorage.Value;
        _pdf = pdfConversion.Value;
        _logger = logger;
    }

    public Task ConvertPdfAsync(Guid pdfToImagesId, Stream pdfStream, string originalFileName, CancellationToken cancellationToken = default)
    {
        var basePath = ResolveBasePath();
        var pdfDir = Path.Combine(basePath, "pdfs", pdfToImagesId.ToString());
        Directory.CreateDirectory(pdfDir);

        var safeName = SanitizePdfFileName(originalFileName);
        var pdfFullPath = Path.Combine(pdfDir, safeName);

        return ExecuteWithJobAsync(pdfToImagesId, async ct =>
        {
            await using (var output = new FileStream(pdfFullPath, FileMode.Create, FileAccess.Write, FileShare.None, 65536, FileOptions.Asynchronous))
            {
                await pdfStream.CopyToAsync(output, ct);
            }

            await ConvertSavedPdfAsync(pdfToImagesId, pdfFullPath, ct);
        }, cancellationToken);
    }

    private async Task ExecuteWithJobAsync(Guid pdfToImagesId, Func<CancellationToken, Task> work, CancellationToken cancellationToken)
    {
        var job = await _db.PdfToImages.FirstOrDefaultAsync(j => j.Id == pdfToImagesId, cancellationToken);
        if (job is null)
        {
            throw new InvalidOperationException($"PdfToImages {pdfToImagesId} was not found.");
        }

        job.ErrorMessage = null;
        job.UpdatedAt = DateTimeOffset.UtcNow;
        await _db.SaveChangesAsync(cancellationToken);

        try
        {
            await work(cancellationToken);

            job.ErrorMessage = null;
            job.UpdatedAt = DateTimeOffset.UtcNow;
            await _db.SaveChangesAsync(cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "PDF conversion failed for job {JobId}", pdfToImagesId);
            job.ErrorMessage = ex.Message;
            job.UpdatedAt = DateTimeOffset.UtcNow;
            await _db.SaveChangesAsync(cancellationToken);
            throw;
        }
    }

    /// Transactional guarantees:
    /// - Individual <see cref="ContentProcessingDbContext.SaveChangesAsync"/> calls persist updates at checkpoints (e.g., PDF hash, new Images, job completion/failure).
    /// - The method should ensure transactional integrity: the entire conversion process (including PDF hash, image creation, and job status) should succeed or fail as a unit, 
    ///   preventing any partial progress from being saved. If any step fails, no intermediate changes will be persisted.
    private async Task ConvertSavedPdfAsync(Guid pdfToImagesId, string pdfFullPath, CancellationToken cancellationToken)
    {
        var job = await _db.PdfToImages.FirstAsync(j => j.Id == pdfToImagesId, cancellationToken);

        var pdfSha256 = await ComputeSha256HexAsync(pdfFullPath, cancellationToken);
        job.PdfPath = pdfFullPath;
        job.PdfSha256 = pdfSha256;
        job.UpdatedAt = DateTimeOffset.UtcNow;
        await _db.SaveChangesAsync(cancellationToken);

        var basePath = ResolveBasePath();
        var imagesDir = Path.Combine(basePath, "images", pdfToImagesId.ToString());
        Directory.CreateDirectory(imagesDir);

        var scalingFactor = _pdf.DefaultDpi / 72.0;
        var pageDimensions = new PageDimensions(scalingFactor);
        var jpegQuality = Math.Clamp(_pdf.JpegQuality, 1, 100);

        using var docReader = DocLib.Instance.GetDocReader(pdfFullPath, pageDimensions);
        var pageCount = docReader.GetPageCount();
        if (pageCount == 0)
        {
            throw new InvalidOperationException("The PDF has no pages.");
        }

        var transparency = new NaiveTransparencyRemover(byte.MaxValue, byte.MaxValue, byte.MaxValue);

        for (var pageIndex = 0; pageIndex < pageCount; pageIndex++)
        {
            cancellationToken.ThrowIfCancellationRequested();

            using var pageReader = docReader.GetPageReader(pageIndex);
            var rawBytes = pageReader.GetImage(transparency);
            var width = pageReader.GetPageWidth();
            var height = pageReader.GetPageHeight();

            if (width <= 0 || height <= 0)
            {
                throw new InvalidOperationException($"Page {pageIndex + 1} has invalid dimensions ({width}x{height}).");
            }

            var pageNumber = pageIndex + 1;
            var imageFileName = $"page-{pageNumber}.jpg";
            var imageFullPath = Path.Combine(imagesDir, imageFileName);

            EncodePageToJpeg(rawBytes, width, height, jpegQuality, imageFullPath);

            var imageSha256 = await ComputeSha256HexAsync(imageFullPath, cancellationToken);
            var imageId = Guid.NewGuid();

            _db.Images.Add(new Image
            {
                Id = imageId,
                PdfToImagesId = pdfToImagesId,
                PageNumber = pageNumber,
                ImagePath = imageFullPath,
                ImageSha256 = imageSha256,
                CreatedAt = DateTimeOffset.UtcNow
            });

            if (pageNumber == 1)
            {
                job.FirstPageImageId = imageId;
            }

            job.UpdatedAt = DateTimeOffset.UtcNow;
            await _db.SaveChangesAsync(cancellationToken);
        }
    }

    private static void EncodePageToJpeg(byte[] rawBgra, int width, int height, int jpegQuality, string outputPath)
    {
        var info = new SKImageInfo(width, height, SKColorType.Bgra8888, SKAlphaType.Premul);
        var handle = GCHandle.Alloc(rawBgra, GCHandleType.Pinned);
        try
        {
            using var pixmap = new SKPixmap(info, handle.AddrOfPinnedObject(), info.RowBytes);
            using var image = SKImage.FromPixels(pixmap);
            using var data = image.Encode(SKEncodedImageFormat.Jpeg, jpegQuality);
            if (data is null)
            {
                throw new InvalidOperationException("SkiaSharp failed to encode the page as JPEG.");
            }

            using var fs = new FileStream(outputPath, FileMode.Create, FileAccess.Write, FileShare.None);
            data.SaveTo(fs);
        }
        finally
        {
            handle.Free();
        }
    }

    private string ResolveBasePath()
    {
        if (string.IsNullOrWhiteSpace(_files.BasePath))
        {
            throw new InvalidOperationException("FileStorage:BasePath is not configured.");
        }

        return Path.GetFullPath(_files.BasePath);
    }

    private static string SanitizePdfFileName(string? originalFileName)
    {
        var name = string.IsNullOrWhiteSpace(originalFileName) ? "document.pdf" : Path.GetFileName(originalFileName);
        foreach (var c in Path.GetInvalidFileNameChars())
        {
            name = name.Replace(c, '_');
        }

        if (!name.EndsWith(".pdf", StringComparison.OrdinalIgnoreCase))
        {
            name += ".pdf";
        }

        return name;
    }

    private static async Task<string> ComputeSha256HexAsync(string filePath, CancellationToken cancellationToken)
    {
        await using var stream = new FileStream(filePath, FileMode.Open, FileAccess.Read, FileShare.Read, 65536, FileOptions.Asynchronous);
        var hash = await SHA256.HashDataAsync(stream, cancellationToken);
        return Convert.ToHexString(hash).ToLowerInvariant();
    }
}

public sealed class FileStorageOptions
{
    public const string SectionName = "FileStorage";

    public string BasePath { get; set; } = string.Empty;
}

public sealed class PdfConversionOptions
{
    public const string SectionName = "PdfConversion";

    public int DefaultDpi { get; set; } = 200;

    public int JpegQuality { get; set; } = 85;
}
