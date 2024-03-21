import os
from Utils.FileDataExtraction.muPDF_reader import muPDF_reader

class muPDF_reader_layer:
    def __init__(self):
        pass
    
    def ParseAllFiles(self, input_folder: str):
        pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
        for pdf_file in pdf_files:
            pdf_file_path = os.path.join(input_folder, pdf_file)
            print(f"Reading file: {pdf_file_path}")
            r = muPDF_reader(pdf_file_path)
            r.main()