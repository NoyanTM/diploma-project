from unicodedata import normalize
from decimal import Decimal

from bs4 import Tag


def normalize_tag(tag: Tag, param: str = None):
    if tag is None or tag.text.strip() == "":
        return None
    if param == "status":
        return normalize("NFKD", tag.text.strip()).lower()
    if param == "user_name":
        return normalize("NFKD", tag.text.strip()).title()
    if param == "code":
        code = normalize("NFKD", tag.text.strip())
        if code == "None" or code == "":
            return None
        return int(code)
    if param == "money_broken_ru":
        text_space = normalize("NFKD", tag.text.strip()).replace(" ", "")
        text_parts = text_space.replace(",", "")[:-2] + "." + text_space.replace(",", "")[-2:]
        return Decimal(str(text_parts)) # text_parts
    if param == "set":
        return normalize("NFKD", tag.text.strip()).replace("-", "")
    return normalize("NFKD", tag.text.strip())
