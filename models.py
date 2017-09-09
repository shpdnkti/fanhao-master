#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'SunCoder'

import datetime
from peewee import *
from Base import *

db = SqliteDatabase(DB_PATH)
#db = MySQLDatabase(host='192.168.31.130', user='root', passwd='root', database='fanhao', charset='utf8', port=3306)

class fanhao(Model):
    id = PrimaryKeyField(primary_key=True)
    code = CharField(64)
    title = CharField(128)
    star = CharField(64,null=True)
    starcode = CharField(64,null=True)
    img = CharField(128,null=True)
    fname = CharField(128,null=True)
    ima = BooleanField(default=0)
    downed = BooleanField(default=0)
    # updateTime = IntegerField(default=int(time.time()))
    updateTime = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
