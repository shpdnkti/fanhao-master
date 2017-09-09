#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import re, os
from urllib import request
from urllib.error import HTTPError
import time
# from PIL import Image  # pillow

from Base import *
from models import fanhao

__author__ = 'SunCoder'

ptCode = re.compile(r'<span class="header">識別碼:</span>.*?<span style="color:#CC0000;">(.*?)</span>', re.I | re.S | re.M)
psTitle = re.compile(r'<h3>(.*?)</h3>', re.I | re.S | re.M)
psStarCode = re.compile(r'<div class="star-name"><a href="https://www.javbus.info.*?star/(.*?)" title=".*?">.*?</a></div>', re.I | re.S | re.M)
psStar = re.compile(r'<div class="star-name"><a href="https://www.javbus.info.*?star/.*?" title=".*?">(.*?)</a></div>', re.I | re.S | re.M)
ptImg = re.compile(r'<a class="bigImage" href="(.*?)">', re.I | re.S | re.M)


def opener():
    topener = request.build_opener()
    opener.addheaders = [("authority", "www.javbus.info")]
    # opener.addheaders = [("method", "GET")]
    # opener.addheaders = [("path", "/HEYZO-0282")]
    # opener.addheaders = [("scheme", "https")]
    # opener.addheaders = [("accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")]
    # opener.addheaders = [("dnt", "1")]
    # opener.addheaders = [("upgrade-insecure-requests", "1")]
    topener.addheaders = [("user-agent", "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36")]
    return topener


def getInfo(fcode,onlyImg=False):
    if not fcode: return json(-1, '番号不正确')
    # 解析番号
    if not onlyImg:
        fcode = fcode.strip().upper().encode('utf-8').decode('utf-8')
        match = re.match(r'[0-9a-zA-Z-_]+', fcode)
        if not match: return json(-1, '番号不正确')
    # 获取信息
    resdata = _request(fcode)
    if resdata['code'] != 0: return json(-1, '番号信息获取失败:'+resdata['msg'])
    resdata = resdata['data']
    # 保存图片
    resimg = _saveImg(resdata['imgsrc'], resdata['filename'])
    if resimg == None : return json(-4, '图片信息保存错误')
    if resimg['code'] != 0: return json(-5, '图片信息保存失败:'+resimg['msg'])
    # 保存信息
    resinf = _saveInf(resdata)
    if resinf == None : return json(-2, '番号信息保存错误')
    if resinf['code'] != 0: return json(-3, '番号信息保存失败:'+resinf['msg'])

    return json(0, '获取成功',{'code': fcode, 'title': resdata['title'],'starcode':resdata['starcode'], 'star': resdata['star'], 'imgsrc': resdata['imgsrc'], 'filename': resdata['filename']})


def _saveInf(infoData):
    try:
        fhinfo = fanhao.get(fanhao.code == infoData['code'])
    except fanhao.DoesNotExist:
        fhinfo = fanhao()
    # try:
    fhinfo.code = infoData['code']
    fhinfo.title = infoData['title']
    fhinfo.star = infoData['star']
    fhinfo.starcode = infoData['starcode']
    fhinfo.img = infoData['imgsrc']
    fhinfo.fname = infoData['filename']
    fhinfo.ima = 0
    # fhinfo.updateTime = int(time.time())
    fhinfo.save()
    return json(0)
    # except:
    #     json(-1, '保存失败')


def _saveImg(imgsrc, fname):
    try:
        rs = opener().open(imgsrc, timeout=30)
        rs = rs.read()
    except Exception as e:
        return json(-1, '网络错误')

    fpath = os.path.join(PHOTO_PATH, fname)

    try:
        with open(fpath,'wb') as op:
            op.write(rs)
    except Exception:
        return json(-1, '保存到本地服务器失败')

    return json(0, '保存成功')


def _request(fcode, tims=0):
    url = 'https://www.javbus.info/' + fcode
    try:
        res = opener().open(url, timeout = 30)
        html = res.read()
    except Exception as e:
        # return json(-1, '网络错误')
        tims += 1
        if tims == 3: return json(-1, '网络错误')
        return _request(fcode, tims)

    html = html.decode('UTF-8')
    title = _domatch(psTitle, html)
    starcode = _domatch(psStarCode,html)
    star = _domatch(psStar,html)
    imgsrc = _domatch(ptImg, html)
    filename = fcode + '.jpg'  # os.path.splitext(imgsrc)[1]

    return json(0, ',', {'code': fcode, 'title': title,'starcode':starcode, 'star': star, 'imgsrc': imgsrc, 'filename': filename})


def _domatch(rec, htmls):
    mh = rec.findall(htmls)
    if mh and len(mh) > 0:
        return mh[0]
    else:
        return ''


if __name__ == '__main__':
    res = getInfo('IPZ-135')
    # res = _request('IPZ-135')
    # print(_saveStar(res['data']['star'],res['data']['name']))
    print(res)


