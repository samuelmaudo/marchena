#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import tempfile

from django.utils._os import upath

from yepes.test.program import TestProgram


program = TestProgram(
    workingDir=os.path.abspath(os.path.dirname(upath(__file__))),
    tempDir=tempfile.mkdtemp(prefix='marchena_'),
    subdirsToSkip=[
        'requirements',
        'templates',
    ],
    alwaysInstalledApps=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sites',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.admin.apps.SimpleAdminConfig',
        'django.contrib.staticfiles',
        'mptt',
        'yepes',
        'yepes.contrib.registry',
        'yepes.contrib.sitemaps',
        'yepes.contrib.slugs',
        'yepes.contrib.thumbnails',
        'marchena',
        'marchena.modules.attachments',
        'marchena.modules.authors',
        'marchena.modules.blogs',
        'marchena.modules.comments',
        'marchena.modules.links',
        'marchena.modules.posts',
    ],
    alwaysMiddlwareClasses=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ],
)


if __name__ == '__main__':
    failures = program.run()
    if failures > 0:
        sys.exit(True)

