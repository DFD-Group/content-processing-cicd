namespace ContentProcessing.Persistence.Entities.Auth;

public class ApiKey
{
    public Guid ApiKeyId { get; set; }
    public string SecretHash { get; set; } = string.Empty;
    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset? ExpiresAt { get; set; }
    public DateTimeOffset? RevokedAt { get; set; }
    public string[]? Scopes { get; set; }
    public string? Name { get; set; }
    public string? CreatedBy { get; set; }
}