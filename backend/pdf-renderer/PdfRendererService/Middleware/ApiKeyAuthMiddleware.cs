namespace PdfRendererService.Middleware;

using System.Text.Json;

public class ApiKeyAuthMiddleware
{
    private readonly RequestDelegate _next;
    private readonly string _authServiceUrl;
    private readonly IHttpClientFactory _httpClient;
    private static readonly JsonSerializerOptions _jsonSerializerOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
    };

    public ApiKeyAuthMiddleware(RequestDelegate next, IConfiguration configuration, IHttpClientFactory httpClientFactory)
    {
        _next = next;
        _authServiceUrl = configuration["AuthService:BaseUrl"]
            ?? throw new InvalidOperationException("AuthService:BaseUrl is not configured");
        _httpClient = httpClientFactory;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        if (IsHealthEndpoint(context.Request.Path))
        {
            await _next(context);
            return;
        }

        var apiKey = ExtractApiKey(context.Request);
        if (apiKey is null)
        {
            context.Response.StatusCode = StatusCodes.Status401Unauthorized;
            await context.Response.WriteAsJsonAsync(new { error = "Missing API key" });
            return;

        }

        var httpClient = _httpClient.CreateClient("AuthService");
        var verifyResponse = await httpClient.PostAsJsonAsync(
            $"{_authServiceUrl}/api-keys/verify",
            new { rawKey = apiKey },
            _jsonSerializerOptions);

        if (!verifyResponse.IsSuccessStatusCode)
        {
            context.Response.StatusCode = StatusCodes.Status401Unauthorized;
            await context.Response.WriteAsJsonAsync(new { error = "Invalid API key" });
            return;
        }

        var keyMetadata = await verifyResponse.Content.ReadFromJsonAsync<JsonElement>();
        context.Items["ApiKeyMetadata"] = keyMetadata;
        await _next(context);
    }

    private static bool IsHealthEndpoint(PathString path) => path.Equals("/health", StringComparison.OrdinalIgnoreCase);

    private static string? ExtractApiKey(HttpRequest request)
    {
        if (request.Headers.TryGetValue("X-API-KEY", out var xApiKey))
            return xApiKey.ToString();

        if (request.Headers.TryGetValue("Authorization", out var authHeader))
        {
            var authHeaderValue = authHeader.ToString();
            if (authHeaderValue.StartsWith("Bearer ", StringComparison.OrdinalIgnoreCase))
            {
                return authHeaderValue["Bearer ".Length..].Trim();
            }
        }

        return null;
    }
}