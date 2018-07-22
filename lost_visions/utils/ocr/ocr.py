import StringIO
import os
import zipfile

import pytesseract
import time
from PIL import Image
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def get_zip_path(root_folder, book_id, volume='0'):
    book_id = book_id + '_' + volume.lstrip('0')
    # print book_id

    # try:
    for a_file in os.listdir(root_folder):
        # print a_file
        disk_folder = os.path.join(root_folder, a_file)
        if 'disk5' in disk_folder:
            disk_folder = os.path.join(disk_folder, 'JP2')
        for b_file in os.listdir(disk_folder):
            # print b_file
            if book_id in b_file:
                # print b_file
                if int(b_file.split('_')[1]) == int(volume):
                    if 'disk5' in disk_folder:
                        return os.path.join(root_folder, os.path.join(os.path.join(a_file, 'JP2'), b_file))
                    else:
                        joined_path = os.path.join(root_folder, os.path.join(a_file, b_file))
                        return joined_path
    # except Exception as e:
    #     print 'get_zip_path', str(e), type(e)
    #     raise e


def find_zip(book_id, volume):
    web_folder = os.path.join('', 'media')
    web_folder = os.path.join(web_folder, 'page_zips')

    root_folder = os.path.join(BASE_DIR, 'lost_visions')
    root_folder = os.path.join(root_folder, 'static')
    root_folder = os.path.join(root_folder, web_folder)
    # zip_path = '/home/ubuntu/PycharmProjects/Lost-Visions/lost_visions/static/media/images/003871282_0_1-324pgs__1023322_dat.zip'

    root_folder = "/home/ubuntu/ocr"
    zip_path = get_zip_path(root_folder, book_id, volume)

    if zip_path is None:
        raise

    archive = zipfile.ZipFile(zip_path, 'r')
    return archive


def get_page_from_archive(archive, page):
    inner_zipped_file = None
    for zipped_file in archive.namelist():
        page_number_found = zipped_file.split('_')[-1]
        page_number_found = page_number_found.split('.')[0]
        if int(page) == int(page_number_found):
            inner_zipped_file = zipped_file
            return inner_zipped_file

    if inner_zipped_file is None:
        raise


def text_file_from_img(img_file, filename, compress=False):
    imgdata = archive.read(img_file)

    input_image = StringIO.StringIO(imgdata)
    input_image.seek(0)
    img = Image.open(input_image)

    if compress:
        quality = 10
        filename = 'compress_{}_{}'.format(quality, filename)
        img2_fp = StringIO.StringIO()
        img.save(img2_fp, "JPEG", quality=quality, optimize=True, progressive=True)
        img2_fp.seek(0)
        img2 = Image.open(img2_fp)

        img_text = pytesseract.image_to_string(img2)

    else:
        img_text = pytesseract.image_to_string(img)

    print img_text

    with open(filename, 'w') as f1:
        f1.write(img_text.encode('utf8'))
    return filename


book_id = "001698719"
volume = "0"
page = "11"
start_page = 3
end_page = None
#1-324

archive = find_zip(book_id, volume)

if archive is None:
    raise

print archive.filename

num_pages = None
try:
    fname_arr = archive.filename.split('/')
    archive_name_arr = fname_arr[-1].split('_')
    filename_pages_subsection = archive_name_arr[2].split('-')[1]
    num_pages = ''.join(c for c in filename_pages_subsection if c.isdigit())
    num_pages = int(num_pages)
except:
    num_pages = len(archive.filelist)

print(num_pages)
if num_pages is None:
    raise

if end_page is None or end_page > num_pages:
    end_page = num_pages


for page in range(start_page, end_page):
    with open('log.log', 'a') as log_file:

        start = time.time()

        inner_zipped_file = get_page_from_archive(archive, page)

        filename = '{}_{}_{}.txt'.format(book_id, volume, page)
        # filename = text_file_from_img(inner_zipped_file, filename)

        end = time.time()
        diff = end - start
        log_file.write('{}\t{}\t{}\t{}\n'.format(
            filename,
            start,
            end,
            diff
        ).encode('utf8'))
