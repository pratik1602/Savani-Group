# from bson.binary import Binary
import cloudinary
import cloudinary.uploader
from decouple import config
# from pdf2image import convert_from_path
# from io import BytesIO
# from PIL import Image
# from pdf2image import convert_from_bytes
# import io
# import os
# from pdf2image import convert_from_path


# def get_file_extension(file_path):
#     # Split the file path into the base name and extension using os.path.splitext()
#     _, extension = os.path.splitext(file_path)
#     return extension


# def convert_pdf_bytes_to_image(pdf_bytes):
#     # Convert PDF bytes data to images using pdf2image
#     image = convert_from_bytes(pdf_bytes)

#     # Get the first page image (you can loop through 'images' to get all pages)
#     # first_page_image = images[0]

#     return image

# def convert_inmemory_file_to_bytes(inmemory_file):
#     inmemory_file.seek(0)  # Ensure the file pointer is at the beginning
#     file_data = inmemory_file.read()
#     return file_data


# # Function to send the PDF file to the MongoDB collection
# def pdf_convert(pdf_file_path):
#     with open(pdf_file_path, "rb") as pdf_file:
#         pdf_data = pdf_file.read()
#         pdf_binary = Binary(pdf_data)
#         return pdf_binary
    
# def convert_bytes_to_image(image_bytes):
#     # Read the image from bytes data using BytesIO
#     image_stream = BytesIO(image_bytes)

#     # Open and convert the image using Pillow (PIL)
#     image = Image.open(image_stream)

#     return image

cloudinary.config(
    cloud_name=config('CLOUD_NAME'),        # Replace with your Cloudinary cloud_name
    api_key=config('API_KEY'),              # Replace with your Cloudinary api_key
    api_secret=config('API_SECRET')         # Replace with your Cloudinary api_secret
)


def upload_aadhar(aadhar_img):
    result = cloudinary.uploader.upload(aadhar_img, resource_type="image", folder="Savani_Group/Community_members/aadhar")    
    img_url = result["secure_url"]

    return img_url

# Function to upload PDF document to Cloudinary and return the URL
def upload_pdf_to_cloudinary(pdf_file_path):
    # Store Pdf with convert_from_path function
    # images = convert_from_path(pdf_file_path)
    
    # for i in range(len(images)):
    
    #     # Save pages as images in the pdf
    #     images[i].save('page'+ str(i) +'.jpg', 'JPEG')
    # print("file_path", pdf_file_path)
    # extension = get_file_extension(pdf_file_path)
    # print("extension", extension)

    # file_data = convert_inmemory_file_to_bytes(pdf_file_path)
    # Convert the PDF file to images using pdf2image
    # image = convert_from_path(file_data)
    # image = convert_pdf_bytes_to_image(file_data)

    # Upload PDF to Cloudinary
    result = cloudinary.uploader.upload(pdf_file_path, resource_type="raw", folder="Savani_Group/Community_Services/Pdf_Forms")

    # Get the URL of the uploaded PDF
    pdf_url = result["secure_url"]

    return pdf_url