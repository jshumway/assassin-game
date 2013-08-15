import re
import unicodedata


def slugify(string):
    """ Slugify |string| for use in URLs. """

    slug = unicodedata.normalize('NFKD', unicode(string))
    slug = slug.encode('ascii', 'ignore').lower()
    slug = re.sub(r'[^a-z0-9]+', '_', slug).strip('_')
    slug = re.sub(r'-+', '-', slug)

    return slug
