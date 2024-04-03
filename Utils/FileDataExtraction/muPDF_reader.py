import os
import fitz
print(fitz.__doc__)

import json
from collections import defaultdict
import re

import nltk
from nltk.corpus import words
from nltk.stem import WordNetLemmatizer

# Download the words corpus if not already downloaded
nltk.download('words')
nltk.download('wordnet')
nltk.download('punkt')

# Set of English words
english_words = set(words.words())

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

    def extract_full_text_structure(self, file):
        try:
            full_dict = {}
            for page_num, page in enumerate(file):
                full_dict[f"page_{page_num}"] = page.get_textpage().extractDICT(sort=True)
            return full_dict
        except Exception as e:
            print(f"Error reading text from PDF: {e}")
            return None   
        
    def contains_english_word(self, input_string):
        wnl = WordNetLemmatizer()
        words_in_string = nltk.word_tokenize(input_string.lower())
        words_in_string = [word for s in words_in_string for word in s.split("-")]
        for word in words_in_string:
            if word:
                stemmed_word = wnl.lemmatize(word)
                if stemmed_word in english_words and len(stemmed_word) > 2:
                    return True
        return False
        
    def generate_paragraphs_per_page(self, file, garbage_filter: bool = True):
        # try:
            text_structure = {}
            for page_num, page in enumerate(file):
                    text_structure[f"page_{page_num}"] = {}
                    current = text_structure[f"page_{page_num}"]
                    all_fonts = {}
                    page_info = page.get_textpage().extractDICT(sort=False)
                    for block in page_info['blocks']:
                        for line in block['lines']:
                            for span in line['spans']:
                                if self.contains_english_word(span['text']) and garbage_filter:
                                    key = (span['font'], span['size'])
                                    all_fonts[key] = all_fonts.get(key, 0) + len(span['text'])

                    font_name_directory = defaultdict(str)

                    if all_fonts:
                        paragraph_font = max(all_fonts, key=all_fonts.get)
                        font_name_directory[paragraph_font] = 'paragraph'
                        all_fonts = [font for font in all_fonts if font != paragraph_font]
                        if all_fonts:
                            # Find the font with the highest size value for 'title'
                            title_font = max(all_fonts, key=lambda x: x[1])
                            font_name_directory[title_font] = 'title'
                            all_fonts = [font for font in all_fonts if font != title_font]
                            all_fonts.sort(key=lambda x: x[1], reverse=True)

                            subtitle_counter = 1
                            subtext_counter = 1
                            for font in all_fonts:
                                if font[1] > paragraph_font[1]:  # Larger than paragraph
                                    font_name_directory[font] = f'subtitle{subtitle_counter}'
                                    subtitle_counter += 1
                                else:  # Smaller than paragraph
                                    font_name_directory[font] = f'subtext{subtext_counter}'
                                    subtext_counter += 1
                        font_name_directory = dict(font_name_directory)

                    font_occurrence = {}
                    prev_font_size = None

                    for block in page_info['blocks']:
                        block_num = block['number']
                        for line in block['lines']:
                            for span in line['spans']:
                                if self.contains_english_word(span['text']) and garbage_filter:
                                    font_key = (span['font'], span['size'])
                                    if prev_font_size == font_key[1]:
                                        current[text_key]['text'] += span['text']
                                        if block_num not in current[text_key]['blocks']:
                                            current[text_key]['blocks'].append(block_num) 
                                    else:
                                        font_occurrence[font_key] = font_occurrence.get(font_key, 0) + 1
                                        text_key = (str(font_name_directory[font_key]) + '_' + str(font_occurrence[font_key]))

                                        current[text_key] = {'text': span['text'], 'blocks': [block_num], 'page_num': page_num}
                                        prev_font_size = font_key[1]
            return text_structure            
        # except Exception as e:
        #     print(f"Error reading text from PDF: {e}")
        #     return None
        
    def generate_paragraphs_per_file(self, file, garbage_filter: bool = True):
        # try:
            text_structure = {}
            all_fonts = {}
            font_occurrence = {}
            prev_font_size = None
            for page_num, page in enumerate(file):
                    page_info = page.get_textpage().extractDICT(sort=False)
                    for block in page_info['blocks']:
                        for line in block['lines']:
                            for span in line['spans']:
                                if self.contains_english_word(span['text']) and garbage_filter:
                                    key = (span['font'], span['size'])
                                    all_fonts[key] = all_fonts.get(key, 0) + len(span['text'])

            if all_fonts:
                font_name_directory = defaultdict(str)
                paragraph_font = max(all_fonts, key=all_fonts.get)
                font_name_directory[paragraph_font] = 'paragraph'
                all_fonts = [font for font in all_fonts if font != paragraph_font]

                if all_fonts:
                    # Find the font with the highest size value for 'title'
                    title_font = max(all_fonts, key=lambda x: x[1])
                    font_name_directory[title_font] = 'title'

                    all_fonts = [font for font in all_fonts if font != title_font]
                    all_fonts.sort(key=lambda x: x[1], reverse=True)

                    subtitle_counter = 1
                    subtext_counter = 1
                    for font in all_fonts:
                        if font[1] > paragraph_font[1]:  # Larger than paragraph
                            font_name_directory[font] = f'subtitle{subtitle_counter}'
                            subtitle_counter += 1
                        else:  # Smaller than paragraph
                            font_name_directory[font] = f'subtext{subtext_counter}'
                            subtext_counter += 1
                font_name_directory = dict(font_name_directory)


            for page_num, page in enumerate(file):
                page_info = page.get_textpage().extractDICT(sort=False)
                for block in page_info['blocks']:
                    block_num = block['number']
                    for line in block['lines']:
                        for span in line['spans']:
                            if self.contains_english_word(span['text']) and garbage_filter:
                                font_key = (span['font'], span['size'])
                                if prev_font_size == font_key[1]:
                                    text_structure[text_key]['text'] += span['text']
                                    if block_num not in text_structure[text_key]['blocks']:
                                        text_structure[text_key]['blocks'].append(block_num)
                                    if page_num not in text_structure[text_key]['page_nums']:
                                        text_structure[text_key]['page_nums'].append(page_num)  
                                else:
                                    font_occurrence[font_key] = font_occurrence.get(font_key, 0) + 1
                                    text_key = (str(font_name_directory[font_key]) + '_' + str(font_occurrence[font_key]))

                                    text_structure[text_key] = {'text': span['text'], 'blocks': [block_num], 'page_nums': [page_num]}
                                    prev_font_size = font_key[1]
            return text_structure            
        # except Exception as e:
        #     print(f"Error reading text from PDF: {e}")
        #     return None
        
    def add_to_nested_dict(self, nested_dict, path, new_thing):
        current = nested_dict
        for key in path[:-1]:
            current = current.setdefault(key, {})
        current[path[-1]] = new_thing

    def structure_paragraphs_per_file(self, text_structure):
        final_structured_text = {}
        current_path = []
        text_type_to_int = {
            'title': 1,
            'subtitle': 2,
            'paragraph': 3,
            'subtext': 4
        }

        for segment_key, segment_value in text_structure.items():
            matches = re.match(r'([a-zA-Z]+)([0-9]+)_([0-9]+)', segment_key)
            if matches:
                segment_type = matches.group(1)
                hierarchical_number = int(matches.group(2))
            else:
                segment_type = re.match(r'([a-zA-Z]+)', segment_key).group(1)
                hierarchical_number = 0
            
            while True:
                if current_path == []:
                    current_path.append(segment_key)
                    break
                else:
                    last = current_path[-1]
                    last_matches = re.match(r'([a-zA-Z]+)([0-9]+)_([0-9]+)', last)
                    if last_matches:
                        last_segment_type = last_matches.group(1)
                        last_hierarchical_number = int(last_matches.group(2))
                    else:
                        last_segment_type = re.match(r'([a-zA-Z]+)', last).group(1)
                        last_hierarchical_number = 0
                    if text_type_to_int[last_segment_type] < text_type_to_int[segment_type]:
                        current_path.append(segment_key)
                        break
                    elif last_segment_type == segment_type and last_hierarchical_number < hierarchical_number:
                        current_path.append(segment_key)
                        break
                    else:
                        del current_path[-1]

            self.add_to_nested_dict(final_structured_text, current_path, segment_value)

        return final_structured_text


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
            
            file_dict = self.extract_full_text_structure(self.file)
            if file_dict:
                with open(os.path.join(output_folder, "file_structured.json"), "w") as structured_file:
                    json.dump(file_dict, structured_file, indent=4)

            structure_dict_for_page = self.generate_paragraphs_per_page(file)
            if structure_dict_for_page:
                with open(os.path.join(output_folder, "page_layout_structured_per_page.json"), "w") as structured_file:
                    json.dump(structure_dict_for_page, structured_file, indent=4)

            structure_dict_for_file = self.generate_paragraphs_per_file(file)

            if structure_dict_for_file:
                with open(os.path.join(output_folder, "page_layout_structured_per_file.json"), "w") as structured_file:
                    json.dump(structure_dict_for_file, structured_file, indent=4)

            hierarchical_structure_for_file = self.structure_paragraphs_per_file(structure_dict_for_file)
            if structure_dict_for_file:
                with open(os.path.join(output_folder, "hierarchical_structure_for_file.json"), "w") as structured_file:
                    json.dump(hierarchical_structure_for_file, structured_file, indent=4)

            print(f"PDF processed successfully. Output saved in '{output_folder}'.")

    def main(self):
        self.process_pdf(self.file, self.filepath)
