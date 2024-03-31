import re


def is_correct_url(user_url):
    reg = r"^(?:http|https):\/\/(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?$"
    is_url = bool(re.search(reg, user_url))
    return is_url
