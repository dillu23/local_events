import re

def filter_url(text):
    st = ""
    words = text.split(' ')
    for word in words:
        if word.find('http') == -1:
            st = st + word + " "
    return st

def filter_words(text):
    text  = re.sub('[^0-9a-zA-Z]+', ' ', text)
    words = text.split(' ')
    st = ""
    ct = 0
    if len(words) <=3:
        return ""
    for word in words:
        if len(word) <=12 and len(word) > 3:
            ct = ct + 1
            st = st + word + " "
    if ct <= 3:
        return ""
    return st

def contains_today_stats(text):
    if ((text.find('today')!= -1 or text.find('week') != -1) and text.find('follower')!= -1) or text.find('#gameinsight')!= -1: 
        return True
    return False

def text_filter(tweet_text):
    text = tweet_text.lower()
    if contains_today_stats(text):
        return ""
    text = filter_url(text)
    text = filter_words(text)
    return text