from PIL import Image
import pytesseract

# Optional: Set the path to the Tesseract executable if it's not in your PATH
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Open an image file
image = Image.open('meme.png')  # Replace with your image path

# Run OCR on the image
text = pytesseract.image_to_string(image)

# Print the extracted text
print(text)