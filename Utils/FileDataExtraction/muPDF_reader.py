import os
current_dir = os.path.dirname(__file__)
os.chdir(current_dir)

import fitz
print(fitz.__doc__)

import json
import numpy as np
import matplotlib.pyplot as plt

class muPDF_reader:
    def __init__(self, file_path) -> None:
        self.filepath = file_path
        self.file = fitz.open(file_path)

    def get_table_of_contents(self, file):
        return file.get_toc(False)

    def get_tables(self, file):
        if not hasattr(fitz.Page, "find_tables"):
            raise RuntimeError("This PyMuPDF version does not support the table feature")
        page = file[0]
        tabs = page.find_tables()
        
        for i, tab in enumerate(tabs):
            print(f"Table {i}")
            print(tab.to_pandas().to_markdown())

        return tabs

    def read_text_from_pdf(self, file):
        try:
            text = ""
            for page in file:
                text += page.get_text()
            return text
        except Exception as e:
            print(f"Error reading text from PDF: {e}")
            return None

    def extract_images_from_pdf(self, file, output_folder):
        try:
            for page_num, page in enumerate(file):
                image_list = page.get_images(full=True)
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = file.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    image_filename = os.path.join(output_folder, "images", f"page_{page_num}_image_{img_index}.{image_ext}")
                    with open(image_filename, "wb") as image_file:
                        image_file.write(image_bytes)
        except Exception as e:
            print(f"Error extracting images from PDF: {e}")

    def process_pdf(self, file, filepath):
        text = self.read_text_from_pdf(file)
        if text:
            output_folder = os.path.join("OutputFiles", os.path.splitext(os.path.basename(filepath))[0])
            os.makedirs(output_folder, exist_ok=True)
            with open(os.path.join(output_folder, "text.txt"), "w", encoding='utf-8') as text_file:
                text_file.write(text)
            os.makedirs(os.path.join(output_folder, "images"), exist_ok=True)
            self.extract_images_from_pdf(file, output_folder)

            toc = self.get_table_of_contents(self.file)

            if toc != []:
                with open(os.path.join(output_folder, "table_of_contents.json"), "w") as toc_file:
                    json.dump(toc, toc_file, indent=4)

            self.get_tables(file)

            tabs = self.get_tables(file)
            for i, tab in enumerate(tabs):
                table_markdown = tab.to_pandas().to_markdown()
                table_filename = f"table_{i}.md"
                with open(os.path.join(output_folder, table_filename), "w", encoding="utf-8") as table_file:
                    table_file.write(table_markdown)
                toc.append({"filename": table_filename, "title": f"Table {i}"})

            print(f"PDF processed successfully. Text and images saved in '{output_folder}'.")

    def main(self):
        self.process_pdf(self.file, self.filepath)
        