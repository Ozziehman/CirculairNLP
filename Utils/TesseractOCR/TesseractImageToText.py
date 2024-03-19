import os
current_dir = os.path.dirname(__file__)
os.chdir(current_dir)

import pytesseract
import PIL.Image
import langdetect

class TesseractImageToText:
  def get_text_from_image(self, image_file_path, config):
      """
      --psm NUM             Specify page segmentation mode.
      --oem NUM             Specify OCR Engine mode.

      Page segmentation modes:
        0    Orientation and script detection (OSD) only.
        1    Automatic page segmentation with OSD.
        2    Automatic page segmentation, but no OSD, or OCR.
        3    Fully automatic page segmentation, but no OSD. (Default)
        4    Assume a single column of text of variable sizes.
        5    Assume a single uniform block of vertically aligned text.
        6    Assume a single uniform block of text.
        7    Treat the image as a single text line.
        8    Treat the image as a single word.
        9    Treat the image as a single word in a circle.
      10    Treat the image as a single character.
      11    Sparse text. Find as much text as possible in no particular order.
      12    Sparse text with OSD.
      13    Raw line. Treat the image as a single text line,
            bypassing hacks that are Tesseract-specific.
            
          OCR Engine modes: (see https://github.com/tesseract-ocr/tesseract/wiki#linux)
        0    Legacy engine only.
        1    Neural nets LSTM engine only.
        2    Legacy + LSTM engines.
        3    Default, based on what is available.
        
        example: config = r"--psm 6 --oem 3"
      """
      return pytesseract.image_to_string(PIL.Image.open(image_file_path), config=config)

  def main(self):
    config = r"--psm 6 --oem 3"
    input_folder = "InputImageFiles"
    output_folder = "OutputTextFiles"
    image_files = [file for file in os.listdir(input_folder) if file.endswith('.png') or file.endswith('.jpg')]

    for image_file in image_files:
        image_file_path = os.path.join(input_folder, image_file)
        text = self.get_text_from_image(self, image_file_path, config)
        language = langdetect.detect(text)
        open(os.path.join(output_folder, image_file + ".txt"), "w").write("Detected language: " + language + "\n" + "\n" + "Found Text: " + text)

item = TesseractImageToText
TesseractImageToText.main(item)
