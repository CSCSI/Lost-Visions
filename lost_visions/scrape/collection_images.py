import json

import requests


def scrape():

    all_ids = []
    with open('id_file.txt', 'a') as id_file:
        for i in range(1, 799):
            page = requests.get('http://lost-visions.cf.ac.uk/view_collection/102/{}'.format(i))
            ids = page.text.split('var all_image_ids = "')[1].split('";')[0].split(',')

            print i
            print ids

            all_ids.extend(ids)
            id_file.write('{}\n'.format(ids))

    with open('all_id_file.txt', 'w') as all_id_file:
        all_id_file.write(str(all_ids))


def grab():
    next_id = 11096666854
    image_data_text = requests.get('http://lost-visions.cf.ac.uk/image_data/{}'.format(next_id))
    image_data = json.loads(image_data_text.text)

    volume = image_data['bl_flickr_data'][0]['fields']['volume']
    page = image_data['bl_flickr_data'][0]['fields']['page']

    print page, volume

    for a in image_data['image_location']:
        if a['fields']['page'] == page:
            if a['fields']['volume'] == volume:
                next_url = a['fields']['location']
                next_url = next_url.replace(
                    '/scratch/lost-visions/images-found/',
                    '/static/media/found/'
                )
                next_url = 'http://lost-visions.cf.ac.uk{}'.format(next_url)

                print next_url

if __name__ == '__main__':
    grab()