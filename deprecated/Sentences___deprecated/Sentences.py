import os
from PyPDF2 import PdfReader
import spacy
import pdfminer.high_level

# Configs
dir = os.path.dirname(__file__)

nlp = spacy.load("en_core_web_sm")

def separate_into_paragraphs(text):
    doc = nlp(text)
    paragraphs = []
    current_paragraph = []
    
    for token in doc:
        if token.text.strip():
            current_paragraph.append(token.text)
        else:
            if current_paragraph:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
    
    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))
    
    return paragraphs

for filename in os.listdir(dir):
    if filename.endswith('.pdf'):
        file_path = os.path.join(dir, filename)
        output_file = os.path.splitext(file_path)[0] + '_sentences.txt'  # Create output file name
        
        with open(output_file, 'w', encoding='utf-8') as f_out:
            text = pdfminer.high_level.extract_text(file_path)
            paragraphs = separate_into_paragraphs(text)
            sentences = text.split('.')# Split text into sentences
                
            for paragraph in paragraphs:
                print(paragraph)
                print("---------------------------------")

            for sentence in sentences:
                sentence = sentence + "."
                sentence = sentence.strip()
                if sentence:  # Check if sentence is not empty
                    f_out.write(sentence + '\n')  # Write sentence to file
