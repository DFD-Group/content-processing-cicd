namespace PdfRendererService.Services;

public interface IPdfConversionService
{
    Task ConvertPdfAsync(Guid pdfToImagesId, Stream pdfStream, string originalFileName, CancellationToken cancellationToken = default);

}
