#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json as sjson
from aiohttp import web
from peewee import SqliteDatabase

import models

__author__ = 'SunCoder'

APP_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_PATH,'fanhao.db')
PHOTO_PATH = os.path.join(APP_PATH, 'photos')
STATIC_PATH = os.path.join(APP_PATH, 'static')

def initsys():
    if not os.path.exists(PHOTO_PATH):
        os.mkdir(PHOTO_PATH)

    if not os.path.exists(DB_PATH):
        db = SqliteDatabase(os.path.join(APP_PATH, 'fanhao.db'))
        db.create_table(models.fanhao)
        db.close()


def json(code, msg='', data='', callback=None):
    json_data = {
        'code': code,
        'msg': msg,
        'data': data
    }
    return json_data


def rjson(code, msg='', data='', callback=None):
    json_data = {
        'code': code,
        'msg': msg,
        'data': data
    }
    jsonstr = sjson.dumps(json_data)
    return web.Response(body=bytes(jsonstr, encoding="utf-8"),content_type='text/html')


class Pager():
    url = ''
    total = 0
    index = 1
    size = 15
    pages = []

    def __init__(self, total, index, size):
        '''
        分页函数
        :param count: 总数
        :param index: 页码
        :param size: 页容量
        :return: object paging
        '''
        self.total = total
        self.index = index
        self.size = size
        self.count, tail = divmod(total, size)
        if tail is not 0: self.count += 1

    def render(self):

        self.pages.clear()
        self.pages.append('<nav><ul class="pagination">')

        rag = range(0, self.count)
        if self.count > 10:
            if self.index <= 5:
                rag = rag[0: 10]
            elif self.index > 5:
                if self.count - self.index < 5:
                    rag = rag[-10:]
                else:
                    rag = rag[self.index - 5:self.index + 5]

        if self.index == 1:
            self.pages.append('<li class="disabled"><span>第1页</a></li>')
            self.pages.append('<li class="disabled"><span>&laquo;</a></li>')
        else:
            self.pages.append('<li><a href="javascript:goPage(%s);">第1页</a></li>' % 1)
            self.pages.append('<li><a href="javascript:goPage(%s);">&laquo;</a></li>' % (self.index - 1))

        for i in rag:
            v = i + 1
            if self.index == v:
                self.pages.append('<li class="active"><span>%s</span></li>' % (v if v > 9 else ('0%s' % v)))
            else:
                self.pages.append('<li><a href="javascript:goPage(%s);">%s</a></li>' % (v, (v if v > 9 else ('0%s' % v))))

        if self.index == self.count:
            self.pages.append('<li class="disabled"><span>&raquo;</span></li>')
            self.pages.append('<li class="disabled"><span>第%s页</span></li>' % self.count)
        else:
            self.pages.append('<li><a href="javascript:goPage(%s);">&raquo;</a></li>' % (self.index + 1))
            self.pages.append('<li><a href="javascript:goPage(%s);">第%s页</a></li>' % (self.count, self.count))

        self.pages.append('<li><span>共%s个</span></li></ul></nav>' % self.total)
        return "".join(self.pages)

    def __str__(self):
        return self.render()


if __name__ == '__main__':
    print(Pager(202, 10, 4))
    print(Pager(202, 2, 4))
    print(Pager(202, 50, 4))
    print(Pager(10, 2, 3))
    print(Pager(10, 3, 3))
