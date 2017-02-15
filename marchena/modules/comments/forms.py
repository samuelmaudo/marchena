# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from time import time

from django import forms
from django.core.exceptions import FieldDoesNotExist
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.translation import ugettext_lazy as _

from yepes.apps import apps
from yepes.conf import settings
from yepes.contrib.registry import registry

Comment = apps.get_model('comments', 'Comment')


class CommentForm(forms.Form):

    error_messages = {
        'invalid_honeypot': _('If you enter anything in this field your comment will be treated as spam.'),
        'invalid_security_hash': _('Security hash check failed.'),
        'invalid_timestamp': _('Timestamp check failed'),
    }
    field_names = [
        ('timestamp', 'timestamp'),
        ('security_hash', 'security_hash'),
        ('honeypot', None),
        ('name', 'author_name'),
        ('email', 'author_email'),
        ('url', 'author_url'),
        ('comment', 'content'),
    ]

    def __init__(self, post, data=None, initial=None, **kwargs):
        self.post = post
        self.field_aliases = {
            name: alias
            for alias, name
            in self.field_names
        }
        self.error_messages = {}
        for cls in reversed(self.__class__.__mro__):
            messages = getattr(cls, 'error_messages', None)
            if messages is not None:
                self.error_messages.update(messages)

        security_data = self.generate_security_data()
        if initial is None:
            initial = security_data
        else:
            initial.update(security_data)

        super(CommentForm, self).__init__(data=data, initial=initial, **kwargs)

        for alias, name in self.field_names:
            if name is None:
                field = forms.CharField(required=False)
            elif name == 'timestamp':
                field = forms.IntegerField(widget=forms.HiddenInput)
            elif name == 'security_hash':
                field = forms.CharField(min_length=40, max_length=40, widget=forms.HiddenInput)
            else:
                db_field = Comment._meta.get_field(name)
                if (name == 'content'
                        and (db_field.max_length is None
                                or db_field.max_length < registry['comments:MAX_LENGTH'])):
                    field = db_field.formfield(max_length=registry['comments:MAX_LENGTH'])
                else:
                    field = db_field.formfield()

            self.fields[alias] = field

    def clean_security_hash(self):
        """
        Check the security hash.
        """
        timestamp = self.data.get(self.field_aliases['timestamp'])
        actual_hash = self.cleaned_data[self.field_aliases['security_hash']]
        expected_hash = self.generate_security_hash(timestamp)
        if not constant_time_compare(actual_hash, expected_hash):
            raise forms.ValidationError(self.error_messages['invalid_security_hash'])
        else:
            return actual_hash

    def clean_timestamp(self):
        """
        Make sure the timestamp isn't too far (default is > 2 hours) in the past.
        """
        timestamp = self.cleaned_data[self.field_aliases['timestamp']]
        if (time() - timestamp) > settings.COMMENT_TIMEOUT:
            raise forms.ValidationError(self.error_messages['invalid_timestamp'])
        else:
            return timestamp

    def full_clean(self):
        super(CommentForm, self).full_clean()
        if not self.is_bound:
            return  # Stop further processing.

        for alias, name in self.field_names:

            # Check that nothing's been entered into the honeypots.
            if name is None:
                initial = self.initial.get(name)
                value = self.cleaned_data[alias]
                if ((initial is None and value)
                        or (initial is not None and value != initial)):
                    msg = self.error_messages['invalid_honeypot']
                    self.add_error(alias, forms.ValidationError(msg))
                continue

            # Call the cleaner methods by the field's name.
            if name != alias:
                method_name = '_'.join(('clean', name))
                method = getattr(self, method_name, None)
                if method is not None:
                    try:
                        value = method()
                    except forms.ValidationError as e:
                        self.add_error(alias, e)
                    else:
                        self.cleaned_data[alias] = value

            # Get the model fields, clean them and store the validation errors.
            try:
                field = Comment._meta.get_field(name)
            except FieldDoesNotExist:
                continue

            raw_value = self.cleaned_data.get(alias)
            if field.blank and raw_value in field.empty_values:
                continue

            try:
                value = field.clean(raw_value, None)
            except forms.ValidationError as e:
                self.add_error(alias, e)
            else:
                self.cleaned_data[alias] = value

    def generate_security_data(self):
        """
        Generate a dict of security data for "initial" data.
        """
        timestamp = int(time())
        security_hash = self.generate_security_hash(timestamp)
        security_data = {
            self.field_aliases['timestamp']: timestamp,
            self.field_aliases['security_hash']: security_hash,
        }
        return security_data

    def generate_security_hash(self, timestamp):
        """
        Generate the initial security hash from self.content_object
        and a (unix) timestamp.
        """
        info = (
            settings.SECRET_KEY[0::2],
            self.post.guid,
            timestamp,
        )
        salt = settings.SECRET_KEY[1::2]
        value = '|'.join(str(i) for i in info)
        return salted_hmac(salt, value).hexdigest()

    def get_comment_data(self):
        if not self.errors:
            data = {
                name: self.cleaned_data[alias]
                for alias, name
                in self.field_names
            }
            return data
        else:
            return None

