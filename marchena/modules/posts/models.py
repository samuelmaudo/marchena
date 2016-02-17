# -*- coding:utf-8 -*-

from marchena.modules.posts.abstract_models import (
    AbstractCategory,
    AbstractPost,
    AbstractPostImage,
    AbstractPostRecord,
    AbstractTag,
)

class Category(AbstractCategory):
    pass

class Post(AbstractPost):
    pass

class PostImage(AbstractPostImage):
    pass

class PostRecord(AbstractPostRecord):
    pass

class Tag(AbstractTag):
    pass
