#!/usr/bin/env python
# coding=utf-8

import math
from flask import url_for

"""
pagination
"""

__author__ = 'Rnd495'


class Pagination(object):
    def __init__(self, sqlite, handler_name, static_params, index=0, size=10):
        self.handler_name = handler_name
        self.static_params = static_params
        self.sqlite = sqlite
        self.index = max(0, index)
        self.size = max(1, size)

        self.total_items = sqlite.count()
        self.index = min(self.total_items - 1, self.index)
        self.total_page = int(math.ceil(self.total_items / float(self.size)))

        self.offset = self.index * self.size
        self.limit = self.size

        self.items = self.sqlite.offset(self.offset).limit(self.limit).all()

    @property
    def pre_url(self):
        new_index = max(0, self.index - 1)
        return url_for(self.handler_name, index=new_index, size=self.size, **self.static_params)

    @property
    def next_url(self):
        new_index = min(self.total_page - 1, self.index + 1)
        return url_for(self.handler_name, index=new_index, size=self.size, **self.static_params)

    @property
    def has_pre(self):
        return self.index > 0

    @property
    def has_next(self):
        return self.index < self.total_page - 1

    @property
    def single_page(self):
        return self.total_items <= self.size
