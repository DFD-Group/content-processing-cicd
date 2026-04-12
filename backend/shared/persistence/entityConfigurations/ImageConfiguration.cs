namespace ContentProcessing.Persistence.EntityConfigurations;

using ContentProcessing.Persistence.Entities.App;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

public class ImageConfiguration : IEntityTypeConfiguration<Image>
{
    public void Configure(EntityTypeBuilder<Image> builder)
    {
        builder.ToTable("images", schema: "app");

        builder.Property(e => e.Id)
        .HasDefaultValueSql("gen_random_uuid()");

        builder.Property(e => e.ImagePath)
        .IsRequired();

        builder.Property(e => e.ImageSha256)
        .HasMaxLength(64)
        .IsFixedLength()
        .IsRequired();

        builder.ToTable(t => t.HasCheckConstraint("CK_images_image_sha256",
            "octet_length(trim(image_sha256::text)) = 64 AND trim(image_sha256::text) ~ '^[0-9a-fA-F]{64}$'"));
        
        builder.Property(e => e.PageNumber)
        .IsRequired();

        builder.HasIndex(e => e.PdfToImagesId)
            .HasDatabaseName("idx_images_pdf_to_images_id");

        builder.ToTable(t => t.HasCheckConstraint("CK_images_page_number", "page_number >= 0"));

        builder.Property(e => e.CreatedAt)
        .HasDefaultValueSql("now()");

    }
}