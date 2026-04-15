namespace ContentProcessing.Persistence.EntityConfigurations;

using ContentProcessing.Persistence.Entities.Auth;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

public class ApiKeyConfiguration : IEntityTypeConfiguration<ApiKey>
{
    public void Configure(EntityTypeBuilder<ApiKey> builder)
    {
        builder.ToTable("api_keys", schema: "auth");

        builder.Property(e => e.ApiKeyId)
            .HasDefaultValueSql("gen_random_uuid()");

        builder.Property(e => e.SecretHash)
            .HasMaxLength(64)
            .IsFixedLength()
            .IsRequired();

        builder.ToTable(t => t.HasCheckConstraint("ck_api_keys_secret", "octet_length(trim(secret_hash::text)) = 64 AND trim(secret_hash::text) ~ '^[0-9a-fA-F]{64}$'"));

        builder.Property(e => e.CreatedAt)
            .HasDefaultValueSql("now()");
        
        builder.ToTable(t => t.HasCheckConstraint("ck_api_keys_scopes", "scopes IS NULL OR scopes <@ ARRAY['content:read', 'content:write', 'iam:admin']::text[]"));
    }
}