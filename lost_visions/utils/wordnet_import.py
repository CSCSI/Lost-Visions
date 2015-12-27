import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowdsource.settings")
from lost_visions import wordnet, models

__author__ = 'ubuntu'

def copy_words():

    # query = "SELECT wordid, lemma FROM words"

    results = wordnet.Words.objects.using('wordnet').all()

    # print type(results), results

    all_words = []

    for res in results:

        word = models.Words()
        word.wordid = res.wordid
        word.lemma = res.lemma
        all_words.append(word)

    models.Words.objects.bulk_create(all_words, batch_size=200)

def copy_senses():

    query = "SELECT * FROM senses"

    results = wordnet.Words.objects.db_manager('wordnet').raw(query, [])
    all_senses = []

    for res in results:

        sense = models.Senses()
        sense.wordid = res.wordid
        sense.casedwordid = res.casedwordid
        sense.synsetid = res.synsetid
        sense.senseid = res.senseid
        sense.sensenum = res.sensenum
        sense.lexid = res.lexid
        sense.tagcount = res.tagcount
        sense.sensekey = res.sensekey

        all_senses.append(sense)

    models.Senses.objects.bulk_create(all_senses)

def copy_synsets():

    query = "SELECT synsetid, pos, lexdomainid, definition FROM synsets"

    results = wordnet.Synsets.objects.db_manager('wordnet').raw(query, [])
    all_synsets = []

    for res in results:

        synset = models.Synsets()
        synset.synsetid = res.synsetid
        synset.pos = res.pos
        synset.lexdomainid = res.lexdomainid
        synset.definition = res.definition

        all_synsets.append(synset)

    models.Synsets.objects.bulk_create(all_synsets)

copy_words()
copy_senses()
copy_synsets()
