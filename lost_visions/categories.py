import json
from crowdsource.settings import STATIC_URL

__author__ = 'ubuntu'

ICON_URL = STATIC_URL + 'media/images/icon/'


class Category():
    def __init__(self, category_id, name, text, img):
        self.img = img
        self.text = text
        self.category_id = category_id
        self.name = name
        self.question = ''
        self.answer_ids = []
        self.should_save = True

    def set_question(self, text):
        self.question = text
        return self

    def set_answers(self, answer_id_array):
        self.answer_ids = answer_id_array
        return self

    def set_save(self, save):
        self.should_save = save
        return self


class CategoryManager():
    def __init__(self):
        self.categories = dict()
        self.load_defaults()

    def load_defaults(self):

        self.categories[0] = Category('0', 'yes', 'Yes', ICON_URL + 'tick.png').set_save(False)
        self.categories[1] = Category('1', 'no', 'No', ICON_URL + 'cross.png').set_save(False)

        self.categories[0] = Category('-1', 'root', 'Root', '')\
            .set_question('Is the image a ...')\
            .set_answers([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300])\
            .set_save(False)

        self.categories[100] = Category('100', 'advert', 'Advertisements?', ICON_URL + 'advert.jpg') \
            .set_question('Is there a product/brand name?') \
            .set_answers([101, 102])
        self.categories[101] = Category('101', 'yes', 'Yes', ICON_URL + 'tick.png').set_save(False)
        self.categories[102] = Category('102', 'no', 'No', ICON_URL + 'cross.png').set_save(False)

        self.categories[200] = Category('200', 'building', 'Building?', ICON_URL + 'building.jpg', ) \
            .set_question('Is this the buildings ...') \
            .set_answers([201, 202, 203])
        self.categories[201] = Category('201', 'interior', 'Interior?', ICON_URL + 'interior.jpg')
        self.categories[202] = Category('202', 'exterior', 'Exterior?', ICON_URL + 'exterior.jpg')
        self.categories[203] = Category('203', 'architectural', 'Architectural Drawing?', ICON_URL + 'schematic.jpg')

        self.categories[300] = Category('300', 'people', 'People?', ICON_URL + 'people.jpg') \
            .set_question('Is this image of an ...').set_answers([301, 302])
        self.categories[301] = Category('301', 'individual', 'Individual?', ICON_URL + 'lv-rect-station.png') \
            .set_question('Is this a named historical figure?').set_answers([311, 312])
        self.categories[302] = Category('302', 'group', 'Group?', ICON_URL + 'lv-rect-station.png') \
            .set_question('Are there any named historical figures?').set_answers([321, 322])

        self.categories[311] = Category('311', 'no', 'No', ICON_URL + 'cross.png') \
            .set_question('Any Activities?').set_answers([321, 322]).set_save(False)
        self.categories[312] = Category('312', 'add', 'Add', ICON_URL + 'tick.png') \
            .set_question('Any Activities?').set_answers([321, 322]).set_save(False)
        self.categories[321] = Category('321', 'yes', 'Yes', ICON_URL + 'tick.png').set_save(False)
        self.categories[322] = Category('322', 'no', 'No', ICON_URL + 'cross.png').set_save(False)

        self.categories[400] = Category('400', 'motif', 'Decoration?', ICON_URL + 'motif.jpg')\
            .set_question('Is the decoration a ...').set_answers([401, 402, 403, 404, 405])
        self.categories[401] = Category('401', 'border', 'Border?', ICON_URL + 'border.jpg')
        self.categories[402] = Category('402', 'emblem', 'Emblem?', ICON_URL + 'lv-rect-station.png')
        self.categories[403] = Category('403', 'motif', 'Motif?', ICON_URL + 'motif.jpg')
        self.categories[404] = Category('404', 'coat_of_arms', 'Coat of Arms?', ICON_URL + 'coat_of_arms.jpg')
        self.categories[405] = Category('405', 'decorative letter', 'Decorative Letter?', ICON_URL + 'letter.jpg')

        self.categories[500] = Category('500', 'title_page', 'Title Page?', ICON_URL + 'title_page.jpg')

        self.categories[600] = Category('600', 'map', 'Map?', ICON_URL + 'map.jpg')

        self.categories[700] = Category('700', 'natural_world', 'Natural World?', ICON_URL + 'nature.jpg')\
            .set_question('Is the image of an ...').set_answers([701, 702, 703])

        self.categories[701] = Category('701', 'animal', 'Animal?', ICON_URL + 'animal.jpg')
        self.categories[702] = Category('702', 'vegetable', 'Vegetable?', ICON_URL + 'lv-rect-station.png')
        self.categories[703] = Category('703', 'mineral', 'Mineral?', ICON_URL + 'lv-rect-station.png')

        self.categories[800] = Category('800', 'scientific_drawing', 'Scientific Drawing?', ICON_URL + 'science.jpg') \
            .set_question('Is the Diagram ...') \
            .set_answers([801, 802, 803, 804, 805, 806])
        self.categories[801] = Category('801', 'Geological', 'Geological?', ICON_URL + 'lv-rect-station.png')
        self.categories[802] = Category('802', 'Medical', 'Medical?', ICON_URL + 'lv-rect-station.png')
        self.categories[803] = Category('803', 'Engineering', 'Engineering?', ICON_URL + 'lv-rect-station.png')
        self.categories[804] = Category('804', 'Botanical', 'Botanical?', ICON_URL + 'lv-rect-station.png')
        self.categories[805] = Category('805', 'Zoological', 'Zoological?', ICON_URL + 'lv-rect-station.png')
        self.categories[806] = Category('806', 'Archaeological', 'Archaeological?', ICON_URL + 'lv-rect-station.png')

        self.categories[900] = Category('900', 'music', 'Musical Score?', ICON_URL + 'music.jpg')

        self.categories[1000] = Category('1000', 'landscape', 'Landscape?', ICON_URL + 'landscape.jpg')
        self.categories[1100] = Category('1100', 'portrait', 'Portrait?', ICON_URL + 'portrait.jpg')

        self.categories[1200] = Category('1200', 'ethnographic', 'Travel/ Ethnography?', ICON_URL + 'travel.jpg')

        self.categories[1300] = Category('1300', 'words', 'Handwritten Text?', ICON_URL + 'words.jpg')

    def get_tag_for_category_id(self, category_id):
        category = self.categories.get(int(category_id))
        if category.should_save:
            return category.name
        else:
            return None

    def get_category_data(self, cat_id):
        parent_category = self.categories.get(int(cat_id))
        answer_categories = []
        if len(parent_category.answer_ids) == 0:
            parent_category = self.categories.get(0)
        for child_id in parent_category.answer_ids:
            child_category = self.categories.get(child_id)
            answer_categories.append({'name': child_category.name,
                                      'id': child_category.category_id,
                                      'text': child_category.text,
                                      'img': child_category.img})
        return {'question': parent_category.question, 'answers': answer_categories}