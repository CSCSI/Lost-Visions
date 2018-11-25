import StringIO
import multiprocessing
import os
import threading
import zipfile
from math import sqrt
import pytesseract
import time
import sys
import requests
from PIL import Image
from multiprocessing.dummy import Pool as ThreadPool

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

    print('The minimum is {0}.'.format(min_time))
    print('The maximum is {0}.'.format(max_time))
    print('The mean is {0}.'.format(mean))
    print('The total time is {0} seconds, or {1} minutes, or {2} hours'.format(
        sum(lst),
        sum(lst) / 60,
        sum(lst) / 60 / 60
    ))

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
    # print('The differences are {0}.'.format(differences))
    # print('The sum of squared differences is {0}.'.format(ssd))
    print('The variance is {0}.'.format(variance))
    print('The standard deviation is {0}.'.format(sd))

    return sd


class OCReveryting:

    def __init__(self):
        self.cpu_time = 0
        self.total_page_count = 0
        self.total_archive_count = 0
        self.logfile = os.path.join(BASE_DIR, 'log.log')
        self.mean = 40
        self.POOL_SIZE = multiprocessing.cpu_count()

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

        # root_folder = "/home/ubuntu/ocr"
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

    def text_from_img(self, archive, img_file, compress, quality=50):
        imgdata = archive.read(img_file)

        input_image = StringIO.StringIO(imgdata)
        input_image.seek(0)
        img = Image.open(input_image)

        if compress:
            img2_fp = StringIO.StringIO()
            img.save(img2_fp, "JPEG", quality=quality, optimize=True, progressive=True)
            img2_fp.seek(0)
            img2 = Image.open(img2_fp)
            img_text = pytesseract.image_to_string(img2)
        else:
            img_text = pytesseract.image_to_string(img)

        # print img_text.encode('utf-8')
        return img_text

    def text_file_from_img(self, archive, img_file, filename, compress=False, quality=50):
        img_text = self.text_from_img(archive, img_file, compress, quality)

        if compress:
            filename = 'compress_{0}_{1}'.format(quality, filename)

        with open(filename, 'w') as f1:
            f1.write(img_text.encode('utf8'))
        return filename

    def ocr_book_pages(self, book_id, volume, start_page, end_page, zip_path=None):

        ocr_files = []
        if zip_path is None:
            archive = self.find_zip(book_id, volume)
        else:
            archive = zipfile.ZipFile(zip_path, 'r')
        if archive is None:
            raise

        print('Loaded archive {}'.format(archive.filename))
        num_pages = self.count_pages_in_archive(archive)
        print('Pages in archive: {}'.format(num_pages))
        if num_pages is None:
            raise

        if end_page is None:
            end_page = num_pages

        start_page = int(start_page)
        end_page = int(end_page)

        if end_page > num_pages:
            end_page = num_pages

        print 'start_page', start_page, 'end_page', end_page
        pages_to_ocr = []

        timestamp_folder = 'runtime_{}'.format(str(time.time()))
        try:
            os.mkdir(timestamp_folder)
        except:
            pass

        output_folder = os.path.join(
            timestamp_folder,
            '{}_{}_{}_{}'.format(book_id, volume, start_page, end_page)
        )
        try:
            os.mkdir(output_folder)
        except:
            pass

        global_lock = threading.Lock()
        global_start = time.time()

        for page in range(start_page, end_page + 1):
            inner_zipped_file = self.get_page_from_archive(archive, page)
            filename = os.path.join(output_folder, '{0}_{1}_{2}.txt'.format(book_id, volume, page))
            pages_to_ocr.append((archive, inner_zipped_file, filename, global_lock))

        print('Pool will be size {}'.format(self.POOL_SIZE))
        pool = ThreadPool(self.POOL_SIZE)
        # Open the urls in their own threads
        # and return the results
        results = pool.map(self.threadable_ocr, pages_to_ocr)
        # close the pool and wait for the work to finish
        pool.close()
        pool.join()

        global_end = time.time()
        print('Time for {} pages to OCR: {}'.format(len(pages_to_ocr), global_end - global_start))
        with open('ocr_timings.txt', 'a') as f1:
            f1.write(
                'Wall time,{},CPU time,{},Number pages,{},Time per page,{},Pool_Size,{}\n'.format(
                    global_end - global_start,
                    self.cpu_time,
                    len(pages_to_ocr),
                    (global_end - global_start) / len(pages_to_ocr),
                    self.POOL_SIZE
                ))
        return ocr_files

    def threadable_ocr(self, ocr_metadata):
        # print('ocr_metadata', ocr_metadata)
        archive= ocr_metadata[0]
        inner_zipped_file = ocr_metadata[1]
        filename = ocr_metadata[2]
        global_lock = ocr_metadata[3]

        page_start = time.time()
        print 'Thread{}/{}, WillCreate {}'.format(
            threading.currentThread().name,
            threading.currentThread().ident,
            filename
        )

        returned_filename = self.text_file_from_img(archive, inner_zipped_file, filename)

        print 'Thread{}/{}, WroteFile {}'.format(
            threading.currentThread().name,
            threading.currentThread().ident,
            filename
        )
        page_end = time.time()
        task_time = page_end - page_start

        # Writing how long that took, which probably increases how long it will take
        global_lock.acquire()
        self.cpu_time += task_time
        with open('ocr_finegrain_timings.txt', 'a') as f1:
            f1.write('Time {}, Thread{}/{}, WroteFile {}\n'.format(
                task_time,
                threading.currentThread().name,
                threading.currentThread().ident,
                filename
            ))
        global_lock.release()
        return returned_filename

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

                    print '\nTotal pages : {0}'.format(ocr.total_page_count)
                    print 'Total archives : {0}'.format(ocr.total_archive_count)
                    print 'Average pages per archive : {0}'.format(
                        ocr.total_page_count / ocr.total_archive_count)
                    print 'Assuming mean tesseract time per page (seconds) {0}'.format(
                        self.mean)
                    print 'Average time (mins, hours) to complete : {0}, {1}'.format(
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

    def ocr_zip_file(self, zip_path):
        print('Zip path {}'.format(zip_path))
        # /media/lostvisions/New Volume/003871282_0_1-324pgs__1023322_dat.zip
        if os.path.isfile(zip_path):
            basename = os.path.basename(zip_path)
            book_metadata = basename.split('_')

            book_id = book_metadata[0]
            volume = book_metadata[1]
            start_page = book_metadata[2].split('-')[0]
            end_page = ''.join(c for c in book_metadata[2].split('-')[1] if c.isdigit())

            # Use this to test different pool sizes
            # for poolsize in range(7, 9):
            #     ocr.POOL_SIZE = poolsize
            #     ocr_files = ocr.ocr_book_pages(book_id, volume, 20, 30, zip_path=zip_path)
            #     print(ocr_files)

            # ocr.POOL_SIZE = 10
            ocr_files = ocr.ocr_book_pages(book_id, volume, start_page, end_page, zip_path=zip_path)
            print(ocr_files)
        else:
            print('Zip path {} is not a valid file'.format(zip_path))

    def scrape_zip_urls_from_url(self):
        import urllib2
        from bs4 import BeautifulSoup

        url = 'http://illustrationarchive.cf.ac.uk/static/media/page_zips/disk1/'

        conn = urllib2.urlopen(url)
        html = conn.read()

        soup = BeautifulSoup(html)
        links = soup.find_all('a')

        full_links = []
        for tag in links:
            link = tag.get('href', None)
            if link is not None and str(link).endswith('.zip'):
                full_links.append('{}{}\n'.format(url, link))
        with open('zip_urls.txt', 'w') as zip_urls_file:
            for link in full_links:
                zip_urls_file.write(link)


if __name__ == "__main__":

    ocr = OCReveryting()

    print ocr.get_root_folder()

    print 'Options are: test, count_all_pages, ocr_book_zip'
    print 'Running..'
    print sys.argv

    if len(sys.argv) < 2:
        print 'Doing nothing, exiting'
        exit(0)

    arg = sys.argv[1]

    if arg == "scrape_html_links":
        ocr.scrape_zip_urls_from_url()

    if arg == "test":
        book_id = "001698719"
        volume = "0"
        start_page = 3
        end_page = 11
        # 1-324 - 586

        ocr.ocr_book_pages(book_id, volume, start_page, end_page)

    if arg == "count_all_pages":
        ocr.ocr_stats(ocr.logfile)
        ocr.count_all_pages()

    if arg == "ocr_stats":
        ocr.ocr_stats(ocr.logfile)

    if arg == "ocr_book_zip":
        print('ocr_book_zip')
        if len(sys.argv) > 2:
            zip_path = sys.argv[2]
            ocr.ocr_zip_file(zip_path)
        else:
            print('Need a zip path')

    if arg == "ocr_dl_book_zip_list":
        print('ocr_dl_book_zip_list')
        if len(sys.argv) > 2:
            with open(sys.argv[2], 'r') as url_file:
                all_urls = url_file.readlines()
                # print all_urls

            for a_url in all_urls[:5]:
                a_url = a_url.strip()
                print('Downloading {}'.format(a_url))
                zip_file = a_url.split('/')[-1]

                if not os.path.isfile(zip_file):
                    # We do not have the zip yet, download it
                    response = requests.head(a_url)
                    file_size = None
                    if 'content-length' in response.headers:
                        file_size = float(response.headers['content-length'])

                    response = requests.get(a_url, stream=True)
                    response.raise_for_status()

                    chunk_count = 0
                    with open(zip_file, 'wb') as handle:
                        for block in response.iter_content(1024):
                            if file_size:
                                chunk_count += 1
                                percent = (1024 * chunk_count) / file_size * 100
                                if percent < 100:
                                    print 'Downloaded {}%  \r'.format(round(percent, 2)),
                                    sys.stdout.flush()
                                else:
                                    print '{}% Download Complete'.format(round(percent, 2))
                            handle.write(block)

                ocr.ocr_zip_file(zip_file)
                os.remove(a_url)
        else:
            print('Need a zip path')



