-- Matches EF migration 20260417132138_RemovePdfToImagesStatus Up()
ALTER TABLE app.pdf_to_images
    DROP COLUMN status;

DROP TYPE app.pdf_to_images_status;
