__author__ = 'ubuntu'

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")

from lost_visions import models


def save_location(book_id, volume, page, index, year, full_path):
    found_image = models.Image.objects.get(book_identifier=book_id, volume=volume, page=page, image_idx=index, date=year)

    if found_image == None:
        print 'No image for {} {} {} {} {} {}'.format(book_id, volume, page, index, year, full_path)

    new_location = models.ImageLocation.objects.get_or_create(image=found_image, location=full_path)
    # new_location.image = found_image
    # new_location.location = full_path
    # new_location.save()


def load_scratch_to_db(sizes):
    print 'db'

    root_folder = '/scratch/lost-visions/images-found/'

    # sizes = ['embellishments', 'medium', 'plates', 'covers']
    if 'embellishments' in sizes:
        # embellishments folder
        embellishment_path = os.path.join(root_folder, 'embellishments')
        for year_folder in os.listdir(embellishment_path):
            for embellishment_file in os.listdir(os.path.join(embellishment_path, year_folder)):
                filename_split = embellishment_file.split('_')

                book_id = filename_split[0]
                volume = filename_split[1]
                page = filename_split[2]
                index = filename_split[3]

                full_path = str(os.path.join(embellishment_path, embellishment_file))
                save_location(book_id, volume, page, index, year_folder, full_path)

    if 'medium' in sizes:
        # medium sized images folder
        medium_path = os.path.join(root_folder, 'medium')
        for year_folder in os.listdir(medium_path):
            for medium_file in os.listdir(os.path.join(medium_path, year_folder)):
                filename_split = medium_file.split('_')

                book_id = filename_split[0]
                volume = filename_split[1]
                page = filename_split[2]
                index = filename_split[3]

                full_path = str(os.path.join(medium_path, medium_file))
                save_location(book_id, volume, page, index, year_folder, full_path)

    if 'plates' in sizes:
        #     plate sized images folder
        plates_path = os.path.join(root_folder, 'plates')
        for year_folder in os.listdir(plates_path):
            for plates_file in os.listdir(os.path.join(plates_path, year_folder)):
                filename_split = plates_file.split('_')

                book_id = filename_split[0]
                volume = filename_split[1]
                page = filename_split[2]
                index = filename_split[3]

                full_path = str(os.path.join(plates_path, plates_file))
                save_location(book_id, volume, page, index, year_folder, full_path)

    if 'covers' in sizes:
        # cover sized image folder
        covers_path = os.path.join(root_folder, 'covers')
        for year_folder in os.listdir(covers_path):
            for covers_file in os.listdir(os.path.join(covers_path, year_folder)):
                filename_split = covers_file.split('_')

                book_id = filename_split[0]
                volume = filename_split[1]
                page = filename_split[2]
                index = filename_split[3]

                full_path = str(os.path.join(covers_path, covers_file))
                save_location(book_id, volume, page, index, year_folder, full_path)


load_scratch_to_db(['embellishments', 'medium', 'plates', 'covers'])