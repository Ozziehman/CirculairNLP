import os
from collections import Counter
from PyPDF2 import PdfReader
import re

# Configs
word_length = 6
print_amount = 50
dir = os.path.dirname(__file__)

# Om te zorgen dat Nederland aan het begin van een zin en nederland in het midden van een zin als 1 woord tellen
def clean_text(text):
    cleaned_text = re.sub(r'\W+', ' ', text.lower())
    return cleaned_text

word_counter = Counter()

for filename in os.listdir(dir):
    if filename.endswith('.pdf'):
        file_path = os.path.join(dir, filename)
        reader = PdfReader(file_path)
        
        for page in reader.pages:
            text = page.extract_text()
            cleaned_text = clean_text(text)
            word_counter.update(word for word in cleaned_text.split() if len(word) >= word_length)

print(word_counter.most_common(print_amount))

