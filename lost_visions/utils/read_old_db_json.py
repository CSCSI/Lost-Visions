import json
import os
from crowdsource import settings
from lost_visions import models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")

__author__ = 'ubuntu'


def read_json_dbdump(full_path):

    all_things = dict()
    all_things['imagetext'] = []
    all_things['tag'] = []
    all_things['geotag'] = []
    all_things['searchquery'] = []
    all_things['savedimages'] = []

    ignore = ['contenttypes.contenttype',
              'sessions.session',
              'lost_visions.book',
              'lost_visions.bookillustrator',
              'socialaccount.socialaccount',
              'lost_vivions.lostvisionsuser',
              'auth.permission'
    ]
    with open(full_path) as f:
        for i, line in enumerate(f):
            # print line
            # whole_mess = ast.literal_eval(line)
            whole_mess = json.loads(line)
            for obj in whole_mess:
                for thing in obj:
                    if obj['model'] not in ignore:
                        if obj['model'] == 'lost_visions.imagetext':
                            img = dict()
                            img['caption'] = obj['fields']['caption']
                            img['flickr_id'] = models.Image.objects.get(id=obj['fields']['image']).flickr_id
                            user_id = obj['fields']['user']
                            try:
                                # user_object = models.LostVisionUser.objects.get(id=user_id)
                                img['user'] = user_id
                            except:
                                pass

                            img['ts'] = obj['fields']['timestamp']
                            img['description'] = obj['fields']['description']
                            all_things['imagetext'].append(img)

                        elif obj['model'] == 'lost_visions.tag':
                            tag = dict()
                            tag['tag'] = obj['fields']['tag']
                            tag['flickr_id'] = models.Image.objects.get(id=obj['fields']['image']).flickr_id
                            user_id = obj['fields']['user']
                            try:
                                # user_object = models.LostVisionUser.objects.get(id=user_id)
                                tag['user'] = user_id
                            except:
                                pass

                            tag['ts'] = obj['fields']['timestamp']
                            tag['y_percent'] = obj['fields']['y_percent']
                            tag['x_percent'] = obj['fields']['x_percent']
                            tag['tag_order'] = obj['fields']['tag_order']
                            all_things['tag'].append(tag)

                        elif obj['model'] == 'lost_visions.geotag':
                            geotag = dict()
                            geotag['flickr_id'] = models.Image.objects.get(id=obj['fields']['image']).flickr_id
                            user_id = obj['fields']['user']
                            try:
                                # user_object = models.LostVisionUser.objects.get(id=user_id)
                                geotag['user'] = user_id
                            except:
                                pass

                            geotag['ts'] = obj['fields']['timestamp']
                            geotag['north_east_x'] = obj['fields']['north_east_x']
                            geotag['north_east_y'] = obj['fields']['north_east_y']
                            geotag['south_west_x'] = obj['fields']['south_west_x']
                            geotag['south_west_y'] = obj['fields']['south_west_y']
                            geotag['tag_order'] = obj['fields']['tag_order']
                            all_things['geotag'].append(geotag)

                        elif obj['model'] == 'lost_visions.searchquery':
                            searchquery = dict()
                            user_id = obj['fields']['user']
                            try:
                                # user_object = models.LostVisionUser.objects.get(id=user_id)
                                searchquery['user'] = user_id
                            except:
                                pass

                            searchquery['search_term'] = obj['fields']['search_term']
                            all_things['searchquery'].append(searchquery)

                        elif obj['model'] == 'lost_visions.savedimages':
                            savedimages = dict()
                            user_id = obj['fields']['user']
                            try:
                                print user_id
                                # user_object = models.LostVisionUser.objects.get(id=user_id)
                                savedimages['user'] = user_id
                            except Exception as e:
                                print e
                                pass

                            savedimages['flickr_id'] = models.Image.objects.get(id=obj['fields']['image']).flickr_id
                            savedimages['ts'] = obj['fields']['timestamp']

                            all_things['savedimages'].append(savedimages)

                        else:
                            print '*'
                            # print obj['model']
    with open('/home/ubuntu/dumped.json', 'a') as dump_file:
        dump_file.write(json.dumps(all_things))


def read_cleaned_json(full_path):
    with open(full_path) as f:
        for i, line in enumerate(f):
            all_things = json.loads(line)
            for obj in all_things['imagetext']:
                print obj
                img_text = models.ImageText()
                img_text.timestamp = obj['ts']
                img_text.description = obj['description']
                img_text.caption = obj['caption']
                img_text.image = models.Image.objects.get(flickr_id=obj['flickr_id'])

                try:
                    user_object = models.LostVisionUser.objects.get(id=obj['user'])
                    img_text.user = user_object
                except Exception as e:
                    print e
                    pass
                img_text.save()

            for obj in all_things['tag']:
                print obj
                tag_object = models.Tag()
                tag_object.tag = obj['tag']
                tag_object.image = models.Image.objects.get(flickr_id=obj['flickr_id'])
                try:
                    user_id = obj['user']
                    tag_object.user = models.LostVisionUser.objects.get(id=user_id)
                except Exception as e:
                    print e
                    pass

                tag_object.timestamp = obj['ts']
                tag_object.y_percent = obj['y_percent']
                tag_object.x_percent = obj['x_percent']
                tag_object.tag_order = obj['tag_order']
                tag_object.save()

            for obj in all_things['geotag']:
                print obj
                geo_object = models.GeoTag()
                geo_object.image = models.Image.objects.get(flickr_id=obj['flickr_id'])
                user_id = obj['user']
                try:
                    geo_object.user = models.LostVisionUser.objects.get(id=user_id)
                except Exception as e:
                    print e
                    pass

                geo_object.timestamp = obj['ts']
                geo_object.north_east_x = obj['north_east_x']
                geo_object.north_east_y = obj['north_east_y']
                geo_object.south_west_x = obj['south_west_x']
                geo_object.south_west_y = obj['south_west_y']
                geo_object.tag_order = obj['tag_order']
                geo_object.save()

            for obj in all_things['searchquery']:
                print obj
                search_object = models.SearchQuery()
                user_id = obj['user']
                try:
                    search_object.user = models.LostVisionUser.objects.get(id=user_id)
                except Exception as e:
                    print e
                    pass

                search_object.timestamp = obj['ts']
                search_object.search_term = obj['search_term']
                search_object.save()

            for obj in all_things['savedimages']:
                print obj
                saved_object = models.SavedImages()
                saved_object.image = models.Image.objects.get(flickr_id=obj['flickr_id'])
                user_id = obj['user']
                try:
                    saved_object.user = models.LostVisionUser.objects.get(id=user_id)
                except Exception as e:
                    print e
                    pass
                saved_object.save()


read_json_dbdump(settings.db_json_location)
read_cleaned_json(settings.db_cleaned_json_location)