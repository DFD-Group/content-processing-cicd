namespace PdfRendererService.Background;

public sealed record PdfConversionWorkItem(Guid JobId, string TempPdfPath, string OriginalFileName);
