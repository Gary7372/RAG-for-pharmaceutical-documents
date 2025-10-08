🛠 How to Use
🔹 STEP 1: Render image-containing pages from PDFs
Run:


python image_page_to_pdf.py


This will:

Look in Data/ for PDFs

Dont forget to paste Data folder here

Render only pages that contain embedded images

Save each rendered image in rendered_pages_with_images/

Group images into PDFs (25 pages per file) into image_pdfs/

🔹 STEP 2: Extract tables using Adobe PDF Services
Once the image_pdfs/ are created:


python extract_tables.py

This will:

Read all PDFs in image_pdfs/

Submit each to Adobe API for table extraction
credentials = ServicePrincipalCredentials(
                client_id='client_id',
                client_secret='client_secret'
            )

Save outputs in output/ExtractTablesOnly/ as .zip and structuredData.json

Log pages with no detected tables in output/missed_tables_log.txt



🔹 STEP 3: Convert extracted Excel tables to clean CSVs
Once Adobe outputs are available inside the results/ folder:


python convert_excel_to_csv.py
This will:

Traverse all subfolders in results/

Read .xlsx files, clean headers and values

Save clean CSVs as csv1.csv, csv2.csv, ... in csv_files/