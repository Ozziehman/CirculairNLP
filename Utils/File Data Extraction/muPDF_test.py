import fitz
import os

print(fitz.__doc__)
current_dir = os.path.dirname(__file__)
os.chdir(current_dir)

def read_text_from_pdf(file_path):
    try:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading text from PDF: {e}")
        return None

def extract_images_from_pdf(file_path, output_folder):
    try:
        with fitz.open(file_path) as doc:
            for page_num, page in enumerate(doc):
                image_list = page.get_images(full=True)
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    image_filename = os.path.join(output_folder, "images", f"page_{page_num}_image_{img_index}.{image_ext}")
                    with open(image_filename, "wb") as image_file:
                        image_file.write(image_bytes)
    except Exception as e:
        print(f"Error extracting images from PDF: {e}")

def process_pdf(file_path):
    text = read_text_from_pdf(file_path)
    if text:
        output_folder = os.path.join("Output Files", os.path.splitext(os.path.basename(file_path))[0])
        os.makedirs(output_folder, exist_ok=True)
        with open(os.path.join(output_folder, "text.txt"), "w", encoding='utf-8') as text_file:
            text_file.write(text)
        os.makedirs(os.path.join(output_folder, "images"), exist_ok=True)
        extract_images_from_pdf(file_path, output_folder)
        print(f"PDF processed successfully. Text and images saved in '{output_folder}'.")


print(os.getcwd())
input_folder = "Input Files"
pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
for pdf_file in pdf_files:
    pdf_file_path = os.path.join(input_folder, pdf_file)
    process_pdf(pdf_file_path)
