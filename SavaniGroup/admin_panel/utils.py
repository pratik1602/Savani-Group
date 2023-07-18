from bson.binary import Binary

def convert_inmemory_file_to_bytes(inmemory_file):
    inmemory_file.seek(0)  # Ensure the file pointer is at the beginning
    file_data = inmemory_file.read()
    return file_data


# Function to send the PDF file to the MongoDB collection
def pdf_convert(pdf_file_path):
    with open(pdf_file_path, "rb") as pdf_file:
        pdf_data = pdf_file.read()
        pdf_binary = Binary(pdf_data)
        return pdf_binary