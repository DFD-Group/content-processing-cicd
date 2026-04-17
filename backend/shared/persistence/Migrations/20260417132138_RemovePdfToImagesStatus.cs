using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ContentProcessing.Persistence.Migrations
{
    /// <inheritdoc />
    public partial class RemovePdfToImagesStatus : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "status",
                schema: "app",
                table: "pdf_to_images");

            migrationBuilder.Sql("DROP TYPE app.pdf_to_images_status;");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(
                "CREATE TYPE app.pdf_to_images_status AS ENUM ('pending', 'processing', 'completed', 'failed');");

            migrationBuilder.AddColumn<string>(
                name: "status",
                schema: "app",
                table: "pdf_to_images",
                type: "app.pdf_to_images_status",
                nullable: false,
                defaultValue: "pending");
        }
    }
}
