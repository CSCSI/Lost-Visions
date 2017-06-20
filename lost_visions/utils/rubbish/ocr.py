import os
import sys

from PIL import ImageFilter

# http://www.fmwconcepts.com/imagemagick/textcleaner/index.php

IMG_DIR = '/home/ubuntu/PycharmProjects/Lost-Visions/lost_visions/static/media/images/scans/embellishments/1848'
# EXAMPLE_IMG = '003984685_02_000450_1_1848_embellishments.jpg'

EXAMPLE_IMG = '000092976_0_000308_1_1848_embellishments.jpg'

# IMG_DIR = '/home/ubuntu'
# EXAMPLE_IMG = 'output_clean.jpg'

img_texts = {}


def dir_list(dir):
    from os import listdir
    from os.path import isfile, join
    only_files = [f for f in listdir(dir) if isfile(join(dir, f))]

    for f in only_files:
        test(f)
    print img_texts


def test(f):
    print f
    try:
        import Image
        print 'Image'
    except ImportError:
        from PIL import Image
        print 'PIL image'
    import pytesseract

    # pytesseract.pytesseract.tesseract_cmd = '<full_path_to_your_tesseract_executable>'
    # Include the above line, if you don't have tesseract executable in your PATH
    # Example tesseract_cmd: 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'

    im_prime = Image.open(os.path.join(IMG_DIR, f))
    txt_prime = pytesseract.image_to_string(im_prime)
    img_texts[f] = {'txt_prime': txt_prime}
    print('im_prime', txt_prime)
    print

    # BLUR
    # CONTOUR
    # DETAIL
    # EDGE_ENHANCE
    # EDGE_ENHANCE_MORE
    # EMBOSS
    # FIND_EDGES
    # SMOOTH
    # SMOOTH_MORE
    # SHARPEN

    # im1 = im.filter(ImageFilter.SHARPEN)
    # print(pytesseract.image_to_string(im1))
    # im1.save('img/sharpen.jpg')

    # im2 = im.filter(ImageFilter.EDGE_ENHANCE_MORE)
    # print(pytesseract.image_to_string(im2))
    # im2.save('img/EDGE_ENHANCE_MORE.jpg')
    #
    # im2 = im_prime.filter(ImageFilter.DETAIL)
    # print('DETAIL', pytesseract.image_to_string(im2))
    # print
    # im2.save('img/DETAIL.jpg')
    #
    # im = im.filter(ImageFilter.EDGE_ENHANCE)
    # print(pytesseract.image_to_string(im))
    # im.save('img/EDGE_ENHANCE.jpg')
    #
    # im3 = im.filter(ImageFilter.FIND_EDGES)
    # print(pytesseract.image_to_string(im3))
    # im3.save('img/FIND_EDGES.jpg')
    #
    # im3 = im.filter(ImageFilter.SHARPEN)
    # im3 = im3.filter(ImageFilter.SHARPEN)
    # print(pytesseract.image_to_string(im3))
    # im3.save('img/SHARPEN_SHARPEN.jpg')

    # im = im.convert('1')  # convert image to black and white

    im = im_prime.convert('L')
    im = im.filter(ImageFilter.SHARPEN)

    im = im.point(lambda x: 0 if x < 180 else 255, '1')
    im.save("img/result_bw.png")
    im = im.convert('L')

    im = im.filter(ImageFilter.SHARPEN)
    im = im.filter(ImageFilter.SHARPEN)

    print('SHARPEN_SHARPEN_bw', pytesseract.image_to_string(im))
    txt_SHARPEN = pytesseract.image_to_string(im)
    img_texts[f]['txt_SHARPEN'] = txt_SHARPEN

    im.save('img/SHARPEN_SHARPEN_bw.jpg')

    # print(pytesseract.image_to_string(Image.open('test-european.jpg'), lang='fra'))

    # IMG_DIR = '/home/ubuntu'
    # EXAMPLE_IMG = 'output_clean.jpg'
    # im_prime = Image.open(os.path.join('/home/ubuntu', 'output_clean.jpg'))
    # print('output_clean', pytesseract.image_to_string(im_prime))
    # print

if __name__ == "__main__":
    print 'Options are: test'
    print 'Running..'
    print sys.argv
    for arg in sys.argv[1:]:
        print arg

        if arg == "test":
            dir_list(IMG_DIR)

    if len(sys.argv) < 2:
        dir_list(IMG_DIR)
