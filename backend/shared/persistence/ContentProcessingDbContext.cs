namespace ContentProcessing.Persistence;

using ContentProcessing.Persistence.Entities.App;
using ContentProcessing.Persistence.Entities.Auth;
using Microsoft.EntityFrameworkCore;
using System.Reflection;
using EFCore.NamingConventions;

public class ContentProcessingDbContext : DbContext
{
    public ContentProcessingDbContext(DbContextOptions<ContentProcessingDbContext> options) : base(options)
    {
    }

    public DbSet<ApiKey> ApiKeys => Set<ApiKey>();
    public DbSet<PdfToImages> PdfToImages => Set<PdfToImages>();
    public DbSet<Image> Images => Set<Image>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.HasPostgresEnum<PdfToImagesStatus>(schema: "app", name: "pdf_to_images_status");
        modelBuilder.ApplyConfigurationsFromAssembly(Assembly.GetExecutingAssembly());
    }

}