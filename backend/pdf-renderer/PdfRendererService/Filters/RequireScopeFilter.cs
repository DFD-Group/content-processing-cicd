namespace PdfRendererService.Filters;

using System.Text.Json;
public static class RequireScopeFilter
{
    public static async ValueTask<object?> RequireScope(
        EndpointFilterInvocationContext context,
        EndpointFilterDelegate next,
        string requiredScope)
    {
        if (context.HttpContext.Items["ApiKey"] is JsonElement keyData
            && keyData.TryGetProperty("scopes", out var scopes)
            && scopes.EnumerateArray().Any(s => s.GetString() == requiredScope))
        {
            return await next(context);
        }

        return Results.Json(new { error = $"Missing required scope: {requiredScope}" },
                            statusCode: 403);
    }
}