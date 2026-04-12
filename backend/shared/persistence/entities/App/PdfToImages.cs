namespace ContentProcessing.Persistence.Entities.App;

public class PdfToImages
{
    public Guid Id { get; set; }
    public string PdfPath { get; set; } = string.Empty;
    public Guid? FirstPageImageId { get; set; }
    public Image? FirstPageImage { get; set; }
     // CHAR(64) NOT NULL — SHA-256 hex hash of the PDF
    public string PdfSha256 { get; set; } = string.Empty;
    public PdfToImagesStatus Status { get; set; }
    public string? ErrorMessage { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset UpdatedAt { get; set; }
    public ICollection<Image> Images { get; set; } = new List<Image>();
}