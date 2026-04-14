namespace AuthService.Models;

public class ApiKeyDto
{
    public Guid ApiKeyId { get; set; }
    public string? Name { get; set; }
    public string[]? Scopes { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset? ExpiresAt { get; set; }
     // Null = still active; populated = revoked
    public DateTimeOffset? RevokedAt { get; set; }
    public string? CreatedBy { get; set; }
}