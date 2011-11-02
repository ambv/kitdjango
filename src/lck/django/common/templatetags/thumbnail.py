#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 by Łukasz Langa
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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

    * s{max_size} - cuts a square from the image and scales it to the value
                    given. Example: "s48" would scale a 50x80 image to 48x48
                    based on the top 50x50 square.

    The thumbnails are kept next to the original images with a `_{size}` suffix
    added to the name. If a thumbnail exists and is newer than the original
    image, it is reused on subsequent calls."""

    if not _is_proper_image(image):
        if hasattr(image, 'image') and _is_proper_image(image.image):
            image = image.image
        else:
            return None

    shift = None
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
    elif size.startswith("s"):
        width = height = int(size[1:])
        if image.width > image.height:
            shift = int((image.width - image.height) / 2)
        else:
            shift = 0
    else:
        width, height = size.split("x")
    width = int(round(width))
    height = int(round(height))

    file = image.file.name
    try:
        basename, format = file.rsplit('.', 1)
    except ValueError: # if there is no extension
        basename = file
        format = 'jpg'
    thumb_filename = basename + '_' + size + '.' + format

    try:
        baseurl, format = image.url.rsplit('.', 1)
    except ValueError: # if there is no extension
        baseurl = image.url
        format = 'jpg'
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
        pil_format = pil_image.format or 'JPEG'
        if pil_format not in Image.SAVE:
            pil_format = 'JPEG'
        if shift is not None:
            shorter = min(image.width, image.height)
            pil_image = pil_image.crop((shift, 0, shorter+shift, shorter))
        pil_image.thumbnail((width, height), Image.ANTIALIAS)
        if pil_format == 'JPEG' and pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        pil_image.save(thumb_filename, pil_format)

    return thumb_url
