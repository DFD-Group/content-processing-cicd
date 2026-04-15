using OneOf;
using ContentProcessing.Persistence;
using Microsoft.EntityFrameworkCore;
using ContentProcessing.Persistence.Entities.App;
using AuthService.Models;
using AuthService.Services;

var builder = WebApplication.CreateBuilder(args);

var connectionString = builder.Configuration.GetConnectionString("ContentProcessing")
    ?? Environment.GetEnvironmentVariable("CONTENT_PROCESSING_CONNECTION_STRING");

builder.Services.AddDbContext<ContentProcessingDbContext>(options =>
    options.UseNpgsql(connectionString,
                      o => o.MapEnum<PdfToImagesStatus>("pdf_to_images_status", schemaName: "app"))
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