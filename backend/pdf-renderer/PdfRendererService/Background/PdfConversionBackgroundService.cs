namespace PdfRendererService.Background;

using PdfRendererService.Services;
using System.Threading.Channels;

public sealed class PdfConversionBackgroundService : BackgroundService
{
    private readonly ChannelReader<PdfConversionWorkItem> _reader;
    private readonly IServiceScopeFactory _scopeFactory;
    private readonly ILogger<PdfConversionBackgroundService> _logger;

    public PdfConversionBackgroundService(
        ChannelReader<PdfConversionWorkItem> reader,
        IServiceScopeFactory scopeFactory,
        ILogger<PdfConversionBackgroundService> logger)
    {
        _reader = reader;
        _scopeFactory = scopeFactory;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        await foreach (var item in _reader.ReadAllAsync(stoppingToken))
        {
            try
            {
                await using var scope = _scopeFactory.CreateAsyncScope();
                var converter = scope.ServiceProvider.GetRequiredService<IPdfConversionService>();
                await using var pdfStream = new FileStream(
                    item.TempPdfPath,
                    FileMode.Open,
                    FileAccess.Read,
                    FileShare.Read,
                    bufferSize: 65536,
                    FileOptions.Asynchronous);

                await converter.ConvertPdfAsync(item.JobId, pdfStream, item.OriginalFileName, stoppingToken);
            }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                _logger.LogError(ex, "Background PDF conversion failed for job {JobId}", item.JobId);
            }
            finally
            {
                TryDeleteTempFile(item.TempPdfPath);
            }
        }
    }

    private static void TryDeleteTempFile(string path)
    {
        try
        {
            if (File.Exists(path))
            {
                File.Delete(path);
            }
        }
        catch
        {
            // Avoid crashing the host if another handle still has the file.
        }
    }
}
