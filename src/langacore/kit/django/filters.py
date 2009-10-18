from django.template.defaultfilters import slugify as crippled_slugify


def slugify(text, fallback='untitled-0'):
    slug = crippled_slugify(text)
    return slug if slug else fallback


def numberify(obj, default=0):
    return int(obj) if obj else default


def nullify(obj):
    return obj if obj else None


def strike_empty(obj):
    return obj if obj else u"---"
