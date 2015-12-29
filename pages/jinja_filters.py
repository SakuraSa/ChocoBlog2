#!/usr/bin/env python
# coding=utf-8

import jinja2
import markdown2

from core.application import app

"""
jinja_filters
"""

__author__ = 'Rnd495'


MARKDOWN = markdown2.Markdown(extras=['fenced-code-blocks', 'footnotes', 'tables'])


@app.template_filter('markdown')
def safe_markdown(content):
    return jinja2.Markup(MARKDOWN.convert(content))


@app.template_filter('datetime_format')
def datetime_format(time):
    return time.strftime('%b %d, %Y')
