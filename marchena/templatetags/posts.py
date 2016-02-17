# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import calendar
from datetime import datetime

from django.core.urlresolvers import reverse
from django.db.models import Count
from django.template.base import Library
from django.template.defaultfilters import date as date_format
from django.utils import six
from django.utils import timezone

from yepes.loading import get_model
from yepes.template import AssignTag, InclusionTag, SingleTag
from yepes.template import MultipleObjectMixin, SingleObjectMixin

Author = get_model('authors', 'Author')
Category = get_model('posts', 'Category')
Post = get_model('posts', 'Post')
Tag = get_model('posts', 'Tag')

register = Library()


## {% calendar[ year[ month]] %} ###############################################


class CalendarTag(MultipleObjectMixin, InclusionTag):

    model = Post
    template = 'partials/calendar.html'

    def get_posts_by_publication_day(self, first_date, last_date, user=None):
        days = {i: [] for i in range(32)}
        for post in self.get_queryset(first_date, last_date, user):
            days[post.publish_from.day].append(post)
        return days

    def get_publication_days(self, first_date, last_date, user=None):
        posts = self.get_queryset(first_date, last_date, user)
        dates = posts.datetimes('publish_from', 'day')
        return {date.day for date in dates}

    def get_queryset(self, first_date, last_date, user=None):
        qs = super(CalendarTag, self).get_queryset()
        qs = qs.published(user=user)
        qs = qs.filter(publish_from__gte=first_date,
                       publish_from__lte=last_date)
        return qs.defer('excerpt', 'excerpt_html', 'content', 'content_html')

    def process(self, year=None, month=None):
        now = timezone.now()
        if month is None:
            month = now.month
        if year is None:
            year = now.year

        cal = calendar.Calendar()
        tzinfo = timezone.get_current_timezone()
        starts_on, last_day = calendar.monthrange(year, month)
        first_date = datetime(year, month, 1, 0, 0, 0, 0, tzinfo)
        last_date = datetime(year, month, last_day, 23, 59, 59, 999999, tzinfo)

        posts_by_day = self.get_posts_by_publication_day(
                                first_date,
                                last_date,
                                self.context.get('user'))
        month_calendar = [
            [
                (
                    day,
                    posts_by_day[day],
                    reverse('archive_day', kwargs={'year': year,
                                                   'month': month,
                                                   'day': day}),
                )
                for day
                in week
            ]
            for week
            in cal.monthdayscalendar(year, month)
        ]

        context = self.get_new_context()
        context.update({
            'day_abbreviations': calendar.day_abbr,
            'day_names': calendar.day_name,
            'first_date': first_date,
            'last_date': last_date,
            'month': month,
            'month_name': calendar.month_name[month],
            'month_calendar': month_calendar,
            'year': year,
        })
        return self.get_content(context)

register.tag('calendar', CalendarTag.as_tag())


## {% get_archives[ period[ ordering]] as variable_name %} #####################


class GetArchivesTag(MultipleObjectMixin, AssignTag):

    field_name = 'publish_from'
    model = Post

    def process(self, period='year', ordering='DESC'):
        qs = self.get_queryset()
        qs = qs.published(user=self.context.get('user'))
        return qs.datetimes(self.get_field_name(), period, ordering)

register.tag('get_archives', GetArchivesTag.as_tag())


## {% get_category category_slug[ as variable_name] %} #########################


class GetCategoryTag(SingleObjectMixin, AssignTag):

    assign_var = False
    field_name = 'slug'
    model = Category

    def process(self, category_slug):
        blog = self.context.get('blog')
        if not blog:
            return None
        qs = self.get_queryset()
        qs = qs.filter(id=blog.pk)
        return self.get_object(qs, category_slug)

register.tag('get_category', GetCategoryTag.as_tag())


## {% get_categories *category_slugs as variable_name %} #######################


class GetCategoriesTag(MultipleObjectMixin, AssignTag):

    field_name = 'slug'
    model = Category

    def process(self, *category_slugs):
        blog = self.context.get('blog')
        if not blog:
            return []
        qs = self.get_queryset()
        qs = qs.filter(id=blog.pk)
        return self.get_object_list(qs, category_slugs)

register.tag('get_categories', GetCategoriesTag.as_tag())


## {% get_next_post[ post[ user[ in_same_blog]]][ as variable_name] %} #########


class GetNextPostTag(AssignTag):

    assign_var = False

    def process(self, post=None, user=None, in_same_blog=True):
        if post is None:
            post = self.context.get('post')
            if not post:
                return None

        if user is None:
            user = self.context.get('user')

        return post.get_next_in_order(user, in_same_blog)

register.tag('get_next_post', GetNextPostTag.as_tag())


## {% get_previous_post[ post[ user[ in_same_blog]]][ as variable_name] %} #####


class GetPreviousPostTag(AssignTag):

    assign_var = False

    def process(self, post=None, user=None, in_same_blog=True):
        if post is None:
            post = self.context.get('post')
            if not post:
                return None

        if user is None:
            user = self.context.get('user')

        return post.get_previous_in_order(user, in_same_blog)

register.tag('get_previous_post', GetPreviousPostTag.as_tag())


## {% get_recent_posts[ limit[ author[ blog[ category[ tag]]]]] as var %} ######


class GetRecentPostsTag(MultipleObjectMixin, AssignTag):

    model = Post

    def process(self, limit=5, author=None, blog=None, category=None, tag=None):
        posts = self.get_queryset()
        posts = posts.published(user=self.context.get('user'))
        posts = posts.order_by('-publish_from')

        if author is not None:
            if isinstance(author, six.string_types):
                username_lookup = 'author__{0}'.format(Author.USERNAME_FIELD)
                posts = posts.filter(**{username_lookup: author})
            else:
                posts = posts.filter(author=author)

        if blog is not None:
            if isinstance(blog, six.string_types):
                posts = posts.filter(blog__slug=blog)
            else:
                posts = posts.filter(blog=blog)

        if category is not None:
            if isinstance(category, six.string_types):
                posts = posts.filter(category__slug=category)
            else:
                posts = posts.filter(category=category)

        if tag is not None:
            if isinstance(tag, six.string_types):
                posts = posts.filter(tags__slug=tag)
            else:
                posts = posts.filter(tag=tag)

        if limit:
            posts = posts[:limit]

        return posts

register.tag('get_recent_posts', GetRecentPostsTag.as_tag())


## {% get_tag tag_slug[ as variable_name] %} ###################################


class GetTagTag(SingleObjectMixin, AssignTag):

    assign_var = False
    field_name = 'slug'
    model = Tag

    def process(self, tag_slug):
        qs = self.get_queryset()
        return self.get_object(qs, tag_slug)

register.tag('get_tag', GetTagTag.as_tag())


## {% get_tags *tag_slugs as variable_name %} ##################################


class GetTagsTag(MultipleObjectMixin, AssignTag):

    field_name = 'slug'
    model = Tag

    def process(self, *tag_slugs):
        qs = self.get_queryset()
        return self.get_object_list(qs, tag_slugs)

register.tag('get_tags', GetTagsTag.as_tag())


## {% last_modification[ format] %} ############################################


class LastModificationTag(MultipleObjectMixin, SingleTag):

    model = Post

    def get_date(self, queryset):
        queryset = queryset.order_by('-last_modified')
        return queryset.values_list('last_modified', flat=True).first()

    def process(self, format=None):
        qs = self.get_queryset()
        qs = qs.published(user=self.context.get('user'))
        return date_format(self.get_date(qs), format)

register.tag('last_modification', LastModificationTag.as_tag())


## {% last_publication[ format] %} #############################################


class LastPublicationTag(LastModificationTag):

    def get_date(self, queryset):
        queryset = queryset.order_by('-publish_from')
        return queryset.values_list('publish_from', flat=True).first()

register.tag('last_publication', LastPublicationTag.as_tag())


## {% next_post_link[ format[ link[ in_same_blog]]] %} #########################


class NextPostLinkTag(SingleTag):

    def process(self, format='{link} &raquo;', link='{title}', in_same_blog=True):
        post = self.context.get('post')
        if not post:
            return ''

        user = self.context.get('user')
        next_post = post.get_next_in_order(user, in_same_blog)
        if not next_post:
            return ''

        return format.format(link='<a href="{url}">{link}</a>'.format(
            url=next_post.get_absolute_url(),
            link=link.format(title=next_post.title),
        ))

register.tag('next_post_link', NextPostLinkTag.as_tag())


## {% post_authors[ separator[ last_separator]][ as variable_name] %} ##########


class PostAuthorsTag(AssignTag):

    assign_var = False
    is_safe = True

    def process(self, separator=', ', last_separator=None):
        post = self.context.get('post')
        if not post:
            return ''

        links = [
            author.get_link()
            for author
            in post.authors.all()
        ]
        if last_separator is not None:
            links[-2:] = [last_separator.join(links[-2:])]

        return separator.join(links)

register.tag('post_authors', PostAuthorsTag.as_tag())


## {% post_categories[ separator[ last_separator]][ as variable_name] %} #######


class PostCategoriesTag(AssignTag):

    assign_var = False
    is_safe = True

    def process(self, separator=', ', last_separator=None):
        post = self.context.get('post')
        if not post:
            return ''

        links = [
            category.get_link()
            for category
            in post.categories.all()
        ]
        if last_separator is not None:
            links[-2:] = [last_separator.join(links[-2:])]

        return separator.join(links)

register.tag('post_categories', PostCategoriesTag.as_tag())


## {% post_tags[ separator[ last_separator]][ as variable_name] %} #############


class PostTagsTag(AssignTag):

    assign_var = False
    is_safe = True

    def process(self, separator=', ', last_separator=None):
        post = self.context.get('post')
        if not post:
            return ''

        links = [
            tag.get_link()
            for tag
            in post.tags.all()
        ]
        if last_separator is not None:
            links[-2:] = [last_separator.join(links[-2:])]

        return separator.join(links)

register.tag('post_tags', PostTagsTag.as_tag())


## {% previous_post_link[ format[ link[ in_same_blog]]] %} #####################


class PreviousPostLinkTag(SingleTag):

    def process(self, format='&laquo; {link}', link='{title}', in_same_blog=True):
        post = self.context.get('post')
        if not post:
            return ''

        user = self.context.get('user')
        previous_post = post.get_previous_in_order(user, in_same_blog)
        if not previous_post:
            return ''

        return format.format(link='<a href="{url}">{link}</a>'.format(
            url=previous_post.get_absolute_url(),
            link=link.format(title=previous_post.title),
        ))

register.tag('previous_post_link', PreviousPostLinkTag.as_tag())


## {% tag_cloud[ limit] %} #####################################################


class TagCloudTag(MultipleObjectMixin, InclusionTag):

    model = Tag
    template = 'partials/tag_cloud.html'

    def process(self, limit=45):
        qs = self.get_queryset()
        qs = qs.annotate(post_count=Count('posts'))
        qs = qs.order_by('post_count')
        if limit:
            qs = qs[:limit]

        tags = list(qs)
        min_posts = tags[0].post_count
        max_posts = tags[-1].post_count
        denominator = float(max_posts - min_posts)
        tags.sort(key=lambda tag: tag.name)

        for tag in tags:
            tag.score = 1.0 + ((tag.post_count - min_posts) / (denominator))

        context = self.get_new_context()
        context.update({
            'tags': tags,
        })
        return self.get_content(context)

register.tag('tag_cloud', TagCloudTag.as_tag())

