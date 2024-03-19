import os
current_dir = os.path.dirname(__file__)
os.chdir(current_dir)

import pytesseract
import cv2
import PIL.Image
from pytesseract import Output

class TextDetectionVis:
    def detect_words(self, config, image_file_path, output_folder, image_file):
      # detect words
      data = pytesseract.image_to_data(PIL.Image.open(image_file_path), config=config, output_type=Output.DICT)
      n_boxes = len(data['text'])
      img = cv2.imread(image_file_path)  # Move this line outside of the loop
      for i in range(n_boxes):
          if float(data['conf'][i]) > 60:
              height, width, _ = img.shape
              (x, y, width, height) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
              img = cv2.rectangle(img, (x, y), (x + width, y + height), (0, 255, 0), 2)
      cv2.imwrite(os.path.join(output_folder, image_file), img)  # Move this line outside of the loop too
              
      """
      boxes = pytesseract.image_to_boxes(PIL.Image.open(image_file_path), config=config)
      # detect characters
      for b in boxes.splitlines():
          box = b.split(' ')
          img = cv2.rectangle(img, (int(box[1]), height - int (box[2])), (int(box[3]), height - int(box[4])), (0, 255, 0), 2)
          
          cv2.imwrite(os.path.join(output_folder, image_file), img)
      """

    def main(self):
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
      """

      config = r"--psm 6 --oem 3"
      input_folder = "InputImageFiles"
      output_folder = "OutputImagesWithVis"
      image_files = [file for file in os.listdir(input_folder) if file.endswith('.png') or file.endswith('.jpg')]

      for image_file in image_files:
          image_file_path = os.path.join(input_folder, image_file)
          self.detect_words(config, image_file_path, output_folder, image_file)
    
item = TextDetectionVis()
item.main()