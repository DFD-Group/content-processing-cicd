using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ContentProcessing.Persistence.Migrations
{
    /// <inheritdoc />
    public partial class InitialCreate : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.EnsureSchema(
                name: "auth");

            migrationBuilder.EnsureSchema(
                name: "app");

            migrationBuilder.AlterDatabase()
                .Annotation("Npgsql:Enum:app.pdf_to_images_status", "pending,processing,completed,failed");

            migrationBuilder.CreateTable(
                name: "api_keys",
                schema: "auth",
                columns: table => new
                {
                    api_key_id = table.Column<Guid>(type: "uuid", nullable: false),
                    secret_hash = table.Column<string>(type: "character(64)", fixedLength: true, maxLength: 64, nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false, defaultValueSql: "now()"),
                    expires_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true),
                    revoked_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true),
                    scopes = table.Column<string[]>(type: "text[]", nullable: true),
                    name = table.Column<string>(type: "text", nullable: true),
                    created_by = table.Column<string>(type: "text", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("pk_api_keys", x => x.api_key_id);
                    table.CheckConstraint("ck_api_keys_scopes", "scopes IS NULL OR scopes <@ ARRAY['content:read', 'content:write', 'iam:admin']::text[]");
                    table.CheckConstraint("ck_api_keys_secret", "octet_length(trim(secret_hash::text)) = 64 AND trim(secret_hash::text) ~ '^[0-9a-fA-F]{64}$'");
                });

            migrationBuilder.CreateTable(
                name: "images",
                schema: "app",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false, defaultValueSql: "gen_random_uuid()"),
                    image_path = table.Column<string>(type: "text", nullable: false),
                    image_sha256 = table.Column<string>(type: "character(64)", fixedLength: true, maxLength: 64, nullable: false),
                    page_number = table.Column<int>(type: "integer", nullable: false),
                    pdf_to_images_id = table.Column<Guid>(type: "uuid", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false, defaultValueSql: "now()")
                },
                constraints: table =>
                {
                    table.PrimaryKey("pk_images", x => x.id);
                    table.CheckConstraint("CK_images_image_sha256", "octet_length(trim(image_sha256::text)) = 64 AND trim(image_sha256::text) ~ '^[0-9a-fA-F]{64}$'");
                    table.CheckConstraint("CK_images_page_number", "page_number >= 0");
                });

            migrationBuilder.CreateTable(
                name: "pdf_to_images",
                schema: "app",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false, defaultValueSql: "gen_random_uuid()"),
                    pdf_path = table.Column<string>(type: "text", nullable: false),
                    first_page_image_id = table.Column<Guid>(type: "uuid", nullable: true),
                    pdf_sha256 = table.Column<string>(type: "character(64)", fixedLength: true, maxLength: 64, nullable: false),
                    status = table.Column<string>(type: "app.pdf_to_images_status", nullable: false, defaultValue: "pending"),
                    error_message = table.Column<string>(type: "text", nullable: true),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false, defaultValueSql: "now()"),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false, defaultValueSql: "now()")
                },
                constraints: table =>
                {
                    table.PrimaryKey("pk_pdf_to_images", x => x.id);
                    table.CheckConstraint("CK_pdf_to_images_pdf_sha256", "octet_length(trim(pdf_sha256::text)) = 64 AND trim(pdf_sha256::text) ~ '^[0-9a-fA-F]{64}$'");
                    table.ForeignKey(
                        name: "fk_pdf_to_images_first_page_image_id",
                        column: x => x.first_page_image_id,
                        principalSchema: "app",
                        principalTable: "images",
                        principalColumn: "id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateIndex(
                name: "idx_images_pdf_to_images_id",
                schema: "app",
                table: "images",
                column: "pdf_to_images_id");

            migrationBuilder.CreateIndex(
                name: "ix_pdf_to_images_first_page_image_id",
                schema: "app",
                table: "pdf_to_images",
                column: "first_page_image_id");

            migrationBuilder.AddForeignKey(
                name: "fk_images_pdf_to_images_id",
                schema: "app",
                table: "images",
                column: "pdf_to_images_id",
                principalSchema: "app",
                principalTable: "pdf_to_images",
                principalColumn: "id",
                onDelete: ReferentialAction.Cascade);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "fk_images_pdf_to_images_id",
                schema: "app",
                table: "images");

            migrationBuilder.DropTable(
                name: "api_keys",
                schema: "auth");

            migrationBuilder.DropTable(
                name: "pdf_to_images",
                schema: "app");

            migrationBuilder.DropTable(
                name: "images",
                schema: "app");
        }
    }
}
