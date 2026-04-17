using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;
using ContentProcessing.Persistence.Entities.App;

namespace ContentProcessing.Persistence;

public class DesignTimeDbContextFactory : IDesignTimeDbContextFactory<ContentProcessingDbContext>
{
    public ContentProcessingDbContext CreateDbContext(string[] args)
    {
        var connectionString = Environment.GetEnvironmentVariable("CONTENT_PROCESSING_CONNECTION_STRING")
            ?? "Host=localhost;Database=dummy";

        var optionsBuilder = new DbContextOptionsBuilder<ContentProcessingDbContext>();
        optionsBuilder
            .UseNpgsql(connectionString)
            .UseSnakeCaseNamingConvention();
            
        return new ContentProcessingDbContext(optionsBuilder.Options);
    }
}