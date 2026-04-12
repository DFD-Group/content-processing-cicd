namespace ContentProcessing.Persistence.Entities.App;

public class Image
{
    public Guid Id { get; set; }
    public string ImagePath { get; set; } = string.Empty;
    public string ImageSha256 { get; set; } = string.Empty;
    public int PageNumber { get; set; }
    public Guid PdfToImagesId { get; set; }
    public PdfToImages? PdfToImages { get; set; } = null;
    public DateTimeOffset CreatedAt { get; set; }
}