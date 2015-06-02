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

test()

# If you're a good person, you can report false positives via akismet.submit_ham(),
# and false negatives via akismet.submit_spam(), using exactly the same parameters
# as akismet.comment_check.