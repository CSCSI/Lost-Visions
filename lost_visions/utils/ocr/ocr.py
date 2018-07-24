import StringIO
import os
import zipfile
from math import sqrt

import pytesseract
import time
import sys
from PIL import Image

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
THIS_FILE_PATH = os.path.realpath(__file__)


def standard_deviation(lst, population=True):
    # https://codeselfstudy.com/blog/how-to-calculate-standard-deviation-in-python/
    min_time = min(lst)
    max_time = max(lst)

    """Calculates the standard deviation for a list of numbers."""
    num_items = len(lst)
    mean = sum(lst) / num_items
    differences = [x - mean for x in lst]
    sq_differences = [d ** 2 for d in differences]
    ssd = sum(sq_differences)

    print('The minimum is {}.'.format(min_time))
    print('The maximum is {}.'.format(max_time))
    print('The mean is {}.'.format(mean))

    # Note: it would be better to return a value and then print it outside
    # the function, but this is just a quick way to print out the values along
    # the way.
    if population is True:
        print('This is POPULATION standard deviation.')
        variance = ssd / num_items
    else:
        print('This is SAMPLE standard deviation.')
        variance = ssd / (num_items - 1)
    sd = sqrt(variance)
    # print('The differences are {}.'.format(differences))
    # print('The sum of squared differences is {}.'.format(ssd))
    print('The variance is {}.'.format(variance))
    print('The standard deviation is {}.'.format(sd))

    return sd

class OCReveryting():

    def __init__(self):
        self.total_page_count = 0
        self.total_archive_count = 0
        self.logfile = 'log.log'
        self.mean = 40

    def get_zip_path(self, root_folder, book_id, volume='0'):
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

    def get_root_folder(self):

        path = os.path.dirname(THIS_FILE_PATH)
        path = os.path.dirname(path)
        path = os.path.dirname(path)

        path = os.path.join(path, 'static')
        path = os.path.join(path, 'media')
        path = os.path.join(path, 'page_zips')

        # root_folder = "/home/ubuntu/ocr"

        return path

    def find_zip(self, book_id, volume):
        root_folder = self.get_root_folder()
        # zip_path = '/home/ubuntu/PycharmProjects/Lost-Visions/lost_visions/static/media/images/003871282_0_1-324pgs__1023322_dat.zip'

        root_folder = "/home/ubuntu/ocr"
        zip_path = self.get_zip_path(root_folder, book_id, volume)

        if zip_path is None:
            raise

        archive = zipfile.ZipFile(zip_path, 'r')
        return archive


    def get_page_from_archive(self, archive, page):
        inner_zipped_file = None
        for zipped_file in archive.namelist():
            page_number_found = zipped_file.split('_')[-1]
            page_number_found = page_number_found.split('.')[0]
            if int(page) == int(page_number_found):
                inner_zipped_file = zipped_file
                return inner_zipped_file

        if inner_zipped_file is None:
            raise


    def text_file_from_img(self, archive, img_file, filename, compress=False):
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


    def ocr_book(self, book_id, volume, start_page, end_page):

        archive = self.find_zip(book_id, volume)

        if archive is None:
            raise

        print archive.filename

        num_pages = self.count_pages_in_archive(archive)

        print(num_pages)
        if num_pages is None:
            raise

        if end_page is None or end_page > num_pages:
            end_page = num_pages

        print 'start_page', start_page, 'end_page', end_page
        for page in range(start_page, end_page + 1):
            with open(self.logfile, 'a') as log_file:

                start = time.time()

                inner_zipped_file = self.get_page_from_archive(archive, page)

                filename = '{}_{}_{}.txt'.format(book_id, volume, page)
                filename = self.text_file_from_img(archive, inner_zipped_file, filename)

                end = time.time()
                diff = end - start
                log_file.write('{}\t{}\t{}\t{}\n'.format(
                    filename,
                    start,
                    end,
                    diff
                ).encode('utf8'))

    def count_pages_in_archive(self, archive):
        try:
            fname_arr = archive.filename.split('/')
            archive_name_arr = fname_arr[-1].split('_')
            filename_pages_subsection = archive_name_arr[2].split('-')[1]
            num_pages = ''.join(c for c in filename_pages_subsection if c.isdigit())
            return int(num_pages)
        except:
            return len(archive.filelist)

    def count_all_pages(self):
        root_folder = self.get_root_folder()
        print 'base_folder', BASE_DIR
        print 'root_folder', root_folder
        for a_file in os.listdir(root_folder):
            print 'folder', a_file
            disk_folder = os.path.join(root_folder, a_file)
            if 'disk5' in disk_folder:
                disk_folder = os.path.join(disk_folder, 'JP2')
            for b_file in os.listdir(disk_folder):
                print b_file
                try:
                    b_file_path = os.path.join(disk_folder, b_file)
                    archive = zipfile.ZipFile(b_file_path, 'r')
                    page_count = self.count_pages_in_archive(archive)
                    self.total_page_count += page_count
                    self.total_archive_count += 1

                    print '\nTotal pages : {}'.format(ocr.total_page_count)
                    print 'Total archives : {}'.format(ocr.total_archive_count)
                    print 'Average pages per archive : {}'.format(
                        ocr.total_page_count / ocr.total_archive_count)
                    print 'Assuming mean tesseract time per page (seconds) {}'.format(
                        self.mean)
                    print 'Average time (mins, hours) to complete : {}, {}'.format(
                        float(ocr.total_page_count * self.mean / 60),
                        float(ocr.total_page_count * self.mean / 60 / 60)
                    )
                except Exception as e:
                    print e

    def ocr_stats(self, logfile):
        times = []
        if not os.path.isfile(logfile):
            print 'No log file, using default 40s'
            return self.mean

        with open(logfile, 'r') as logfile_handle:
            for line in logfile_handle:
                times.append(float(line.split('\t')[-1]))
        standard_deviation(times)

        mean = sum(times) / len(times)
        self.mean = mean
        return self.mean


if __name__ == "__main__":

    path = os.path.dirname(THIS_FILE_PATH)
    path = os.path.dirname(path)
    path = os.path.dirname(path)

    path = os.path.join(path, 'static')
    path = os.path.join(path, 'media')
    path = os.path.join(path, 'page_zips')
    print path

    print 'Options are: test, count_all_pages'
    print 'Running..'
    # print sys.argv
    for arg in sys.argv[1:]:

        ocr = OCReveryting()
        if arg == "test":
            book_id = "001698719"
            volume = "0"
            page = "11"
            start_page = 3
            end_page = 11
            # 1-324 - 586

            ocr.ocr_book(book_id, volume, start_page, end_page)

        if arg == "count_all_pages":
            ocr.ocr_stats(ocr.logfile)
            ocr.count_all_pages()

        if arg == "ocr_stats":
            ocr.ocr_stats(ocr.logfile)

    if len(sys.argv) < 2:
        print 'Doing nothing, exiting'
        exit(0)
