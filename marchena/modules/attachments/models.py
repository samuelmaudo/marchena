# -*- coding:utf-8 -*-

from yepes.apps import apps

AbstractAttachment = apps.get_class('attachments.abstract_models', 'AbstractAttachment')
AbstractAttachmentCategory = apps.get_class('attachments.abstract_models', 'AbstractAttachmentCategory')


class Attachment(AbstractAttachment):
    pass

class AttachmentCategory(AbstractAttachmentCategory):
    pass

