namespace AuthService.Models;

public class VerifyApiKeyRequest
{
    public string RawKey { get; set; } = string.Empty;
}