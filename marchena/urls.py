# -*- coding:utf-8 -*-

from django.conf.urls import patterns, include, url

from yepes.contrib.sitemaps.views import SitemapIndexView
from yepes.loading import get_class
from yepes.urlresolvers import full_reverse_lazy

CommentAtomFeed = get_class('comments.feeds', 'CommentAtomFeed')
CommentRssFeed = get_class('comments.feeds', 'CommentRssFeed')
PostsAtomFeed = get_class('posts.feeds', 'PostsAtomFeed')
PostsRssFeed = get_class('posts.feeds', 'PostsRssFeed')
AuthorPostsAtomFeed = get_class('posts.feeds', 'AuthorPostsAtomFeed')
AuthorPostsRssFeed = get_class('posts.feeds', 'AuthorPostsRssFeed')
BlogPostsAtomFeed = get_class('posts.feeds', 'BlogPostsAtomFeed')
BlogPostsRssFeed = get_class('posts.feeds', 'BlogPostsRssFeed')
CategoryPostsAtomFeed = get_class('posts.feeds', 'CategoryPostsAtomFeed')
CategoryPostsRssFeed = get_class('posts.feeds', 'CategoryPostsRssFeed')
TagPostsAtomFeed = get_class('posts.feeds', 'TagPostsAtomFeed')
TagPostsRssFeed = get_class('posts.feeds', 'TagPostsRssFeed')

BlogUrlGenerator = get_class('blogs.urlresolvers', 'BlogUrlGenerator')

AuthorDetailView = get_class('authors.views', 'AuthorDetailView')
AuthorListView = get_class('authors.views', 'AuthorListView')
BlogDetailView = get_class('blogs.views', 'BlogDetailView')
BlogListView = get_class('blogs.views', 'BlogListView')
CategoryDetailView = get_class('posts.views', 'CategoryDetailView')
CategoryListView = get_class('posts.views', 'CategoryListView')
PostDetailView = get_class('posts.views', 'PostDetailView')
PostListView = get_class('posts.views', 'PostListView')
PostSearchView = get_class('posts.views', 'PostSearchView')
TagDetailView = get_class('posts.views', 'TagDetailView')
TagListView = get_class('posts.views', 'TagListView')

PostArchiveIndexView = get_class('posts.views.archive', 'PostArchiveIndexView')
PostArchiveYearView = get_class('posts.views.archive', 'PostArchiveYearView')
PostArchiveMonthView = get_class('posts.views.archive', 'PostArchiveMonthView')
PostArchiveDayView = get_class('posts.views.archive', 'PostArchiveDayView')

LinksOpmlView = get_class('links.views.opml', 'LinksOpmlView')

AuthorSitemapView = get_class('authors.views.sitemaps', 'AuthorSitemapView')
BlogSitemapView = get_class('blogs.views.sitemaps', 'BlogSitemapView')
CategorySitemapView = get_class('posts.views.sitemaps', 'CategorySitemapView')
NewsSitemapView = get_class('posts.views.sitemaps', 'NewsSitemapView')
PostSitemapView = get_class('posts.views.sitemaps', 'PostSitemapView')
TagSitemapView = get_class('posts.views.sitemaps', 'TagSitemapView')


urlpatterns = patterns('',
    url(r'^$',
        PostListView.as_view(),
        name='post_list',
    ),
    url(r'^archives/$',
        PostArchiveIndexView.as_view(),
        name='archive_index',
    ),
    url(r'^archives/(?P<year>[\d]{4})/$',
        PostArchiveYearView.as_view(),
        name="archive_year",
    ),
    url(r'^archives/(?P<year>[\d]{4})/(?P<month>[\d]{1,2})/$',
        PostArchiveMonthView.as_view(),
        name="archive_month",
    ),
    url(r'^archives/(?P<year>[\d]{4})/(?P<month>[\d]{1,2})/(?P<day>[\d]{1,2})/$',
        PostArchiveDayView.as_view(),
        name="archive_day",
    ),
    url(r'^atom.xml$',
        PostsAtomFeed(),
        name='post_feed_atom',
    ),
    url(r'^authors/$',
        AuthorListView.as_view(),
        name='author_list',
    ),
    url(r'^authors/sitemap\.xml$',
        AuthorSitemapView.as_view(),
        name='author_sitemap',
    ),
    url(r'^authors/(?P<author_name>[-\w]+)/$',
        AuthorDetailView.as_view(),
        name='post_list',
    ),
    url(r'^authors/(?P<author_name>[-\w]+)/atom.xml$',
        AuthorPostsAtomFeed(),
        name='post_feed_atom',
    ),
    url(r'^authors/(?P<author_name>[-\w]+)/rss2.xml$',
        AuthorPostsRssFeed(),
        name='post_feed',
    ),
    url(r'^blogs/$',
        BlogListView.as_view(),
        name='blog_list',
    ),
    url(r'^blogs/sitemap\.xml$',
        BlogSitemapView.as_view(),
        name='blog_sitemap',
    ),
    url(r'^blogs/(?P<blog_slug>[-\w]+)/$',
        BlogDetailView.as_view(),
        name='post_list',
    ),
    url(r'^blogs/(?P<blog_slug>[-\w]+)/atom.xml$',
        BlogPostsAtomFeed(),
        name='post_feed_atom',
    ),
    url(r'^blogs/(?P<blog_slug>[-\w]+)/rss2.xml$',
        BlogPostsRssFeed(),
        name='post_feed',
    ),
    url(r'^blogs/(?P<blog_slug>[-\w]+)/categories/$',
        CategoryListView.as_view(),
        name='category_list',
    ),
    url(r'^blogs/(?P<blog_slug>[-\w]+)/categories/sitemap\.xml$',
        CategorySitemapView.as_view(),
        name='category_sitemap',
    ),
    url(r'^blogs/(?P<blog_slug>[-\w]+)/categories/(?P<category_slug>[-\w]+)/$',
        CategoryDetailView.as_view(),
        name='post_list',
    ),
    url(r'^blogs/(?P<blog_slug>[-\w]+)/categories/(?P<category_slug>[-\w]+)/atom.xml$',
        CategoryPostsAtomFeed(),
        name='post_feed_atom',
    ),
    url(r'^blogs/(?P<blog_slug>[-\w]+)/categories/(?P<category_slug>[-\w]+)/rss2.xml$',
        CategoryPostsRssFeed(),
        name='post_feed',
    ),
    url(r'^blogs/(?P<blog_slug>[-\w]+)/links/opml\.xml$',
        LinksOpmlView.as_view(),
        name='links_opml',
    ),
    url(r'^blogs/(?P<blog_slug>[-\w]+)/search/$',
        PostSearchView.as_view(),
        name='post_search',
    ),
    url(r'^blogs/(?P<blog_slug>[-\w]+)/sitemap\.xml$',
        PostSitemapView.as_view(),
        name='post_sitemap',
    ),
    url(r'^blogs/(?P<blog_slug>[-\w]+)/(?P<post_slug>[-\w]+)-(?P<post_guid>[0-9a-f]+)/$',
        PostDetailView.as_view(),
        name='post_detail',
    ),
    url(r'^blogs/(?P<blog_slug>[-\w]+)/(?P<post_slug>[-\w]+)-(?P<post_guid>[0-9a-f]+)/atom.xml$',
        CommentAtomFeed(),
        name='comment_feed_atom',
    ),
    url(r'^blogs/(?P<blog_slug>[-\w]+)/(?P<post_slug>[-\w]+)-(?P<post_guid>[0-9a-f]+)/rss2.xml$',
        CommentRssFeed(),
        name='comment_feed',
    ),
    url(r'^news/sitemap\.xml$',
        NewsSitemapView.as_view(),
        name='news_sitemap',
    ),
    url(r'^rss2.xml$',
        PostsRssFeed(),
        name='post_feed',
    ),
    url(r'^search/$',
        PostSearchView.as_view(),
        name='post_search',
    ),
    url(r'^sitemap\.xml$',
        SitemapIndexView.as_view(
            sitemap_urls=[
                full_reverse_lazy('author_sitemap'),
                full_reverse_lazy('blog_sitemap'),
                BlogUrlGenerator('category_sitemap'),
                full_reverse_lazy('news_sitemap'),
                BlogUrlGenerator('post_sitemap'),
                full_reverse_lazy('tag_sitemap'),
            ]
        ),
        name='sitemap_index',
    ),
    url(r'^tags/$',
        TagListView.as_view(),
        name='tag_list',
    ),
    url(r'^tags/sitemap\.xml$',
        TagSitemapView.as_view(),
        name='tag_sitemap',
    ),
    url(r'^tags/(?P<tag_slug>[-\w]+)/$',
        TagDetailView.as_view(),
        name='post_list',
    ),
    url(r'^tags/(?P<tag_slug>[-\w]+)/atom.xml$',
        TagPostsAtomFeed(),
        name='post_feed_atom',
    ),
    url(r'^tags/(?P<tag_slug>[-\w]+)/rss2.xml$',
        TagPostsRssFeed(),
        name='post_feed',
    ),
)
