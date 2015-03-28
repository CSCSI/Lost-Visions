import json
from django.core.urlresolvers import reverse
from raven import Client
from crowdsource.settings import STATIC_URL #RAVEN_CONFIG

__author__ = 'ubuntu'

ICON_URL = STATIC_URL + 'media/images/icon/'
NEW_DESIGN_URL = STATIC_URL + 'media/images/new_design/'
MIKEY_URL = NEW_DESIGN_URL + 'mikey/'

# ADVERT_BUTTON_IMAGE_URL = NEW_DESIGN_URL + 'TagImages_Categories_Advertisement.png'
# BUILDING_BUTTON_IMAGE_URL = NEW_DESIGN_URL + 'TagImages_Categories_Building.png'
# PORTRAIT_BUTTON_IMAGE_URL = NEW_DESIGN_URL + 'TagImages_Categories_Portrait.png'
#
# DECORATION_BUTTON_IMAGE_URL = NEW_DESIGN_URL + 'TagImages_Categories_Decoration.png'
# TITLE_PAGE_BUTTON_IMAGE_URL = NEW_DESIGN_URL + 'TagImages_Categories_TitlePage.png'
# MAP_BUTTON_IMAGE_URL = NEW_DESIGN_URL + 'TagImages_Categories_Map.png'
#
# SCIENTIFIC_BUTTON_IMAGE_URL = NEW_DESIGN_URL + 'TagImages_Categories_Scientific.png'
# LOCATION_BUTTON_IMAGE_URL = NEW_DESIGN_URL + 'TagImages_Categories_Location.png'
# LITERATURE_BUTTON_IMAGE_URL = NEW_DESIGN_URL + 'TagImages_Categories_Literature.png'

ADVERT_BUTTON_IMAGE_URL = MIKEY_URL + "advert.jpg"
BUILDING_BUTTON_IMAGE_URL = MIKEY_URL + "building.jpg"
PORTRAIT_BUTTON_IMAGE_URL = MIKEY_URL + "portrait.jpg"

DECORATION_BUTTON_IMAGE_URL = MIKEY_URL + "decoration.jpg"
TITLE_PAGE_BUTTON_IMAGE_URL = MIKEY_URL + "title page.jpg"
MAP_BUTTON_IMAGE_URL = MIKEY_URL + "a map.jpg"

SCIENTIFIC_BUTTON_IMAGE_URL = MIKEY_URL + "scientific.jpg"
LOCATION_BUTTON_IMAGE_URL = MIKEY_URL + "location.jpg"
LITERATURE_BUTTON_IMAGE_URL = MIKEY_URL + "literature.jpg"

YES_BUTTON_URL = MIKEY_URL + "yes button.jpg"
NO_BUTTON_URL = MIKEY_URL + "No button.jpg"

ARCHAEOLOGICAL_BUTTON_URL = MIKEY_URL + "archaeological.jpg"
ARCHITECTURAL_BUTTON_URL = MIKEY_URL + "architecturaldrawing.jpg"
BOTANICAL_BUTTON_URL = MIKEY_URL + "botanical.jpg"
BYNAME_BUTTON_URL = MIKEY_URL + "byname.jpg"
ENGINEERING_BUTTON_URL = MIKEY_URL + "engineering.jpg"
GEOLOGICAL_BUTTON_URL = MIKEY_URL + "geological.jpg"
MEDICAL_BUTTON_URL = MIKEY_URL + "medical.jpg"
ON_A_MAP_BUTTON_URL = MIKEY_URL + "onamap.jpg"
ZOOLOGICAL_BUTTON_URL = MIKEY_URL + "zoological.jpg"
NONE_OF_THESE_BUTTON_URL = MIKEY_URL + "noneofthesenew.jpg"

NOVEL_BUTTON_URL = MIKEY_URL + "a novel.jpg"
PLAY_BUTTON_URL = MIKEY_URL + "A play.jpg"
POEM_BUTTON_URL = MIKEY_URL + "poem1.jpg"

BACK_BUTTON_URL = MIKEY_URL + "back.jpg"
COAT_OF_ARMS_BUTTON_URL = MIKEY_URL + "coatofarms.jpg"
DECORATIVE_BORDER_BUTTON_URL = MIKEY_URL + "decorative border.jpg"
DECORATIVE_MOTIF_BUTTON_URL = MIKEY_URL + "decorativeletter.jpg"
DECORATIVE_LETTER_BUTTON_URL = MIKEY_URL + "decorativemotif.jpg"


class Category():
    def __init__(self, category_id, name, text, img):
        self.img = img
        self.text = text
        self.category_id = category_id
        self.name = name
        self.question = ''
        self.answer_ids = []
        self.should_save = True
        self.action_name = ''
        self.synset = ''

    def set_question(self, text):
        self.question = text
        return self

    def set_answers(self, answer_id_array):
        self.answer_ids = answer_id_array
        return self

    def set_save(self, save):
        self.should_save = save
        return self

    def set_action(self, action_name):
        self.action_name = action_name
        return self

    def set_synset(self, synset):
        self.synset = synset
        return self


class Action():
    def __init__(self, name, link='', question='', type=''):
        self.name = name
        self.link = link
        self.question = question
        self.type = type

    def __unicode__(self):
        return u'' + self.name + ' ' + self.link

    def __str__(self):
        return self.name + ':' + self.link

    def __repr__(self):
        return self.name + ':' + self.link


class CategoryManager():
    def __init__(self):
        self.categories = dict()
        self.actions = dict()
        self.load_default_categories()

    def update_image_actions(self, image_id):
        link = reverse('image.map', kwargs={'image_id': image_id})

        self.actions['map'] = Action('map', link=link, type='map')
        self.actions['gazetteer'] = Action('gazetteer', link=link)
        self.actions['person_name_entry'] = Action('person_name_entry',
                                                   question='If you can, please name the person',
                                                   type='text_entry')
        self.actions['product_name_entry'] = Action('product_name_entry',
                                                    question='If you can, please name the product being advertised',
                                                    type='text_entry')
        self.actions['building_name_entry'] = Action('building_name_entry',
                                                     question='If you can, please name the building or type of building',
                                                     type='text_entry')


    def load_default_categories(self):

        self.categories[0] = Category('0', 'yes', '', YES_BUTTON_URL).set_save(False)
        self.categories[1] = Category('1', 'no', '', NO_BUTTON_URL).set_save(False)

        self.categories[0] = Category('-1', 'root', 'Root', '') \
            .set_question('Is the illustration:') \
            .set_answers([100, 200, 303, 400, 500, 600, 800, 1000, 1100]) \
            .set_save(False)

        self.categories[100] = Category('100', 'advert', '', ADVERT_BUTTON_IMAGE_URL).set_synset('advert.n.1')
            # .set_question('Is there a product/brand name?') \
            # .set_answers([101, 102])
        self.categories[101] = Category('101', 'yes', '', YES_BUTTON_URL) \
            .set_save(False).set_action('product_name_entry')
        self.categories[102] = Category('102', 'no', '', NO_BUTTON_URL).set_save(False)

        self.categories[200] = Category('200', 'building', '', BUILDING_BUTTON_IMAGE_URL).set_synset('building.n.1')
            # .set_answers([203, 204])
        # self.categories[201] = Category('201', 'interior', 'Interior?', ICON_URL + 'interior.jpg')
        # self.categories[202] = Category('202', 'exterior', 'Exterior?', ICON_URL + 'exterior.jpg')
        # self.categories[203] = Category('203', 'save', "", YES_BUTTON_URL) \
        #     .set_save(False).set_action('building_name_entry')
        # self.categories[204] = Category('204', 'dont_know', "", NO_BUTTON_URL).set_save(False)

        # self.categories[300] = Category('300', 'people', 'People?', ICON_URL + 'people.jpg') \
        #     .set_question('Is this image of an ...').set_answers([301, 302, 303])
        # self.categories[301] = Category('301', 'individual', 'Individual?', ICON_URL + 'lv-rect-station.png') \
        #     .set_question('Is this a named historical figure?').set_answers([311, 312])
        # self.categories[302] = Category('302', 'group', 'Group?', ICON_URL + 'lv-rect-station.png') \
        #     .set_question('Are there any named historical figures?').set_answers([321, 322])
        self.categories[303] = Category('303', 'portrait', '', PORTRAIT_BUTTON_IMAGE_URL).set_synset('portrait.n.2')
            # .set_answers([304, 305])
        # self.categories[304] = Category('304', "dont_know", "", NO_BUTTON_URL).set_save(False)
        # self.categories[305] = Category('305', 'named_person', "", YES_BUTTON_URL).set_action('person_name_entry')

        self.categories[311] = Category('311', 'no', 'No', NO_BUTTON_URL) \
            .set_question('Any Activities?').set_answers([321, 322]).set_save(False)
        self.categories[312] = Category('312', 'add', 'Add', YES_BUTTON_URL) \
            .set_question('Any Activities?').set_answers([321, 322]).set_save(False)
        self.categories[321] = Category('321', 'yes', 'Yes', YES_BUTTON_URL).set_save(False)
        self.categories[322] = Category('322', 'no', 'No', NO_BUTTON_URL) \
            .set_save(False).set_question('Is the person in a named location?').set_answers([1000, 1])

        # MOTIF

        self.categories[400] = Category('400', 'decoration', '', DECORATION_BUTTON_IMAGE_URL) \
            .set_question('Is the decoration a ...').set_answers([401, 403, 404, 405, 406]).set_synset('decoration.n.1')
        self.categories[401] = Category('401', 'border', '', DECORATIVE_BORDER_BUTTON_URL)\
            .set_synset('border.n.5')
        # self.categories[402] = Category('402', 'emblem', 'Emblem?', ICON_URL + 'lv-rect-station.png')
        self.categories[403] = Category('403', 'motif', '', DECORATIVE_MOTIF_BUTTON_URL)\
            .set_synset('motif.n.1')
        self.categories[404] = Category('404', 'coat_of_arms', '', COAT_OF_ARMS_BUTTON_URL)\
            .set_synset('coat of arms.n.1')
        self.categories[405] = Category('405', 'decorative letter', '', DECORATIVE_LETTER_BUTTON_URL)
        self.categories[406] = Category('406', 'no', '', NONE_OF_THESE_BUTTON_URL).set_save(False)

        self.categories[500] = Category('500', 'title_page', '', TITLE_PAGE_BUTTON_IMAGE_URL).set_synset('title page.n.1')

        # self.categories[700] = Category('700', 'natural_world', 'Natural World?', ICON_URL + 'nature.jpg')\
        #     .set_question('Is the image of an ...').set_answers([701, 702, 703])

        # self.categories[701] = Category('701', 'animal', 'Animal?', ICON_URL + 'animal.jpg')
        # self.categories[702] = Category('702', 'vegetable', 'Vegetable?', ICON_URL + 'lv-rect-station.png')
        # self.categories[703] = Category('703', 'mineral', 'Mineral?', ICON_URL + 'lv-rect-station.png')

        self.categories[800] = Category('800', 'scientific_drawing', '', SCIENTIFIC_BUTTON_IMAGE_URL) \
            .set_question('Is the illustration ...').set_synset('diagram.n.1') \
            .set_answers([801, 802, 803, 804, 805, 806, 807, 808])
        self.categories[801] = Category('801', 'Geological', '', GEOLOGICAL_BUTTON_URL).set_synset('geology.n.1') \
            .set_question('If you can, please name the geological location').set_answers([1001, 1002])
        # self.categories[810] = Category('810', 'yes', '', YES_BUTTON_URL).set_save(False).set_answers([1000])

        self.categories[802] = Category('802', 'Medical', '', MEDICAL_BUTTON_URL).set_synset('medical.a.1')
        self.categories[803] = Category('803', 'Engineering', '', ENGINEERING_BUTTON_URL).set_synset('engineering.n.2')
        self.categories[804] = Category('804', 'Botanical', '', BOTANICAL_BUTTON_URL).set_synset('botany.n.2')
        self.categories[805] = Category('805', 'Zoological', '', ZOOLOGICAL_BUTTON_URL).set_synset('zoology.n.2')
        self.categories[806] = Category('806', 'Archaeological', '', ARCHAEOLOGICAL_BUTTON_URL).set_synset('archaeology.n.1') \
            .set_question('Is the archaeological illustration of a named location?').set_answers([1001, 1002])
        # self.categories[816] = Category('810', 'yes', '', YES_BUTTON_URL).set_save(False).set_answers([1000])

        self.categories[807] = Category('807', 'Architectural', '', ARCHITECTURAL_BUTTON_URL).set_synset('architecture.n.2') \
            .set_question('If you can, please name the location of the architectural illustration').set_answers([1001, 1002])
        # self.categories[817] = Category('810', 'yes', '', YES_BUTTON_URL).set_save(False).set_answers([1000])
        self.categories[808] = Category('808', 'no', '', NONE_OF_THESE_BUTTON_URL).set_save(False)

        # self.categories[900] = Category('900', 'music', 'Musical Score?', ICON_URL + 'music.jpg')

        self.categories[600] = Category('600', 'map', '', MAP_BUTTON_IMAGE_URL).set_synset('map.n.1') \
            .set_question('If you can, please name the mapped location')\
            .set_answers([1001, 1002]).set_synset('map.n.1')

        self.categories[1000] = Category('1000', 'location', '', LOCATION_BUTTON_IMAGE_URL) \
            .set_save(False).set_question('If you can, please name the location').set_answers([1001, 1002])

        # self.categories[1200] = Category('1200', 'ethnographic', 'Travel/ Ethnography?', ICON_URL + 'travel.jpg')
        # self.categories[1300] = Category('1300', 'words', 'Handwritten Text?', ICON_URL + 'words.jpg')

        self.categories[1001] = Category('1001', 'Name', '', BYNAME_BUTTON_URL)\
            .set_action('gazetteer').set_save(False).set_answers([1003, 1004])
        self.categories[1002] = Category('1002', 'Map', '', ON_A_MAP_BUTTON_URL)\
            .set_save(False).set_action('map').set_answers([1004])
        self.categories[1003] = Category('1003', 'save', '', ICON_URL + 'tick.png').set_save(False)
        self.categories[1004] = Category('1004', 'back', '', BACK_BUTTON_URL).set_save(False)

        self.categories[1100] = Category('1100', 'literature', '', LITERATURE_BUTTON_IMAGE_URL) \
            .set_save(True).set_synset('literature.n.3')\
            .set_question('Does this illustrate...').set_answers([1101, 1102, 1103, 406])
        self.categories[1101] = Category('1101', 'poem', '', POEM_BUTTON_URL).set_synset('poetry.n.2')
        self.categories[1102] = Category('1102', 'play', '', PLAY_BUTTON_URL).set_synset('play.n.2')
        self.categories[1103] = Category('1103', 'novel', '', NOVEL_BUTTON_URL).set_synset('novel.n.1')

    def get_tag_for_category_id(self, category_id):
        try:
            category = self.categories.get(int(category_id), 0)
            if category.should_save:
                return category.name
            else:
                return None
        except:
            # client = Client(RAVEN_CONFIG['dsn'])
            # client.tags = {'category id': category_id}
            # client.captureException()
            pass

    def get_category_data(self, cat_id):
        root = False
        move_on = False

        # If the category doesn't have any children return children for root
        parent_category = self.categories.get(int(cat_id))

        if len(parent_category.answer_ids) == 0:
            move_on = True

        answer_categories = []
        actions = []
        if parent_category is None or len(parent_category.answer_ids) == 0 or int(cat_id) == 0:
            parent_category = self.categories.get(0)
            root = True

        # build child categories and actions for the parent category
        for child_id in parent_category.answer_ids:
            child_category = self.categories.get(child_id)
            try:
                if child_category.action_name is '':

                    answer_categories.append({'name': child_category.name,
                                              'save': child_category.should_save,
                                              'synset': child_category.synset,
                                              'id': child_category.category_id,
                                              'text': child_category.text,
                                              'img': child_category.img})
                else:
                    action = self.actions.get(child_category.action_name)
                    actions.append({'name': child_category.name,
                                    'id': child_category.category_id,
                                    'save': child_category.should_save,
                                    'synset': child_category.synset,
                                    'text': child_category.text,
                                    'img': child_category.img,
                                    'link': action.link,
                                    'action': action.name,
                                    'question': action.question,
                                    'type': action.type
                    })

            except:
                # client = Client(RAVEN_CONFIG['dsn'])
                # client.tags = {'child id': child_id}
                # client.captureException()
                pass
        # We return the question from the parent category
        # if click Person, and get asked "name the person"
        return {'question': parent_category.question,
                'answers': answer_categories,
                'actions': actions,
                'next_question': move_on,
                'root': root}
