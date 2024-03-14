import re


def is_correct_url(user_url):
    reg = r"https?:\/\/www\..+\/.*"
    is_url = bool(re.search(reg, user_url))
    return is_url
