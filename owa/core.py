import re

TAG_BREAKERS = re.compile('|'.join(('\\\\', '/', '&', ',', ' ',  '\\\.')))


def break_tag(tag):
    """Splits a composite tag (like "death metal") into individual tags
    (like "death" and "metal") based on arbitrary punctuation. The smaller
    tags are striped of white space and placed into a set.

    :param tag: A string representing a tag.
    """
    return set(t.strip() for t in re.split(TAG_BREAKERS, tag) if t)
