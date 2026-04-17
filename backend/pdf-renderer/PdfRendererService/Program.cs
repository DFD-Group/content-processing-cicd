using System.Security.Cryptography;
using System.Threading.Channels;
using ContentProcessing.Persistence;
using ContentProcessing.Persistence.Entities.App;
using Microsoft.EntityFrameworkCore;
using PdfRendererService.Background;
using PdfRendererService.Filters;
using PdfRendererService.Middleware;
using PdfRendererService.Services;

var builder = WebApplication.CreateBuilder(args);

var connectionString = builder.Configuration.GetConnectionString("ContentProcessing")
    ?? Environment.GetEnvironmentVariable("CONTENT_PROCESSING_CONNECTION_STRING");

builder.Services.AddDbContext<ContentProcessingDbContext>(options =>
    options.UseNpgsql(connectionString)
    .UseSnakeCaseNamingConvention());

// builder.Services.AddHttpClient("AuthService", client =>
// {
//     client.BaseAddress = new Uri(
//         builder.Configuration["AuthService:BaseUrl"]
//         ?? throw new InvalidOperationException("AuthService:BaseUrl is not configured"));
// });

builder.Services.Configure<FileStorageOptions>(builder.Configuration.GetSection(FileStorageOptions.SectionName));
builder.Services.Configure<PdfConversionOptions>(builder.Configuration.GetSection(PdfConversionOptions.SectionName));
builder.Services.AddScoped<IPdfConversionService, PdfConversionService>();

var pdfQueue = Channel.CreateBounded<PdfConversionWorkItem>(new BoundedChannelOptions(32)
{
    FullMode = BoundedChannelFullMode.Wait,
    SingleReader = true,
    SingleWriter = false,
});
builder.Services.AddSingleton(pdfQueue);
builder.Services.AddSingleton(pdfQueue.Reader);
builder.Services.AddSingleton(pdfQueue.Writer);
builder.Services.AddHostedService<PdfConversionBackgroundService>();

builder.Host.UseWindowsService();

var app = builder.Build();

// app.UseMiddleware<ApiKeyAuthMiddleware>();

app.MapGet("/health", () => Results.Json(new { status = "UP" }));

app.MapPost("/pdf-to-images", UploadPdfToImages)
    .DisableAntiforgery();
// .AddEndpointFilter((ctx, next) => RequireScopeFilter.RequireScope(ctx, next, "content:write"));

app.Run();

static async Task<IResult> UploadPdfToImages(
    IFormFile file,
    ContentProcessingDbContext db,
    ChannelWriter<PdfConversionWorkItem> queue,
    CancellationToken cancellationToken)
{
    if (file.Length == 0)
    {
        return Results.BadRequest(new { error = "Empty file." });
    }

    if (!string.Equals(Path.GetExtension(file.FileName), ".pdf", StringComparison.OrdinalIgnoreCase)
        && !string.Equals(file.ContentType, "application/pdf", StringComparison.OrdinalIgnoreCase))
    {
        return Results.BadRequest(new { error = "Expected a PDF file." });
    }

    var jobId = Guid.NewGuid();
    var tempDir = Path.Combine(Path.GetTempPath(), "pdf-renderer");
    Directory.CreateDirectory(tempDir);
    var tempPath = Path.Combine(tempDir, $"{jobId:N}.pdf");

    await using (var output = new FileStream(tempPath, FileMode.Create, FileAccess.Write, FileShare.None, 65536, FileOptions.Asynchronous))
    {
        await file.CopyToAsync(output, cancellationToken);
    }

    var pdfSha256 = await ComputeSha256HexForFileAsync(tempPath, cancellationToken);

    var now = DateTimeOffset.UtcNow;
    db.PdfToImages.Add(new PdfToImages
    {
        Id = jobId,
        PdfPath = tempPath,
        PdfSha256 = pdfSha256,
        CreatedAt = now,
        UpdatedAt = now,
    });

    await db.SaveChangesAsync(cancellationToken);

    await queue.WriteAsync(new PdfConversionWorkItem(jobId, tempPath, file.FileName), cancellationToken);

    return Results.Accepted($"/pdf-to-images/{jobId}", new { id = jobId });
}

static async Task<string> ComputeSha256HexForFileAsync(string filePath, CancellationToken cancellationToken)
{
    await using var stream = new FileStream(filePath, FileMode.Open, FileAccess.Read, FileShare.Read, 65536, FileOptions.Asynchronous);
    var hash = await SHA256.HashDataAsync(stream, cancellationToken);
    return Convert.ToHexString(hash).ToLowerInvariant();
}
