using ContentProcessing.Persistence;
using Microsoft.EntityFrameworkCore;
using AuthService.Models;
using AuthService.Services;

var builder = WebApplication.CreateBuilder(args);

var connectionString = builder.Configuration.GetConnectionString("ContentProcessing")
    ?? Environment.GetEnvironmentVariable("CONTENT_PROCESSING_CONNECTION_STRING");

builder.Services.AddDbContext<ContentProcessingDbContext>(options =>
    options.UseNpgsql(connectionString)
    .UseSnakeCaseNamingConvention());

builder.Services.AddScoped<IApiKeyService, ApiKeyService>();

builder.Host.UseWindowsService();

var app = builder.Build();

app.MapGet("/health", () => Results.Json(new { status = "UP" }));

app.MapPost("/api-keys", async (CreateApiKeyRequest request, IApiKeyService service) =>
{
    var result = await service.CreateAsync(request);
    
    return result.Match(
        response => Results.Created($"/api-keys/{response.ApiKeyId}", response),
        error => Results.BadRequest(new { error = error.Message })
    );
});

app.MapPost("/api-keys/verify", async (VerifyApiKeyRequest request, IApiKeyService service) =>
{
    var result = await service.VerifyAsync(request.RawKey);
    return result is null
        ? Results.Unauthorized()
        : Results.Ok(result);
});

app.MapGet("/api-keys", async (IApiKeyService service) =>
{
    var keys = await service.ListAsync();
    return Results.Ok(keys);
});

app.MapGet("/api-keys/{id:guid}", async (Guid id, IApiKeyService service) =>
{
    var key = await service.GetByIdAsync(id);
    return key is null ? Results.NotFound() : Results.Ok(key);
});

app.MapDelete("/api-keys/{id:guid}", async (Guid id, IApiKeyService service) =>
{
    var revoked = await service.RevokeAsync(id);
    return revoked ? Results.NoContent() : Results.NotFound();
});


app.Run();