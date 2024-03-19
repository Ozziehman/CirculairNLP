import os
from muPDF_reader import muPDF_reader


input_folder = "InputFiles"
pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
for pdf_file in pdf_files:
    pdf_file_path = os.path.join(input_folder, pdf_file)
    r = muPDF_reader(pdf_file_path)
    r.main()