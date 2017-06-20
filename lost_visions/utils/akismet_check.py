import sys

import akismet
from crowdsource import settings
from lost_visions import models

akismet.USERAGENT = "IllustrationArchive/v2"

my_api_key = settings.kismet_api_key

spam_comment = '''How many more years do you have to go? <a href=" http://morodalsfestivalen.no/orlistat-uk-buy.pptx#hum ">where can i buy orlistat 120mg</a> Tepco's handling of the clean-up has complicated Japan'sefforts to restart its 50 nuclear power plants, almost all ofwhich have been idled since the disaster over local community concerns about safety. <a href=" http://www.orphanageclothing.com/?p=directions-for-taking-fluticasone-propionate-nasal-spray-que-es.pdf ">fluticasone nasal spray cost it working</a> Using data from spacecraft orbiting Mars, scientists have studied a huge crater that they theorize is the evidence of a super volcano that would have drastically altered the climate on Mars by sending large amounts of ash and gas into the atmosphere. There are similar types of craters on Earth in places such as Yellowstone National Park, Lake Toba in North Sumatra, Indonesia, and the Canary Islands off the west coast of North Africa. <a href=" http://hettalentenlab.nl/index.php/use-of-tablet-diamox-322#excepting ">strattera 80 mgs</a> "The broader picture is still that labor market conditions are improving, albeit not quite as much as we previously thought," said Paul Ashworth, chief U.S. economist for Capital Economics, in a research note. <a href=" http://www.world-television.com/buy-inderal.pdf ">order propranolol online uk</a> Sir Chris Hoy, who has switched to four wheels this year after winning everything in track cycling, makes an appearance in a Mini, alongside celebrity chef James Martin. Lord Paul Drayson, a champion of electric racers, is driving an Aston Martin DB4GT in the RAC TT Celebration race. <a href=" http://www.st-cuthbertmayne.co.uk/gabapentin-300mg-side-effects-uk.pdf ">gabapentin 300 mg uk</a> "This will help people get quick answers for things they are looking for across their own stuff," Roya Soleimani, who works with Google's search team, told ABC News. "Rather than making people be their own mini search engine, they are able to search in one search box -- rather than dig through their email or calendar."'''

def test():
    try:
        real_key = akismet.verify_key(my_api_key, "illustrationarchive.cardiff.ac.uk")
        print real_key
        if real_key:
            is_spam = akismet.comment_check(my_api_key, "illustrationarchive.cardiff.ac.uk",
                "127.0.0.1", "Mozilla/5.0 (...) Gecko/20051111 Firefox/1.5",
                comment_content=spam_comment)
            if is_spam:
                print "Yup, that's spam alright."
            else:
                print "Hooray, your users aren't scum!"
    except akismet.AkismetError, e:
        print e.response, e.statuscode


def is_spam(text):
    try:
        is_spam = akismet.comment_check(my_api_key, "illustrationarchive.cardiff.ac.uk",
                "127.0.0.1", "Mozilla/5.0 (...) Gecko/20051111 Firefox/1.5",
                comment_content=text)
        return is_spam

    except akismet.AkismetError, e:
        print e.response, e.statuscode


# If you're a good person, you can report false positives via akismet.submit_ham(),
# and false negatives via akismet.submit_spam(), using exactly the same parameters
# as akismet.comment_check.


def send_spam():
    spams = [
        'Not in at the moment http://anestasiavodka.com/blog/how-to-use-mastigra-100/ mastigra price  This is what differentiates Americans, American foreign policy and our reaction to 9/11. This Americanism was at the core of the Bush Doctrine and is the ultimate legacy that will dominate American discussion of foreign policy for this entire century.',
        '''I like it a lot http://anestasiavodka.com/blog/how-to-use-mastigra-100/ mastigra 120 tabletki  Police had traveled to St. Augustine, Fla., to look for Ferrante, a leading researcher on Lou Gehrig's disease. But Allegheny County district attorney's office spokesman Mike Manko and police said Ferrante was arrested near Beckley, W.Va., by state police.'''
    ]

    for spam in spams:
        try:
            akismet.submit_spam(my_api_key, "illustrationarchive.cardiff.ac.uk",
                "127.0.0.1", "Mozilla/5.0 (...) Gecko/20051111 Firefox/1.5",
                comment_content=spam)
        except Exception as e:
            print e


def clean_image_texts():
    texts = models.ImageText.objects.all()
    print len(texts)
    for t in texts:
        spam = False
        print t.caption
        if is_spam(t.caption):
            spam = True

        print t.description
        if is_spam(t.description):
            spam = True
        if spam:
            print "spam found"
            # t.delete()

if __name__ == "__main__":
    print 'Options are: test, spam'
    print 'Running..'
    print sys.argv
    for arg in sys.argv[1:]:
        print arg

        if arg == "test":
            test()
        if arg == "spam":
            clean_image_texts()

    if len(sys.argv) < 2:
        clean_image_texts()
