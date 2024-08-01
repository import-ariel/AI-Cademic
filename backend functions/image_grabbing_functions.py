import PyPDF2
import fitz  #PyMuPDF
import io
from PIL import Image
import os
import re


def clean_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def get_unique_filename(output_folder, base_name, file_ext, side=None):
    '''
    A function to handle the fact that some "Figures" 
    are actually multiple separate images that have one "figure" label 
    (often with left, right, bottom)
    '''
    if side:
        unique_name = f"{base_name}_{side}.{file_ext}"
        if os.path.exists(os.path.join(output_folder, unique_name)):
            sides = ["left", "right", "top", "bottom"]
            sides.remove(side)  # Remove the current side from options when it has already been used 
            for new_side in sides:
                unique_name = f"{base_name}_{new_side}.{file_ext}"
                if not os.path.exists(os.path.join(output_folder, unique_name)):
                    break
    else:
        counter = 1
        unique_name = f"{base_name}.{file_ext}"
        while os.path.exists(os.path.join(output_folder, unique_name)):
            unique_name = f"{base_name}_{counter}.{file_ext}"
            counter += 1
    return unique_name


def extract_images_from_pdf(pdf_path, output_folder):
    '''
    Extracting images from PDFs by iterating over each page of the PDF
    '''
    # Open the PDF file with PyMuPDF
    pdf_document = fitz.open(pdf_path)
    
    # Open the PDF file with PyPDF2
    pdf_file = open(pdf_path, "rb")
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    image_count = 0
    figure_count = {}

    # go through each page
    for page_number in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_number]
        try:
            xObject = page['/Resources']['/XObject'].get_object()
            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    image = xObject[obj]
                    size = (image['/Width'], image['/Height'])
                    data = image.get_data()

                    if image['/ColorSpace'] == '/DeviceRGB':
                        mode = "RGB"
                    elif image['/ColorSpace'] == '/DeviceCMYK':
                        mode = "CMYK"
                    else:
                        mode = "P"

                    if image['/Filter'] == '/DCTDecode':
                        file_ext = "jpg"
                        image_data = io.BytesIO(data)
                        img = Image.open(image_data)
                    elif image['/Filter'] == '/FlateDecode':
                        file_ext = "png"
                        # Decode the FlateDecode (typically PNG) data
                        img = Image.frombytes(mode, size, data)
                    elif image['/Filter'] == '/JPXDecode':
                        file_ext = "jp2"
                        image_data = io.BytesIO(data)
                        img = Image.open(image_data)
                    else:
                        file_ext = "bmp"
                        image_data = io.BytesIO(data)
                        img = Image.open(image_data)

                    # extract text around the image
                    # this assumes it's on the same page, given time, we will prepare for edge cases
                    pdf_page = pdf_document.load_page(page_number)
                    text = pdf_page.get_text("text")
                    figure_number = None
                    side = None

                    for line in text.split('\n'):
                        if 'Figure' in line:
                            figure_number = line.strip().split()[1]  # Get the figure number
                            if 'left' in line.lower():
                                side = "left"
                            elif 'right' in line.lower():
                                side = "right"
                            elif 'top' in line.lower():
                                side = "top"
                            elif 'bottom' in line.lower():
                                side = "bottom"
                            break

                    if figure_number:
                        sanitized_figure_number = clean_filename(figure_number)
                        base_name = f"{os.path.basename(pdf_path).split('.')[0]}_Figure_{sanitized_figure_number}"
                        unique_name = get_unique_filename(output_folder, base_name, file_ext, side)
                    else:
                        image_count += 1
                        base_name = f"{os.path.basename(pdf_path).split('.')[0]}_image{image_count}"
                        unique_name = get_unique_filename(output_folder, base_name, file_ext)

                    #save image
                    image_path = os.path.join(output_folder, unique_name)
                    img.save(image_path)
                    print(f"Saved image {image_path}")

        except KeyError:
            print(f"No images found on page {page_number + 1}")
        except Exception as e:
            print(f"Could not extract image on page {page_number + 1}, object {obj}: {e}")

    pdf_file.close()



def process_all_pdfs_in_folder(folder_path, output_folder):
    '''
    Add all PDFs into a folder
    Specify folder_path - suggested to create folder specific to this task
    '''
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            print(f"Processing file: {pdf_path}")
            extract_images_from_pdf(pdf_path, output_folder)
