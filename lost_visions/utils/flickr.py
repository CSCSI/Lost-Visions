# coding=utf-8
import os
import errno
from nltk import corpus
from BeautifulSoup import BeautifulSoup
import re
import urllib
import urllib2
from django.utils.encoding import smart_unicode
import subprocess

__author__ = 'Ian Harvey'


def getImageTags(url, size='o'):

    allTags = dict()
    large_image_resp = urllib2.urlopen(url + '/sizes/' + size + '/')

    if large_image_resp.code == 200:
        large_image_resp_data = large_image_resp.read()
        xml = BeautifulSoup(large_image_resp_data)

        for elm in xml.findAll('div', {'id': 'allsizes-photo'}):
            for img in elm.findAll('img'):
                allTags['image_location'] = img['src']


    resp = urllib2.urlopen(url)

    if resp.code == 200:
        data = resp.read()

        ## use for local files
        # with open ("image-1.html", "r") as myfile:
        #     data=myfile.read().replace('\n', '')


        xml = BeautifulSoup(data)

        counter = 0
        for elm in xml.findAll('a', {'class': 'tag-item ywa-track'}):
            if ":" in elm.text:
                kv = elm.text.split(':')
                k = kv[0].strip()
                v = kv[1].strip()
                allTags[k] = v
            else:
                counter += 1
                allTags[str(counter)] = elm.text



                # info taken from the photo description side bar,
                # not the metadata which is similar but the formatting sucks.
        for elm in xml.findAll('div', {'class': 'photo-desc'}):

        # the 2nd <p> block has the data we want, ignore the others
            data = str(elm.findAll('p')[1])

            #split by new line
            allkeyvalues = data.split('<br />')

            for kv in allkeyvalues:

            #regex to remove <strong> <p> and other html tags
                line = re.sub(r"(<[^>]+>)", "", kv)

                kvsplit = line.split(':')

                #store the string before the : as the key, and the words afterwards as the value
                #strip whitespace from both ends.
                allTags[kvsplit[0].strip()] = kvsplit[1].strip()

        #printing everything for debug
        # for key in allTags:
        #     print key + '       :       ' + allTags[key]

        return allTags
    else:
        print 'error with url : ' + url
        return None



def getImagePagesFromBasePage(url, imagecounter=0):
    resp = urllib2.urlopen(url)
    if resp.code == 200:
        pageUrls = dict()
        print url

        xml = BeautifulSoup(resp.read())

        for elm in xml.findAll('span', {'class': 'photo_container pc_ju'}):
            for photoclick in elm.findAll('a'):
                pageUrls[imagecounter] = 'http://www.flickr.com' + photoclick['href']
                imagecounter += 1
            # print pageUrls
        return pageUrls
    else:
        return None


def downloadImage(image_url, download_folder=None):
    filename = image_url.rsplit('/', 1)[1]
    if download_folder is not None:
        try:
            os.makedirs(download_folder)
        except OSError, exc:
            if exc.errno != errno.EEXIST:
                raise

        filename = os.path.join(download_folder, filename)

    if not os.path.exists(filename):
        urllib.urlretrieve(image_url, filename)
    return filename


def getTagsFromBasePage(baseurl=None, basepagenumber=None,
                        output_file=None, downloadImages=False, download_folder=None):
    # base_url = 'http://www.flickr.com/photos/britishlibrary/page'

    if basepagenumber is None:
        pagecount = 0
    else:
        pagecount = basepagenumber

    imagecounter = 0
    fail = False
    allPageTags = dict()

    while not fail:

        if basepagenumber is not None:
            page_url = baseurl + str(pagecount)
        else:
            page_url = baseurl
        pageUrls = getImagePagesFromBasePage(page_url, imagecounter)
        if pageUrls is not None:
            print 'page ' + str(pagecount) + ' images(total) ' + str(len(pageUrls))

            pageImageTags = dict()

            for urlCounter in pageUrls:
                print 'URL: ' + pageUrls[urlCounter]
                print 'Image number : ' + str(imagecounter)
                if output_file is not None:
                    output_file.write('\n\n' + pageUrls[urlCounter] + '\n')
                imageTags = getImageTags(pageUrls[urlCounter])

                if imageTags is not None:
                    for key in imageTags:
                        print key + '       :       ' + imageTags[key]
                        if output_file is not None:
                            outputString = (key + "::::" + imageTags[key] + '\n')
                            strstring = smart_unicode(outputString, encoding='utf-8', strings_only=False,
                                                      errors='strict').encode('utf-8')
                            # outputString #.decode('utf8')
                            output_file.write(strstring)
                    pageImageTags[urlCounter] = imageTags

                if downloadImages:
                    downloadImage(imageTags['image_location'], download_folder)

                imagecounter += 1
            allPageTags[pagecount] = pageImageTags
            pagecount += 1

            # stop when we go through too many (3) base pages
            if pagecount > 3:
                fail = True
        else:
            fail = True

    return allPageTags



urls = ("http://www.flickr.com/photos/12403504@N02/11008336364/in/photolist-hLLASQ",
        "http://www.flickr.com/photos/12403504@N02/11224008225",
        "http://www.flickr.com/photos/12403504@N02/11305545956",
        "http://www.flickr.com/photos/12403504@N02/11307140774",
        "http://www.flickr.com/photos/britishlibrary/11031313694/"
)



def getTextFromImage(url):
    urllib.urlretrieve(url, "image.jpg")

    subprocess.call(["convert", "-alpha", "set", "-auto-level", "-auto-gamma",
                     "-compress", "none", "image.jpg", "output.tiff"])

    print ('converted file')

    subprocess.call(["tesseract", "output.tiff", "text"])

    read_and_clean('text.txt')


def clean_ocr_text(whole_file):
    textOutputFile = open('./output_text.txt', 'a')
    words = []

    for line in whole_file:
        for word in line:
            word = unicode(word, 'ascii', 'ignore')
            word = word.lower().strip()
            word = re.sub(ur'[\W_]+', u'', word, flags=re.UNICODE)

            stop = corpus.stopwords.words('english')
            if len(word) > 2 and word not in stop:
                words.append(word)
                textOutputFile.write(str(word) + " ")

    textOutputFile.close()
    print words


def readFile(filename):
    whole_file = []
    with open(filename) as f:
        for line in f:
            words = line.split(' ')
            whole_file.append(words)

    return whole_file


def read_and_clean(file):

    whole_file_words = readFile(file)

    clean_ocr_text(whole_file_words)

