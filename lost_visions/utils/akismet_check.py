import akismet
from crowdsource import settings

akismet.USERAGENT = "IllustrationArchive/v2"

my_api_key = settings.kismet_api_key

def test():
    try:
        real_key = akismet.verify_key(my_api_key, "illustrationarchive.cardiff.ac.uk")
        print real_key
        if real_key:
            is_spam = akismet.comment_check(my_api_key, "illustrationarchive.cardiff.ac.uk",
                "127.0.0.1", "Mozilla/5.0 (...) Gecko/20051111 Firefox/1.5",
                comment_content="""buy cheap viagra!!!""")
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

# send_spam()