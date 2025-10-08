import os
import fitz  # PyMuPDF
from PIL import Image

def render_pages_with_images(pdf_folder, images_output_folder, dpi=150):
    if not os.path.exists(images_output_folder):
        os.makedirs(images_output_folder)

    image_paths = []
    img_counter = 0

    for pdf_file in os.listdir(pdf_folder):
        if not pdf_file.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(pdf_folder, pdf_file)
        doc = fitz.open(pdf_path)
        print(f"📄 Scanning {pdf_file} for pages with images...")

        for page_num, page in enumerate(doc):
            images = page.get_images(full=True)
            if not images:
                continue  # Skip pages without images

            # Render full page to image
            pix = page.get_pixmap(dpi=dpi)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            img_filename = f"{os.path.splitext(pdf_file)[0]}_page_{page_num + 1}.jpg"
            img_path = os.path.join(images_output_folder, img_filename)
            img.save(img_path)
            image_paths.append(img_path)
            img_counter += 1

    print(f"✅ Rendered {img_counter} pages that contained images.")
    return image_paths

def create_image_pdfs(image_paths, output_folder, images_per_pdf=25):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    chunks = [image_paths[i:i + images_per_pdf] for i in range(0, len(image_paths), images_per_pdf)]

    for i, chunk in enumerate(chunks):
        images = [Image.open(img).convert("RGB") for img in chunk]
        pdf_path = os.path.join(output_folder, f"images_batch_{i+1}.pdf")
        images[0].save(pdf_path, save_all=True, append_images=images[1:])
        print(f"📝 Created PDF: {pdf_path} with {len(images)} images")

    print(f"✅ Created {len(chunks)} PDF files.")

# === USAGE ===
pdf_input_folder = "Data"                   # Folder containing PDFs
images_temp_folder = "rendered_pages_with_images"  # Folder to store rendered page images
output_pdf_folder = "image_pdfs"            # Final PDFs

# Step 1: Render only pages with images
page_images = render_pages_with_images(pdf_input_folder, images_temp_folder, dpi=150)

# Step 2: Group into 25-image PDFs
create_image_pdfs(page_images, output_pdf_folder, images_per_pdf=25)
