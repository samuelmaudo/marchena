# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase

from marchena.modules.attachments.models import Attachment
from marchena.modules.attachments.processors import attachment_tags


class AttachmentTagsTest(TestCase):

    def setUp(self):
        self.attachment = Attachment.objects.create(
            title='Example',
            external_file='http://www.example.org/')

    def test_audio_tag(self):
        self.assertHTMLEqual("""
            <audio src="http://www.example.org/" controls preload="none">
              <a href="http://www.example.org/" download>
                Example
              </a>
            </audio>
        """, self.attachment.get_audio_tag())

        self.assertHTMLEqual("""
            <audio id="id" class="class" src="http://www.example.org/" controls preload="none">
              <a href="http://www.example.org/" download>
                Example
              </a>
            </audio>
        """, self.attachment.get_audio_tag(cls='class', id='id'))

        self.assertHTMLEqual("""
            <audio src="http://www.example.org/" controls preload="auto">
              <a href="http://www.example.org/" download>
                Example
              </a>
            </audio>
        """, self.attachment.get_audio_tag(preload='auto'))

    def test_file_link(self):
        self.assertHTMLEqual("""
            <a href="http://www.example.org/" download>
              Example
            </a>
        """, self.attachment.get_file_link())

        self.assertHTMLEqual("""
            <a id="id" class="class" href="http://www.example.org/" download>
              Example
            </a>
        """, self.attachment.get_file_link(cls='class', id='id'))

        self.assertHTMLEqual("""
            <a href="http://www.example.org/">
              Example
            </a>
        """, self.attachment.get_file_link(download=False))

    def test_iframe_tag(self):
        self.assertHTMLEqual("""
            <iframe src="http://www.example.org/" width="640" height="360" frameborder="0" allowfullscreen mozallowfullscreen webkitallowfullscreen>
              <a href="http://www.example.org/" download>
                Example
              </a>
            </iframe>
        """, self.attachment.get_iframe_tag())

        self.assertHTMLEqual("""
            <iframe id="id" class="class" src="http://www.example.org/" width="640" height="360" frameborder="0" allowfullscreen mozallowfullscreen webkitallowfullscreen>
              <a href="http://www.example.org/" download>
                Example
              </a>
            </iframe>
        """, self.attachment.get_iframe_tag(cls='class', id='id'))

        self.assertHTMLEqual("""
            <iframe src="http://www.example.org/" width="640" height="360" frameborder="0">
              <a href="http://www.example.org/" download>
                Example
              </a>
            </iframe>
        """, self.attachment.get_iframe_tag(allowfullscreen=False, mozallowfullscreen=False, webkitallowfullscreen=False))

        text = '[iframe style="width:100%"]{0}[/iframe]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_iframe_tag(style='width:100%'))

    def test_image_tag(self):
        self.assertHTMLEqual("""
            <img src="http://www.example.org/" alt="Example">
        """, self.attachment.get_image_tag())

        self.assertHTMLEqual("""
            <img id="id" class="class" src="http://www.example.org/" alt="Example">
        """, self.attachment.get_image_tag(cls='class', id='id'))

        self.assertHTMLEqual("""
            <img src="http://www.example.org/" alt="Image">
        """, self.attachment.get_image_tag(alt='Image'))

    def test_video_tag(self):
        self.assertHTMLEqual("""
            <video src="http://www.example.org/" width="640" height="360" controls preload="metadata">
              <a href="http://www.example.org/" download>
                Example
              </a>
            </video>
        """, self.attachment.get_video_tag())

        self.assertHTMLEqual("""
            <video id="id" class="class" src="http://www.example.org/" width="640" height="360" controls preload="metadata">
              <a href="http://www.example.org/" download>
                Example
              </a>
            </video>
        """, self.attachment.get_video_tag(cls='class', id='id'))

        self.assertHTMLEqual("""
            <video src="http://www.example.org/" width="640" height="360" controls preload="auto">
              <a href="http://www.example.org/" download>
                Example
              </a>
            </video>
        """, self.attachment.get_video_tag(preload='auto'))


class TextProcessorTest(TestCase):

    def setUp(self):
        self.attachment = Attachment.objects.create(
            title='Example',
            external_file='http://www.example.org/')

    def test_audio_tag(self):
        text = '[audio]{0}[/audio]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_audio_tag())

        text = '[audio={0}]Audio file[/audio]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_audio_tag())

        text = '[audio class1 class2 #id]{0}[/audio]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_audio_tag(cls='class1 class2', id='id'))

        text = '[audio preload=auto]{0}[/audio]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_audio_tag(preload='auto'))

        text = '[audio style="width:100%"]{0}[/audio]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_audio_tag(style='width:100%'))

    def test_file_link(self):
        text = '[link]{0}[/link]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_file_link())

        text = '[link={0}]File link[/link]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_file_link(text='File link'))

        text = '[link class1 class2 #id]{0}[/link]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_file_link(cls='class1 class2', id='id'))

        text = '[link preload=auto]{0}[/link]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_file_link(preload='auto'))

        text = '[link style="width:100%"]{0}[/link]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_file_link(style='width:100%'))

    def test_iframe_tag(self):
        text = '[iframe]{0}[/iframe]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_iframe_tag())

        text = '[iframe={0}]Iframe file[/iframe]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_iframe_tag())

        text = '[iframe class1 class2 #id]{0}[/iframe]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_iframe_tag(cls='class1 class2', id='id'))

        text = '[iframe preload=auto]{0}[/iframe]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_iframe_tag(preload='auto'))

        text = '[iframe style="width:100%"]{0}[/iframe]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_iframe_tag(style='width:100%'))

    def test_image_tag(self):
        text = '[image]{0}[/image]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_image_tag())

        text = '[image={0}]Image file[/image]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_image_tag(alt='Image file'))

        text = '[image class1 class2 #id]{0}[/image]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_image_tag(cls='class1 class2', id='id'))

        text = '[image preload=auto]{0}[/image]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_image_tag(preload='auto'))

        text = '[image style="width:100%"]{0}[/image]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_image_tag(style='width:100%'))

    def test_video_tag(self):
        text = '[video]{0}[/video]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_video_tag())

        text = '[video={0}]Video file[/video]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_video_tag())

        text = '[video class1 class2 #id]{0}[/video]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_video_tag(cls='class1 class2', id='id'))

        text = '[video preload=auto]{0}[/video]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_video_tag(preload='auto'))

        text = '[video style="width:100%"]{0}[/video]'
        tag = attachment_tags(text.format(self.attachment.guid))
        self.assertHTMLEqual(tag, self.attachment.get_video_tag(style='width:100%'))

