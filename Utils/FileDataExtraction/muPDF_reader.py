import os
import fitz
print(fitz.__doc__)

import json

class muPDF_reader:
    def __init__(self, file_path) -> None:
        self.filepath = file_path
        self.file = fitz.open(file_path)

    def get_table_of_contents(self, file):
        return file.get_toc(False)

    def get_tables(self, file):
        output = [] # List of table, table number and page number triplets
        
        for page_num, page in enumerate(file):
            tabs = page.find_tables()
            for i, tab in enumerate(tabs):
                output.append((tab.to_pandas(), i, page_num))
        return output

    def read_text_from_pdf(self, file):
        try:
            text = ""
            for page in file:
                text += page.get_text()
            return text
        except Exception as e:
            print(f"Error reading text from PDF: {e}")
            return None
        
    def extract_textblocks_from_pdf(self, file):
        try:
            text_blocks = []
            for page_num, page in enumerate(file):
                for block in page.get_textpage().extractBLOCKS():
                    coords = (block[0], block[1], block[2], block[3])
                    lines = str(block[4])
                    block_no = block[5]
                    block_type = block[6]
                    text_block = {
                        "coords": coords,
                        "lines": lines,
                        "block_no": block_no,
                        "block_type": block_type,
                        "page_num": page_num
                    }
                    text_blocks.append(text_block)
            return text_blocks
        except Exception as e:
            print(f"Error reading text from PDF: {e}")
            return None

    def get_metadata(self, file):
        #print(file.metadata)
        return file.metadata

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

            blocks = self.extract_textblocks_from_pdf(file)
            with open(os.path.join(output_folder, 'extracted_text_blocks.json'), 'w') as blocks_file:
                json.dump(blocks, blocks_file, indent=4)

            metadata = self.get_metadata(file)
            with open(os.path.join(output_folder, 'metadata.json'), 'w') as blocks_file:
                json.dump(metadata, blocks_file, indent=4)

            self.extract_images_from_pdf(file, output_folder)

            toc = self.get_table_of_contents(self.file)

            if toc != []:
                with open(os.path.join(output_folder, "table_of_contents.json"), "w") as toc_file:
                    json.dump(toc, toc_file, indent=4)

            tabs = self.get_tables(file)

            if tabs != []:
                tables_folder = os.path.join(output_folder, 'tables')
                if not os.path.exists(tables_folder):
                    os.makedirs(tables_folder)
                for tab in tabs:
                    table_data = tab[0]
                    table_filename = f"page_{tab[2]+1}_table_{tab[1]+1}.md"
                    with open(os.path.join(tables_folder, table_filename), "w", encoding="utf-8") as table_file:
                        table_file.write(table_data.to_markdown())

            print(f"PDF processed successfully. Output saved in '{output_folder}'.")

    def main(self):
        self.process_pdf(self.file, self.filepath)
