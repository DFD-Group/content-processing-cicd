namespace AuthService.Models;

public class CreateApiKeyRequest
{
    public string? Name { get; set; }
    public string[]? Scopes { get; set; }
    public DateTimeOffset? ExpiresAt { get; set; }
}