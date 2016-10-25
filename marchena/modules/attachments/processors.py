# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from yepes.loading import LazyModel

Attachment = LazyModel('attachments', 'Attachment')

__all__ = ('attachment_tags', )


TAGS_RE = re.compile(r"""
    (?P<open_paragraph><p[^>]*>\s*)?
    \[
        (?P<tag>audio|iframe|image|link|video)
        (?:=(?P<arg>[a-zA-Z0-9]+))?
        (?P<classes>(?:\ +[a-zA-Z0-9_\-]+)+)?
        (?:\ +\#(?P<id>[a-zA-Z0-9_\-]+))?
        (?P<attributes>(?:\ +[a-zA-Z]+=(?:[a-zA-Z0-9_\-]+|'[^']*'|"[^"]*"))+)?
    \]
    (?P<content>[^[\]]+)
    \[
        /
        \2
    \]
    (?P<close_paragraph>\s*</p>)?
""", re.VERBOSE)


def replacement(matchobj):
    attachment_id = matchobj.group('arg')
    if attachment_id is not None:
        content = matchobj.group('content')
    else:
        attachment_id = matchobj.group('content')
        content = None
        if attachment_id is None or ' ' in attachment_id:
            return matchobj.group(0)

    if len(attachment_id) < 10 and attachment_id.isdigit():
        constraints = {'pk__exact': attachment_id}
    else:
        constraints = {'guid__exact': attachment_id}

    attachment = Attachment.objects.filter(**constraints).first()
    if attachment is None:
        return matchobj.group(0)

    attrs = {}

    id = matchobj.group('id')
    if id:
        attrs['id'] = id

    classes = matchobj.group('classes')
    if classes:
        attrs['class'] = ' '.join(classes.split())

    attributes = matchobj.group('attributes')
    if attributes:
        for item in attributes.split():
            key, value = item.split('=')
            if value.startswith("'"):
                value = value.strip("'")
            elif value.startswith('"'):
                value = value.strip('"')
            elif value == '' or value == key or value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            attrs[key] = value

    tag = matchobj.group('tag')
    if tag == 'audio':
        html = attachment.get_audio_tag(**attrs)
    elif tag == 'iframe':
        html = attachment.get_iframe_tag(**attrs)
    elif tag == 'image':
        if content:
            attrs['alt'] = content
        html = attachment.get_image_tag(**attrs)
    elif tag == 'link':
        if content:
            attrs['text'] = content
        html = attachment.get_file_link(**attrs)
    elif tag == 'video':
        html = attachment.get_video_tag(**attrs)
    else:
        return matchobj.group(0)

    open_paragraph = matchobj.group('open_paragraph')
    close_paragraph = matchobj.group('close_paragraph')
    if (open_paragraph is not None and close_paragraph is not None
            and html.startswith('<div') and html.endswith('</div>')):
        # If the element is wrapped into a div and its parent is an
        # empty paragraph, remove the paragraph.
        return html

    if open_paragraph is not None:
        html = open_paragraph + html

    if close_paragraph is not None:
        html = html + close_paragraph

    return html


def attachment_tags(text):
    return TAGS_RE.sub(replacement, text)

