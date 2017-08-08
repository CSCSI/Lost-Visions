# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class Adjpositions(models.Model):
    synsetid = models.IntegerField(primary_key=True)
    wordid = models.IntegerField(primary_key=True)
    position = models.TextField() # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'adjpositions'

class Adjpositiontypes(models.Model):
    position = models.TextField(unique=True) # This field type is a guess.
    positionname = models.CharField(max_length=24)
    class Meta:
        managed = False
        db_table = 'adjpositiontypes'

class Bncconvtasks(models.Model):
    wordid = models.IntegerField(primary_key=True)
    pos = models.TextField(primary_key=True, blank=True) # This field type is a guess.
    freq1 = models.IntegerField(blank=True, null=True)
    range1 = models.SmallIntegerField(blank=True, null=True)
    disp1 = models.TextField(blank=True) # This field type is a guess.
    freq2 = models.IntegerField(blank=True, null=True)
    range2 = models.SmallIntegerField(blank=True, null=True)
    disp2 = models.TextField(blank=True) # This field type is a guess.
    ll = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'bncconvtasks'

class Bncimaginfs(models.Model):
    wordid = models.IntegerField(primary_key=True)
    pos = models.TextField(primary_key=True, blank=True) # This field type is a guess.
    freq1 = models.IntegerField(blank=True, null=True)
    range1 = models.SmallIntegerField(blank=True, null=True)
    disp1 = models.TextField(blank=True) # This field type is a guess.
    freq2 = models.IntegerField(blank=True, null=True)
    range2 = models.SmallIntegerField(blank=True, null=True)
    disp2 = models.TextField(blank=True) # This field type is a guess.
    ll = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'bncimaginfs'

class Bncs(models.Model):
    wordid = models.IntegerField(primary_key=True)
    pos = models.TextField(primary_key=True, blank=True) # This field type is a guess.
    freq = models.IntegerField(blank=True, null=True)
    range = models.SmallIntegerField(blank=True, null=True)
    disp = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'bncs'

class Bncspwrs(models.Model):
    wordid = models.IntegerField(primary_key=True)
    pos = models.TextField(primary_key=True, blank=True) # This field type is a guess.
    freq1 = models.IntegerField(blank=True, null=True)
    range1 = models.SmallIntegerField(blank=True, null=True)
    disp1 = models.TextField(blank=True) # This field type is a guess.
    freq2 = models.IntegerField(blank=True, null=True)
    range2 = models.SmallIntegerField(blank=True, null=True)
    disp2 = models.TextField(blank=True) # This field type is a guess.
    ll = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'bncspwrs'

class Casedwords(models.Model):
    casedwordid = models.IntegerField(primary_key=True)
    wordid = models.IntegerField()
    cased = models.CharField(max_length=80)
    class Meta:
        managed = False
        db_table = 'casedwords'

class Glfs(models.Model):
    wordid = models.IntegerField()
    synsetid = models.IntegerField()
    lf = models.TextField()
    text = models.TextField(blank=True)
    issub = models.BooleanField()
    class Meta:
        managed = False
        db_table = 'glfs'

class Ilfs(models.Model):
    wordid = models.IntegerField()
    synsetid = models.IntegerField()
    lf = models.TextField()
    prettylf = models.TextField()
    text = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'ilfs'

class Lexdomains(models.Model):
    lexdomainid = models.SmallIntegerField(unique=True)
    lexdomainname = models.CharField(max_length=32, blank=True)
    lexdomain = models.CharField(max_length=32, blank=True)
    pos = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'lexdomains'

class Lexlinks(models.Model):
    synset1id = models.IntegerField(primary_key=True)
    word1id = models.IntegerField(primary_key=True)
    synset2id = models.IntegerField(primary_key=True)
    word2id = models.IntegerField(primary_key=True)
    linkid = models.SmallIntegerField(primary_key=True)
    class Meta:
        managed = False
        db_table = 'lexlinks'

class Linktypes(models.Model):
    linkid = models.SmallIntegerField(unique=True)
    link = models.CharField(max_length=50, blank=True)
    recurses = models.BooleanField()
    class Meta:
        managed = False
        db_table = 'linktypes'

class Logs(models.Model):
    id = models.IntegerField(primary_key=True)
    module = models.CharField(max_length=32)
    tag = models.CharField(max_length=32)
    subtag = models.CharField(max_length=64)
    source = models.CharField(max_length=128, blank=True)
    location = models.IntegerField(blank=True, null=True)
    object = models.TextField()
    exc = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'logs'

class Morphmaps(models.Model):
    wordid = models.IntegerField(primary_key=True)
    pos = models.TextField(primary_key=True, blank=True) # This field type is a guess.
    morphid = models.IntegerField(primary_key=True)
    class Meta:
        managed = False
        db_table = 'morphmaps'

class Morphs(models.Model):
    morphid = models.IntegerField(primary_key=True)
    morph = models.CharField(max_length=70)
    class Meta:
        managed = False
        db_table = 'morphs'

class Postypes(models.Model):
    pos = models.TextField(unique=True) # This field type is a guess.
    posname = models.CharField(max_length=20)
    class Meta:
        managed = False
        db_table = 'postypes'

class Samples(models.Model):
    synsetid = models.IntegerField(primary_key=True)
    sampleid = models.SmallIntegerField(primary_key=True)
    sample = models.TextField()
    class Meta:
        managed = False
        db_table = 'samples'

class Semlinks(models.Model):
    synset1id = models.IntegerField(primary_key=True)
    synset2id = models.IntegerField(primary_key=True)
    linkid = models.SmallIntegerField(primary_key=True)
    class Meta:
        managed = False
        db_table = 'semlinks'

class Sensemaps2021(models.Model):
    wordid = models.IntegerField(primary_key=True)
    synsetid = models.IntegerField(primary_key=True)
    srcsynsetid = models.IntegerField(primary_key=True)
    quality = models.TextField(primary_key=True) # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'sensemaps2021'

class Sensemaps2130(models.Model):
    wordid = models.IntegerField(primary_key=True)
    synsetid = models.IntegerField(primary_key=True)
    srcsynsetid = models.IntegerField(primary_key=True)
    quality = models.TextField(primary_key=True) # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'sensemaps2130'

class Sensemaps3031(models.Model):
    wordid = models.IntegerField(primary_key=True)
    synsetid = models.IntegerField(primary_key=True)
    srcsynsetid = models.IntegerField(primary_key=True)
    quality = models.TextField(primary_key=True) # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'sensemaps3031'

class Senses(models.Model):
    wordid = models.IntegerField(primary_key=True)
    casedwordid = models.IntegerField(blank=True, null=True)
    synsetid = models.IntegerField(primary_key=True)
    senseid = models.IntegerField(blank=True, null=True)
    sensenum = models.SmallIntegerField()
    lexid = models.SmallIntegerField()
    tagcount = models.IntegerField(blank=True, null=True)
    sensekey = models.CharField(max_length=100, blank=True)
    class Meta:
        managed = False
        db_table = 'senses'

class Senses20(models.Model):
    wordid = models.IntegerField(primary_key=True)
    synsetid = models.IntegerField(primary_key=True)
    pos = models.TextField() # This field type is a guess.
    senseid = models.IntegerField(blank=True, null=True)
    sensenum = models.SmallIntegerField()
    sensekey = models.CharField(max_length=100, blank=True)
    class Meta:
        managed = False
        db_table = 'senses20'

class Senses21(models.Model):
    wordid = models.IntegerField(primary_key=True)
    synsetid = models.IntegerField(primary_key=True)
    pos = models.TextField() # This field type is a guess.
    senseid = models.IntegerField(blank=True, null=True)
    sensenum = models.SmallIntegerField()
    sensekey = models.CharField(max_length=100, blank=True)
    class Meta:
        managed = False
        db_table = 'senses21'

class Senses30(models.Model):
    wordid = models.IntegerField(primary_key=True)
    synsetid = models.IntegerField(primary_key=True)
    pos = models.TextField() # This field type is a guess.
    senseid = models.IntegerField(blank=True, null=True)
    sensenum = models.SmallIntegerField()
    sensekey = models.CharField(max_length=100, blank=True)
    class Meta:
        managed = False
        db_table = 'senses30'

class Sumofiles(models.Model):
    sumofileid = models.IntegerField(primary_key=True)
    sumofile = models.CharField(max_length=128)
    sumoversion = models.CharField(max_length=5, blank=True)
    sumodate = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'sumofiles'

class Sumoformulas(models.Model):
    formulaid = models.IntegerField(primary_key=True)
    formula = models.TextField()
    sumofileid = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'sumoformulas'

class Sumomaps(models.Model):
    synsetid = models.IntegerField(primary_key=True)
    sumoid = models.IntegerField()
    sumownrel = models.TextField() # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'sumomaps'

class Sumoparsemaps(models.Model):
    mapid = models.IntegerField(primary_key=True)
    formulaid = models.IntegerField()
    sumoid = models.IntegerField()
    sumoparsetype = models.TextField() # This field type is a guess.
    argnum = models.SmallIntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'sumoparsemaps'

class Sumotermattrs(models.Model):
    sumoid = models.IntegerField(primary_key=True)
    sumoattr = models.CharField(primary_key=True, max_length=1)
    class Meta:
        managed = False
        db_table = 'sumotermattrs'

class Sumoterms(models.Model):
    sumoid = models.IntegerField(primary_key=True)
    sumoterm = models.CharField(max_length=128)
    class Meta:
        managed = False
        db_table = 'sumoterms'

class Synsetmaps2031(models.Model):
    synsetid = models.IntegerField(primary_key=True)
    srcsynsetid = models.IntegerField(primary_key=True)
    quality = models.TextField(primary_key=True) # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'synsetmaps2031'

class Synsetmaps2131(models.Model):
    synsetid = models.IntegerField(primary_key=True)
    srcsynsetid = models.IntegerField(primary_key=True)
    quality = models.TextField(primary_key=True) # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'synsetmaps2131'

class Synsetmaps3031(models.Model):
    synsetid = models.IntegerField(primary_key=True)
    srcsynsetid = models.IntegerField(primary_key=True)
    quality = models.TextField(primary_key=True) # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'synsetmaps3031'

class Synsets(models.Model):
    synsetid = models.IntegerField(primary_key=True)
    pos = models.TextField() # This field type is a guess.
    lexdomainid = models.SmallIntegerField()
    definition = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'synsets'

class Vframemaps(models.Model):
    synsetid = models.IntegerField(primary_key=True)
    wordid = models.IntegerField(primary_key=True)
    frameid = models.SmallIntegerField(primary_key=True)
    class Meta:
        managed = False
        db_table = 'vframemaps'

class Vframes(models.Model):
    frameid = models.SmallIntegerField(unique=True)
    frame = models.CharField(max_length=50, blank=True)
    class Meta:
        managed = False
        db_table = 'vframes'

class Vframesentencemaps(models.Model):
    synsetid = models.IntegerField(primary_key=True)
    wordid = models.IntegerField(primary_key=True)
    sentenceid = models.SmallIntegerField(primary_key=True)
    class Meta:
        managed = False
        db_table = 'vframesentencemaps'

class Vframesentences(models.Model):
    sentenceid = models.SmallIntegerField(unique=True)
    sentence = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'vframesentences'

class Vnclasses(models.Model):
    classid = models.SmallIntegerField(unique=True)
    class_field = models.CharField(db_column='class', max_length=64) # Field renamed because it was a Python reserved word.
    class Meta:
        managed = False
        db_table = 'vnclasses'

class Vnclassmembers(models.Model):
    classid = models.SmallIntegerField(primary_key=True)
    wordid = models.IntegerField(primary_key=True)
    class Meta:
        managed = False
        db_table = 'vnclassmembers'

class Vnclassmembersenses(models.Model):
    classid = models.SmallIntegerField(primary_key=True)
    wordid = models.IntegerField(primary_key=True)
    sensenum = models.SmallIntegerField(primary_key=True)
    synsetid = models.IntegerField(blank=True, null=True)
    sensekey = models.CharField(max_length=100, blank=True)
    quality = models.TextField() # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'vnclassmembersenses'

class Vnexamplemaps(models.Model):
    frameid = models.IntegerField(primary_key=True)
    exampleid = models.SmallIntegerField(primary_key=True)
    class Meta:
        managed = False
        db_table = 'vnexamplemaps'

class Vnexamples(models.Model):
    exampleid = models.SmallIntegerField(unique=True)
    example = models.CharField(max_length=128)
    class Meta:
        managed = False
        db_table = 'vnexamples'

class Vnframemaps(models.Model):
    framemapid = models.IntegerField(primary_key=True)
    wordid = models.IntegerField()
    synsetid = models.IntegerField(blank=True, null=True)
    classid = models.SmallIntegerField()
    frameid = models.IntegerField()
    fquality = models.TextField() # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'vnframemaps'

class Vnframenames(models.Model):
    nameid = models.SmallIntegerField(unique=True)
    framename = models.CharField(max_length=64)
    class Meta:
        managed = False
        db_table = 'vnframenames'

class Vnframes(models.Model):
    frameid = models.IntegerField(primary_key=True)
    number = models.CharField(max_length=16, blank=True)
    xtag = models.CharField(max_length=16, blank=True)
    nameid = models.SmallIntegerField()
    subnameid = models.SmallIntegerField()
    syntaxid = models.IntegerField()
    semanticsid = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'vnframes'

class Vnframesubnames(models.Model):
    subnameid = models.SmallIntegerField(unique=True)
    framesubname = models.CharField(max_length=64)
    class Meta:
        managed = False
        db_table = 'vnframesubnames'

class Vngroupingmaps(models.Model):
    groupingmapid = models.IntegerField(primary_key=True)
    classid = models.SmallIntegerField()
    wordid = models.IntegerField()
    groupingid = models.SmallIntegerField()
    class Meta:
        managed = False
        db_table = 'vngroupingmaps'

class Vngroupings(models.Model):
    groupingid = models.SmallIntegerField(unique=True)
    grouping = models.CharField(max_length=64)
    class Meta:
        managed = False
        db_table = 'vngroupings'

class Vnpredicatemaps(models.Model):
    semanticsid = models.IntegerField(primary_key=True)
    predid = models.SmallIntegerField(primary_key=True)
    class Meta:
        managed = False
        db_table = 'vnpredicatemaps'

class Vnpredicates(models.Model):
    predid = models.SmallIntegerField(unique=True)
    pred = models.CharField(max_length=128)
    class Meta:
        managed = False
        db_table = 'vnpredicates'

class Vnrolemaps(models.Model):
    rolemapid = models.IntegerField(primary_key=True)
    wordid = models.IntegerField()
    synsetid = models.IntegerField(blank=True, null=True)
    roleid = models.SmallIntegerField()
    classid = models.SmallIntegerField()
    rquality = models.TextField() # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'vnrolemaps'

class Vnroles(models.Model):
    roleid = models.SmallIntegerField(unique=True)
    roletypeid = models.SmallIntegerField()
    selrestrsid = models.SmallIntegerField()
    class Meta:
        managed = False
        db_table = 'vnroles'

class Vnroletypes(models.Model):
    roletypeid = models.SmallIntegerField(unique=True)
    roletype = models.CharField(max_length=32)
    class Meta:
        managed = False
        db_table = 'vnroletypes'

class Vnselrestrs(models.Model):
    selrestrsid = models.SmallIntegerField(unique=True)
    selrestrs = models.TextField()
    class Meta:
        managed = False
        db_table = 'vnselrestrs'

class Vnselrestrtypes(models.Model):
    selrestrid = models.SmallIntegerField(unique=True)
    selrestrval = models.CharField(max_length=32)
    selrestr = models.CharField(max_length=32)
    class Meta:
        managed = False
        db_table = 'vnselrestrtypes'

class Vnsemantics(models.Model):
    semanticsid = models.IntegerField(primary_key=True)
    semantics = models.TextField()
    class Meta:
        managed = False
        db_table = 'vnsemantics'

class Vnsyntaxes(models.Model):
    syntaxid = models.IntegerField(primary_key=True)
    syntax = models.TextField()
    class Meta:
        managed = False
        db_table = 'vnsyntaxes'

class Words(models.Model):
    wordid = models.IntegerField(primary_key=True)
    lemma = models.CharField(max_length=80)
    class Meta:
        managed = False
        db_table = 'words'

class Xwnparselfts(models.Model):
    synsetid = models.IntegerField()
    parse = models.TextField()
    lft = models.TextField()
    parsequality = models.SmallIntegerField(blank=True, null=True)
    lftquality = models.SmallIntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'xwnparselfts'

class Xwnwsds(models.Model):
    synsetid = models.IntegerField()
    wsd = models.TextField()
    text = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'xwnwsds'

