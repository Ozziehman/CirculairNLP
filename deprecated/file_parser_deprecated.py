import os
current_dir = os.path.dirname(__file__)
os.chdir(current_dir)

from PyPDF2 import PdfReader

class file_parser:
    def read_text_from_pdf(self, file_path):
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
            return text
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None

    def extract_images_from_pdf(self, file_path, output_folder):
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                count = 1
                for page_number, page in enumerate(reader.pages):
                    try:
                        for image_file_object in page.images:
                            with open(os.path.join(output_folder, "images", f"{count}_{page_number+1}.png"), "wb") as fp:
                                fp.write(image_file_object.data)
                                count += 1
                    except Exception as e:
                        print(f"Error processing image: {e} at page {page_number}")
                        continue
        except FileNotFoundError:
            print(f"File not found: {file_path}")

    def process_pdf(self, file_path):
        text = self.read_text_from_pdf(file_path)
        if text:
            output_folder = os.path.join("OutputFiles", os.path.splitext(os.path.basename(file_path))[0])
            os.makedirs(output_folder, exist_ok=True)
            with open(os.path.join(output_folder, "text.txt"), "w", encoding='utf-8') as text_file:
                text_file.write(text)
            os.makedirs(os.path.join(output_folder, "images"), exist_ok=True)
            self.extract_images_from_pdf(file_path, output_folder)
            print(f"PDF processed successfully. Text and images saved in '{output_folder}'.")

    def main(self):
        input_folder = "InputFiles"
        pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
        for pdf_file in pdf_files:
            pdf_file_path = os.path.join(input_folder, pdf_file)
            self.process_pdf(pdf_file_path)

file_parser().main()