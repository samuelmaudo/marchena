# -*- coding:utf-8 -*-

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils.encoding import python_2_unicode_compatible
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from yepes.urlresolvers import build_full_url, full_reverse

from marchena.abstract_models import (
    AbstractBlog,
    AbstractCategory,
    AbstractComment,
    AbstractCommentStatus,
    AbstractLink,
    AbstractLinkCategory,
    AbstractPost,
    AbstractPostImage,
    AbstractTag,
)
from marchena.managers import AuthorManager


@python_2_unicode_compatible
class Author(get_user_model()):

    objects = AuthorManager()

    class Meta:
        proxy = True
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')

    def get_absolute_url(self):
        kwargs = {
            #'author_pk': self.pk,
            'author_name': self.get_username(),
        }
        return reverse('post_list', kwargs=kwargs)

    def get_feed_url(self):
        kwargs = {
            #'author_pk': self.pk,
            'author_name': self.get_username(),
        }
        return full_reverse('post_feed', kwargs=kwargs)

    def get_full_url(self):
        return build_full_url(self.get_absolute_url())

    def get_link(self):
        return mark_safe('<a href="{0}">{1}</a>'.format(
                         self.get_absolute_url(),
                         self))

    def __str__(self):
        return self.get_full_name() or self.get_username()


class Blog(AbstractBlog):
    pass

class Category(AbstractCategory):
    pass

class Comment(AbstractComment):
    pass

class CommentStatus(AbstractCommentStatus):
    pass

class Link(AbstractLink):
    pass

class LinkCategory(AbstractLinkCategory):
    pass

class Post(AbstractPost):
    pass

class PostImage(AbstractPostImage):
    pass

class Tag(AbstractTag):
    pass

