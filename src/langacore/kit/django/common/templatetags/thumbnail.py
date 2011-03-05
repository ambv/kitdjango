#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2010 Łukasz Langa

"""The thumbnail filter."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from django import template
from PIL import Image


register = template.Library()


def _is_proper_image(image):
    if image is not None:
        for attr in 'width', 'height', 'file', 'url':
            if not hasattr(image, attr):
                return False
        return True
    return False


@register.filter
def thumbnail(image, size):
    """For a given `image` constructs a thumbnail using the rule specified in
    the `size` param.

    Supported types of `image`:

    * any object with the `width`, `height`, `file` and `url` attributes (such
      as a Django ImageField)

    * any object with an `image` attribute pointing to an object of the other
      kind

    If an incompatible object is passed, None is returned.

    Possible values for `size`:

    * h{height} - scale to match the height given. Example: "h100" scales to
                  100px in height. Width is scaled proportionally, may exceed
                  100px.

    * w{width} - scale to match the width given. Example: "w312" scales to
                 312px in width. Height is scaled proportionally, may exceed
                 312px.

    * m{max_size} - scale to match the greater dimension to the value given.
                    Example: "m50" would scale an 80x50 image to 50x31, and
                    an 40x120 image to 17x50.

    The thumbnails are kept next to the original images with a `_{size}` suffix
    added to the name. If a thumbnail exists and is newer than the original
    image, it is reused on subsequent calls."""

    if not _is_proper_image(image):
        if hasattr(image, 'image') and _is_proper_image(image.image):
            image = image.image
        else:
            return None

    if size.startswith("h"):
        height = int(size[1:])
        width = height * image.width / image.height
    elif size.startswith("w"):
        width = int(size[1:])
        height = width * image.height / image.width
    elif size.startswith("m"):
        max = int(size[1:])
        if image.width > image.height:
            width = max
            height = width * image.height / image.width
        else:
            height = max
            width = height * image.width / image.height
    else:
        width, height = size.split("x")
    width = int(round(width))
    height = int(round(height))

    file = image.file.name
    basename, format = file.rsplit('.', 1)
    thumb_filename = basename + '_' + size + '.' + format

    baseurl, format = image.url.rsplit('.', 1)
    thumb_url = baseurl + '_' + size + '.' + format

    if os.path.exists(thumb_filename):
        if os.path.getmtime(thumb_filename) < os.path.getmtime(file):
            create_new = True
            os.unlink(thumb_filename)
        else:
            create_new = False
    else:
        create_new = True

    if create_new:
        pil_image = Image.open(file)
        pil_image.thumbnail([width, height], Image.ANTIALIAS)
        pil_image.save(thumb_filename, pil_image.format)

    return thumb_url
