# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.translation import ugettext as _


def forwards(apps, schema_editor):

    Post = apps.get_model('posts', 'Post')
    post = Post.objects.get(pk=1)

    CommentStatus = apps.get_model('comments', 'CommentStatus')
    pending = CommentStatus.objects.create(**{
        'pk': 1,
        'label': _('Pending'),
        'api_id': 'pending',
        'color': '#EE9A31',
        'publish_comment': False,
    })
    approved = CommentStatus.objects.create(**{
        'pk': 2,
        'label': _('Approved'),
        'api_id': 'approved',
        'color': '#42AD3F',
        'publish_comment': True,
    })
    spam = CommentStatus.objects.create(**{
        'pk': 3,
        'label': _('Spam'),
        'api_id': 'spam',
        'color': '#DE2121',
        'publish_comment': False,
    })
    trash = CommentStatus.objects.create(**{
        'pk': 4,
        'label': _('Trash'),
        'api_id': 'trash',
        'color': '#444444',
        'publish_comment': False,
    })
    Comment = apps.get_model('comments', 'Comment')
    comment = Comment(**{
        'pk': 1,
        'lft': 1,
        'rght': 2,
        'level': 0,
        'tree_id': 0,
        'post': post,
        'author_name': 'William Howdy',
        'author_email': 'william.howdy@example.org',
        'author_url': 'example.org',
        'status': approved,
        'content': _("Hi, this is a comment.  \n"
                     "To delete a comment, just log in and view the post's "
                     "comments. There you will have the option to edit or "
                     "delete them."),
    })
    comment.save(force_insert=True)


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0002_custom_fields'),
        ('posts', '0002_initial_data'),
    ]

    initial = True

    operations = [
        migrations.RunPython(forwards),
    ]
