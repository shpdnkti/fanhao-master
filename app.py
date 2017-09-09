#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'SunCoder'

import logging

import asyncio, os
import models
import platform
from aiohttp import web
from jinja2 import Environment, FileSystemLoader

from Base import *
from models import fanhao
import searcher
logging.basicConfig(level=logging.INFO)

env = Environment(loader=FileSystemLoader(os.path.join(APP_PATH, 'templates')))


def render(tempname, *args, **kwargs):
    template = env.get_template(tempname)
    html = template.render(*args, **kwargs)
    return html


async def index(request):
    requestdata = {}

    pageindex = request.GET.get('pageindex')
    if not pageindex:
        pageindex = 1
    else:
        pageindex = int(pageindex)
    requestdata['pageindex'] = pageindex

    pagesize = request.GET.get('pagesize')
    if not pagesize:
        pagesize = 15
    else:
        pagesize = int(pagesize)
    requestdata['pagesize'] = pagesize

    ps = fanhao.select()

    downed = request.GET.get('downed')
    if downed:
        ps = ps.where(fanhao.downed == downed)
        requestdata['downed'] = downed

    code = request.GET.get('code')
    if code:
        ps = ps.where(fanhao.code == code)
        requestdata['code'] = code

    ma = request.GET.get('ma')
    if ma == '0' or ma == '1' or ma == '2':
        ps = ps.where(fanhao.ima == ma)
        requestdata['ma'] = ma

    star = request.GET.get('star')
    if star:
        if star == '-1':
            star = ''
        ps = ps.where(fanhao.star == star)
        requestdata['star'] = star

    count = ps.count()

    pc = fanhao.select(fanhao.code).order_by(fanhao.code.asc())
    ss = fanhao.select(fanhao.starcode,fanhao.star).group_by(fanhao.star)#.order_by(fanhao.code.asc())
    ps = ps.order_by(fanhao.id.desc()).paginate(pageindex, pagesize)
    pager = Pager(count, pageindex, pagesize)

    html = render('index.html', {'pc': pc,'ss':ss, 'ps': ps, 'requestdata': requestdata, 'pagehtml': pager.render()})
    return web.Response(body=bytes(html, encoding="utf-8"), content_type='text/html')


async def search(request):
    xcode = request.GET.get('xcode')
    if not xcode:
        return rjson(0)
    try:
        ps = fanhao.get(fanhao.code == xcode)
        return rjson(1, '已存在', ps.code)
    except fanhao.DoesNotExist:
        pass

    res = searcher.getInfo(xcode)
    if res['code'] == 0:
        return rjson(0, '获取成功', res['data'])
    else:
        return rjson(-1, '获取失败:' + res['msg'], res['data'])


async def regetImg(request):
    xcode = request.GET.get('xcode')
    if not xcode:
        return rjson(-1, 'xcode err')

    res = searcher.getInfo(xcode,True)
    if res['code'] == 0:
        return rjson(0, '重新获取成功',res['data'])
    else:
        return rjson(-1, '重新获取失败:' + res['msg'])


async def deimg(request):
    pid = request.GET.get('pid')
    if not pid:
        return rjson(-1, 'xcode err')

    try:
        rs = fanhao.get(fanhao.id == pid)
        rs.delete_instance()
        if os.path.exists(os.path.join(PHOTO_PATH, rs.code + '.jpg')):
            os.remove(os.path.join(PHOTO_PATH, rs.code + '.jpg'))
        return rjson(0, 'ok', '删除成功')
    except fanhao.DoesNotExist:
        pass


async def ima(request):
    id = request.match_info.get('id')
    val = request.match_info.get('val')
    if not id or not val:
        return rjson(1, 'args err')
    try:
        f = models.fanhao.get(models.fanhao.id == id)
        f.ima = int(val)
        f.save()
        return rjson(0, 'ok')
    except models.fanhao.DoesNotExist:
        return rjson(1, 'not exist')


async def checkfile(request):
    resdata = []

    # 获取本地封面信息
    imgloclist = [(os.path.splitext(x)[0]).upper() for x in os.listdir(PHOTO_PATH) if x != '.' and x != '..']
    imgloclist.sort()
    resdata.append(','.join(imgloclist))
    resdata.append('imgloclist end ' + str(len(imgloclist)))
    # 获取数据库信息
    ps = fanhao.select()
    datalist = list(x.code for x in ps)
    datalist.sort()
    resdata.append(','.join(datalist))
    resdata.append('datalist end ' + str(len(datalist)))
    # 清理删除后的图像
    dellist = []
    for p in imgloclist:
        if p not in datalist:
            os.remove(PHOTO_PATH + '/' + p + '.jpg')
            dellist.append('del loc ' + p + '.jpg')

    if dellist:
        resdata.append(','.join(dellist))
    else:
        resdata.append('没有删除的封面')
    return rjson(0, 'ok', resdata)


async def manage(request):
    ps = fanhao.select(fanhao.id, fanhao.code).order_by(fanhao.code)
    html = render('manage.html', {'ps': ps})
    return web.Response(body=bytes(html, encoding='utf-8'))


async def init(loop):
    app = web.Application(loop=loop, debug=True)
    app.router.add_route('*', '/', index)
    app.router.add_route('*', '/search', search)
    app.router.add_route('*', '/recode', regetImg)
    app.router.add_route('*', '/deimg', deimg)
    app.router.add_route('GET', '/ima/{id}/{val}', ima)
    app.router.add_route('*', '/checkfile', checkfile)
    app.router.add_route('*', '/m', manage)

    app.router.add_static('/static', STATIC_PATH)
    app.router.add_static('/photos', PHOTO_PATH)

    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 8004)
    logging.info('system start at port http://127.0.0.1:8004...')
    return srv


if __name__ == '__main__':
    initsys()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()

