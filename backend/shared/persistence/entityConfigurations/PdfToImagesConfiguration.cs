namespace ContentProcessing.Persistence.EntityConfigurations;

using ContentProcessing.Persistence.Entities.App;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

public class PdfToImagesConfiguration : IEntityTypeConfiguration<PdfToImages>
{
    public void Configure(EntityTypeBuilder<PdfToImages> builder)
    {
        builder.ToTable("pdf_to_images", schema: "app");

        builder.Property(e => e.Id)
            .HasDefaultValueSql("gen_random_uuid()");

        builder.Property(e => e.PdfPath)
            .IsRequired();

        builder.Property(e => e.PdfSha256)
            .HasMaxLength(64)
            .IsFixedLength()
            .IsRequired();

        builder.ToTable(t => t.HasCheckConstraint("CK_pdf_to_images_pdf_sha256",
            "octet_length(trim(pdf_sha256::text)) = 64 AND trim(pdf_sha256::text) ~ '^[0-9a-fA-F]{64}$'"));

        builder.Property(e => e.Status)
            .HasDefaultValue(PdfToImagesStatus.Pending);

        builder.Property(e => e.CreatedAt)
            .HasDefaultValueSql("now()");

        builder.Property(e => e.UpdatedAt)
            .HasDefaultValueSql("now()");

        builder.HasOne(e => e.FirstPageImage)
            .WithMany()
            .HasForeignKey(e => e.FirstPageImageId)
            .HasConstraintName("fk_pdf_to_images_first_page_image_id")
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasMany(e => e.Images)
            .WithOne(e => e.PdfToImages)
            .HasForeignKey(e => e.PdfToImagesId)
            .HasConstraintName("fk_images_pdf_to_images_id")
            .OnDelete(DeleteBehavior.Cascade);
    }
}