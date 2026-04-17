namespace AuthService.Services;

using OneOf;
using System.Security.Cryptography;
using System.Text;
using AuthService.Models;
using ContentProcessing.Persistence;
using ContentProcessing.Persistence.Entities.Auth;
using Microsoft.EntityFrameworkCore;

public class ApiKeyService : IApiKeyService
{
    private readonly ContentProcessingDbContext _db;
    private readonly string? _pepper;

    public ApiKeyService(ContentProcessingDbContext db, IConfiguration configuration)
    {
        _db = db;
        _pepper = configuration["ApiKeys:Pepper"];
    }

    private static readonly HashSet<string> AllowedScopes = new()
    {
        "content:read",
        "content:write",
        "iam:admin"
    };

    public async Task<OneOf<CreateApiKeyResponse, ArgumentException>> CreateAsync(CreateApiKeyRequest request)
    {
        if (request.Scopes is { Length: > 0 })
        {
            var invalid = request.Scopes.Where(s => !AllowedScopes.Contains(s)).ToArray();
            if (invalid.Length > 0)
            {
                return new ArgumentException(
                    $"Invalid scopes: {string.Join(", ", invalid)}. " +
                    $"Allowed values: {string.Join(", ", AllowedScopes)}");
            }
        }

        var secretBytes = RandomNumberGenerator.GetBytes(24);
        var rawSecret = Convert.ToHexString(secretBytes).ToLowerInvariant();

        var payload = (_pepper ?? "") + rawSecret;
        var hashBytes = SHA256.HashData(Encoding.UTF8.GetBytes(payload));
        var secretHash = Convert.ToHexString(hashBytes).ToLowerInvariant();

        var entity = new ApiKey
        {
            SecretHash = secretHash,
            Scopes = request.Scopes,
            Name = request.Name,
            ExpiresAt = request.ExpiresAt,
            CreatedBy = null
        };

        _db.ApiKeys.Add(entity);
        await _db.SaveChangesAsync();

        return new CreateApiKeyResponse
        {
            ApiKeyId = entity.ApiKeyId,
            RawKey = $"cp_{entity.ApiKeyId}_{rawSecret}",
            Name = request.Name,
            Scopes = request.Scopes,
            CreatedAt = DateTimeOffset.UtcNow,
        };
    }

    public async Task<ApiKeyDto?> VerifyAsync(string rawKey)
    {
        if (!rawKey.StartsWith("cp_"))
            return null;

        var withoutPrefix = rawKey["cp_".Length..];
        if (withoutPrefix.Length < 36 + 1 + 1)
            return null;

        var idPart = withoutPrefix[..36];
        var secretPart = withoutPrefix[37..];

        if (!Guid.TryParse(idPart, out var id))
            return null;

        var entity = await _db.ApiKeys
            .AsNoTracking()
            .FirstOrDefaultAsync(a => a.ApiKeyId == id);
        
        if (entity is null || entity.RevokedAt is not null)
            return null;

        if (entity.ExpiresAt is not null && entity.ExpiresAt < DateTimeOffset.UtcNow)
            return null;

        var payload = (_pepper ?? "") + secretPart;
        var hashBytes = SHA256.HashData(Encoding.UTF8.GetBytes(payload));
        var secretHash = Convert.ToHexString(hashBytes).ToLowerInvariant();

        var storedHashBytes = Encoding.UTF8.GetBytes(entity.SecretHash);
        var computedHashBytes = Encoding.UTF8.GetBytes(secretHash);

        if (CryptographicOperations.FixedTimeEquals(storedHashBytes, computedHashBytes))
            return MapToDto(entity);

        return null;
    }

    public async Task<List<ApiKeyDto>> ListAsync()
    {
        return await _db.ApiKeys
            .AsNoTracking()
            .Where(a => a.RevokedAt == null)
            .OrderByDescending(a => a.CreatedAt)
            .Select(a => MapToDto(a))
            .ToListAsync();
    }

    public async Task<ApiKeyDto?> GetByIdAsync(Guid apiKeyId)
    {
        var entity = await _db.ApiKeys
            .AsNoTracking()
            .FirstOrDefaultAsync(a => a.ApiKeyId == apiKeyId);
        
        return entity is null ? null : MapToDto(entity);
    }

    public async Task<bool> RevokeAsync(Guid apiKeyId)
    {
        var rowsAffected = await _db.ApiKeys
        .Where(k => k.ApiKeyId == apiKeyId)
        .ExecuteUpdateAsync(s => s.SetProperty(k => k.RevokedAt, DateTimeOffset.UtcNow));
        
        return rowsAffected > 0;
    }

    private static ApiKeyDto MapToDto(ApiKey entity) => new()
    {
        ApiKeyId = entity.ApiKeyId,
        Name = entity.Name,
        Scopes = entity.Scopes,
        CreatedAt = entity.CreatedAt,
        ExpiresAt = entity.ExpiresAt,
        RevokedAt = entity.RevokedAt,
        CreatedBy = entity.CreatedBy,
    };
}