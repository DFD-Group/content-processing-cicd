using ContentProcessing.Persistence;
using Microsoft.EntityFrameworkCore;
using ContentProcessing.Persistence.Entities.App;

var builder = WebApplication.CreateBuilder(args);

var connectionString = builder.Configuration.GetConnectionString("ContentProcessing")
    ?? Environment.GetEnvironmentVariable("CONTENT_PROCESSING_CONNECTION_STRING");

builder.Services.AddDbContext<ContentProcessingDbContext>(options =>
    options.UseNpgsql(connectionString,
                      o => o.MapEnum<PdfToImagesStatus>("pdf_to_images_status", schemaName: "app"))
    .UseSnakeCaseNamingConvention());

builder.Host.UseWindowsService();

var app = builder.Build();

app.MapGet("/health", () => Results.Json(new { status = "UP" }));

app.Run();