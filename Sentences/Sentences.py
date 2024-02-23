import os
from PyPDF2 import PdfReader

# Configs
dir = os.path.dirname(__file__)

for filename in os.listdir(dir):
    if filename.endswith('.pdf'):
        file_path = os.path.join(dir, filename)
        output_file = os.path.splitext(file_path)[0] + '_sentences.txt'  # Create output file name
        
        with open(output_file, 'w', encoding='utf-8') as f_out:
            reader = PdfReader(file_path)
            
            for page in reader.pages:
                text = page.extract_text()
                sentences = text.split('.')  # Split text into sentences
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence:  # Check if sentence is not empty
                        f_out.write(sentence + '\n')  # Write sentence to file
