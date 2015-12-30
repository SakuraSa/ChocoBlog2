#!/usr/bin/env python
# coding=utf-8

import jinja2
import misaka
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from core.application import app

"""
jinja_filters
"""

__author__ = 'Rnd495'


class HighlighterRenderer(misaka.HtmlRenderer):
    def blockcode(self, text, lang):
        if not lang:
            return '\n<pre><code>{}</code></pre>\n'.format(text.strip())

        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter()

        return highlight(text, lexer, formatter)


MARKDOWN = misaka.Markdown(
        HighlighterRenderer(),
        extensions=misaka.EXT_FENCED_CODE | misaka.EXT_TABLES | misaka.EXT_MATH | misaka.EXT_STRIKETHROUGH)


@app.template_filter('markdown')
def safe_markdown(content):
    return jinja2.Markup(MARKDOWN(content))


@app.template_filter('datetime_format')
def datetime_format(time):
    return time.strftime('%b %d, %Y')
