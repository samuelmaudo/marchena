# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mimetypes
try:
    import magic
except ImportError:
    magic = None

from django.db import migrations
from django.utils.encoding import force_text
from django.utils.six.moves.urllib.request import urlopen


def calculate_mime_type(obj):
    if obj.file and magic is not None:
        file_type = magic.from_buffer(obj.file.read(1024), mime=True)
        if file_type is not None:
            return force_text(file_type)

    file_name = get_file_name(obj)
    file_type, _ = mimetypes.guess_type(file_name)
    if file_type is not None:
        return force_text(file_type)

    if not obj.file and magic is not None:
        file_type = magic.from_buffer(urlopen(file_name).read(1024), mime=True)
        if file_type is not None:
            return force_text(file_type)

    return None


def get_file_name(obj):
    if not obj.file:
        return obj.external_file
    else:
        return obj.file.name


def populate_mime_type(apps, schema_editor):
    Attachment = apps.get_model('attachments', 'Attachment')
    for obj in Attachment.objects.all():
        obj.mime_type = calculate_mime_type(obj)
        obj.save(update_fields=['mime_type'])


class Migration(migrations.Migration):

    dependencies = [
        ('attachments', '0002_add_mime_type'),
    ]

    operations = [
        migrations.RunPython(
            populate_mime_type,
            reverse_code=migrations.RunPython.noop
        ),
    ]
