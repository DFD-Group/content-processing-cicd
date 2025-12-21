var builder = WebApplication.CreateBuilder(args);

builder.WebHost.UseUrls("http://0.0.0.0:9080");

var app = builder.Build();

app.MapGet("/health", () => Results.Json(new { status = "UP" }));

app.Run();
