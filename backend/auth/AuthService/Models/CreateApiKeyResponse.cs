namespace AuthService.Models;

public class CreateApiKeyResponse
{
    public Guid ApiKeyId { get; set; }
    // The full composite key "cp_{id}_{secret}" -- shown only once, never stored
    public string RawKey { get; set; } = string.Empty;
    public string? Name { get; set; }
    public string[]? Scopes { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset? ExpiresAt { get; set; }
}