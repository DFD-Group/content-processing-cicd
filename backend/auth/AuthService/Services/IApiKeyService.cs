namespace AuthService.Services;

using OneOf;
using AuthService.Models;

public interface IApiKeyService
{
    Task<OneOf<CreateApiKeyResponse, ArgumentException>> CreateAsync(CreateApiKeyRequest request);
    Task<ApiKeyDto?> VerifyAsync(string rawKey);
    Task<List<ApiKeyDto>> ListAsync();
    Task<ApiKeyDto?> GetByIdAsync(Guid apiKeyId);
    Task<bool> RevokeAsync(Guid apiKeyId);
}