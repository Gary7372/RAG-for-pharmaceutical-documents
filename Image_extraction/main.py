import os
import json
import csv
import zipfile
import logging
from datetime import datetime
from multiprocessing import Pool, cpu_count,  current_process
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult

logging.basicConfig(level=logging.INFO)


class ExtractTablesOnly:
    def __init__(self, input_pdf_path, csv_output_dir):
        self.missed_pages_log = "output/missed_tables_log.txt"

        try:
            logging.info(f"Processing PDF file: {input_pdf_path}")
            with open(input_pdf_path, 'rb') as file:
                input_stream = file.read()

            credentials = ServicePrincipalCredentials(
                client_id='client_id',
                client_secret='client_secret'
            )

            pdf_services = PDFServices(credentials=credentials)

            input_asset = pdf_services.upload(
                input_stream=input_stream,
                mime_type=PDFServicesMediaType.PDF
            )

            extract_params = ExtractPDFParams(
                elements_to_extract=[ExtractElementType.TABLES]
            )
            extract_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_params)

            location = pdf_services.submit(extract_job)
            result: ExtractPDFResult = pdf_services.get_job_result(location, ExtractPDFResult)

            result_asset: CloudAsset = result.get_result().get_resource()
            stream_asset: StreamAsset = pdf_services.get_content(result_asset)

            base_output_dir = "output/ExtractTablesOnly"
            output_dir = self.get_timestamped_dir(base_output_dir)
            os.makedirs(output_dir, exist_ok=True)
            os.makedirs(csv_output_dir, exist_ok=True)

            zip_path = os.path.join(output_dir, "result.zip")
            with open(zip_path, "wb") as f:
                f.write(stream_asset.get_input_stream())
            logging.info(f"✅ ZIP saved: {zip_path}")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)

            json_path = os.path.join(output_dir, 'structuredData.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]

            table_elements = [el for el in data.get('elements', []) if "Table" in el.get('Path', '')]
            pages_with_tables = set()
            table_count = 0

            for el in table_elements:
                page_number = el.get('Page', None)
                if page_number is not None:
                    pages_with_tables.add(page_number)

                rows = el.get('Rows', [])


                table_count += 1

            if table_count == 0:
                logging.warning("⚠️ No tables found.")

            total_pages = max([el.get('Page', 0) for el in data.get('elements', [])])
            missed_pages = [str(p) for p in range(1, total_pages + 1) if p not in pages_with_tables]

            if missed_pages:
                os.makedirs(os.path.dirname(self.missed_pages_log), exist_ok=True)
                with open(self.missed_pages_log, 'a', encoding='utf-8') as log_file:
                    log_file.write(f"{base_name}.pdf - Missed Table Pages: {', '.join(missed_pages)}\n")
                logging.warning(f"⚠️ Table not found on pages: {', '.join(missed_pages)} in {base_name}.pdf")

        except (ServiceApiException, ServiceUsageException, SdkException) as e:
            logging.exception(f"Adobe PDF Services error: {e}")
        except Exception as e:
            logging.exception(f"Unexpected error: {e}")

    def get_timestamped_dir(self, base_dir):
        time_stamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        return os.path.join(base_dir, f"run_{time_stamp}")

def extract_worker(pdf_path_and_output):
    pdf_path, csv_output_dir = pdf_path_and_output
    process_name = current_process().name

    try:
        logging.info(f"[{process_name}] Starting extraction for {pdf_path}")
        ExtractTablesOnly(pdf_path, csv_output_dir)
        logging.info(f"[{process_name}] ✅ Finished extraction for {pdf_path}")
    except Exception as e:
        logging.exception(f"[{process_name}] ❌ Error processing {pdf_path}: {e}")

def process_all_pdfs_in_folder(folder_path):
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    if not pdf_files:
        logging.warning(f"No PDF files found in {folder_path}")
        return

    csv_output_dir = "output/all_tables"
    os.makedirs(csv_output_dir, exist_ok=True)

    pdf_paths = [(os.path.join(folder_path, f), csv_output_dir) for f in pdf_files]

    num_processes = max(1, min(4, cpu_count() // 2))  # Limit to 4 or half the CPUs
    logging.info(f"🧠 Starting multiprocessing with {num_processes} worker(s)...")

    with Pool(processes=num_processes) as pool:
        pool.map(extract_worker, pdf_paths)

    logging.info("✅ All PDF files have been processed.")


if __name__ == '__main__':
    input_folder = 'image_pdfs'  # Folder containing PDFs
    process_all_pdfs_in_folder(input_folder)

#157
#211