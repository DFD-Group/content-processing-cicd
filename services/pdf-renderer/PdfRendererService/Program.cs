var builder = WebApplication.CreateBuilder(args);

builder.WebHost.UseUrls("http://0.0.0.0:9081");

var app = builder.Build();

app.MapGet("/health", () => Results.Json(new { status = "UP" }));

app.Run();