__author__ = 'ubuntu'

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")

from lost_visions import models


def save_location(book_id, volume, page, index, year, full_path):
    found_images = models.Image.objects.filter(book_identifier=book_id, volume=volume, page=page, image_idx=index, date=year)
    found_image = found_images[0]

    if found_image == None:
        print 'No image for {} {} {} {} {} {}'.format(book_id, volume, page, index, year, full_path)
    else:
        new_location = models.ImageLocation.objects.get_or_create(image=found_image, location=full_path)
        # new_location.image = found_image
        # new_location.location = full_path
        # new_location.save()


def make_file_list(sizes):
    root_folder = '/scratch/lost-visions/images-found/'

    for size in sizes:
        size_path = os.path.join(root_folder, size)
        if os.path.exists(size_path):
            with open(size, 'w') as f:
                for year_folder in os.listdir(size_path):
                    year_folder_path = os.path.join(size_path, year_folder)

                    for size_file in os.listdir(year_folder_path):
                        f.write(str(os.path.join(year_folder_path, size_file)) + '\n')


def db_from_file(sizes):

    counter = 0
    for size in sizes:
        if os.path.exists(size):
            with open(size, 'r') as f:
                writable_objects = []

                for line_number, line in enumerate(f.readlines()):
                    filepath_split = line.split('/')[-1]
                    filename_split = filepath_split.split('_')

                    book_id = filename_split[0]
                    volume = filename_split[1]
                    page = filename_split[2]
                    index = filename_split[3]

                    # save_location(book_id, volume, page, index, year_folder, full_path)
                    # try:
                    #     found_images = models.Image.objects.filter(
                    #         book_identifier=book_id,
                    #         volume=volume,
                    #         page=page,
                    #         image_idx=index)
                    #     found_image = found_images[0]
                    #     new_location = models.ImageLocation(image=found_image, location=line)
                    #     writable_objects.append(new_location)
                    # except:
                    #     print 'No image for {} {} {} {} {} {}'.format(book_id, volume, page, index, filepath_split[-2], line)

                    new_location = models.ImageLocation(
                        location=line.strip(),
                        book_id=book_id,
                        volume=volume,
                        page=page,
                        idx=index
                    )
                    writable_objects.append(new_location)

                    if len(writable_objects) > 100:
                        counter += len(writable_objects)
                        print 'writing to db - (' + str(len(writable_objects)) + \
                              ' lines) (' + str(counter) + ' total) (file_name ' + size + ')'
                        models.ImageLocation.objects.bulk_create(writable_objects)
                        writable_objects = []

                if len(writable_objects) > 0:
                    counter += len(writable_objects)
                    print 'writing to db - (' + str(len(writable_objects)) + \
                          ' lines) (' + str(counter) + ' total) (file_name ' + size + ')'
                    models.ImageLocation.objects.bulk_create(writable_objects)
                    writable_objects = []


def load_scratch_to_db(sizes):
    print 'db'

    root_folder = '/scratch/lost-visions/images-found/'

    # sizes = ['embellishments', 'medium', 'plates', 'covers']
    if 'embellishments' in sizes:
        # embellishments folder
        embellishment_path = os.path.join(root_folder, 'embellishments')
        for year_folder in os.listdir(embellishment_path):
            year_folder_path = os.path.join(embellishment_path, year_folder)

            writable_objects = []
            for embellishment_file in os.listdir(year_folder_path):
                filename_split = embellishment_file.split('_')

                book_id = filename_split[0]
                volume = filename_split[1]
                page = filename_split[2]
                index = filename_split[3]

                full_path = str(os.path.join(year_folder_path, embellishment_file))
                # save_location(book_id, volume, page, index, year_folder, full_path)
                found_images = models.Image.objects.filter(
                    book_identifier=book_id,
                    volume=volume,
                    page=page,
                    image_idx=index)
                if found_images.count() > 0:
                    found_image = found_images[0]
                    new_location = models.ImageLocation(image=found_image, location=full_path)
                    writable_objects.append(new_location)
                else :
                    print 'No image for {} {} {} {} {} {}'.format(book_id, volume, page, index, year_folder, full_path)

                if len(writable_objects) > 100:
                    models.ImageLocation.objects.bulk_create(writable_objects)
                    writable_objects = []

            if len(writable_objects) > 0:
                models.ImageLocation.objects.bulk_create(writable_objects)
                writable_objects = []

    if 'medium' in sizes:
        # medium sized images folder
        medium_path = os.path.join(root_folder, 'medium')
        for year_folder in os.listdir(medium_path):
            year_folder_path = os.path.join(medium_path, year_folder)
            for medium_file in os.listdir(year_folder_path):
                filename_split = medium_file.split('_')

                book_id = filename_split[0]
                volume = filename_split[1]
                page = filename_split[2]
                index = filename_split[3]

                full_path = str(os.path.join(year_folder_path, medium_file))
                save_location(book_id, volume, page, index, year_folder, full_path)

    if 'plates' in sizes:
        #     plate sized images folder
        plates_path = os.path.join(root_folder, 'plates')
        for year_folder in os.listdir(plates_path):
            year_folder_path = os.path.join(plates_path, year_folder)
            for plates_file in os.listdir(year_folder_path):
                filename_split = plates_file.split('_')

                book_id = filename_split[0]
                volume = filename_split[1]
                page = filename_split[2]
                index = filename_split[3]

                full_path = str(os.path.join(year_folder_path, plates_file))
                save_location(book_id, volume, page, index, year_folder, full_path)

    if 'covers' in sizes:
        # cover sized image folder
        covers_path = os.path.join(root_folder, 'covers')
        for year_folder in os.listdir(covers_path):
            year_folder_path = os.path.join(covers_path, year_folder)
            for covers_file in os.listdir(year_folder_path):
                filename_split = covers_file.split('_')

                book_id = filename_split[0]
                volume = filename_split[1]
                page = filename_split[2]
                index = filename_split[3]

                full_path = str(os.path.join(year_folder_path, covers_file))
                save_location(book_id, volume, page, index, year_folder, full_path)


# sizes = ['embellishments', 'medium', 'plates', 'covers']
sizes = ['embellishments']

# load_scratch_to_db(['embellishments'])
make_file_list(sizes)
db_from_file(sizes)