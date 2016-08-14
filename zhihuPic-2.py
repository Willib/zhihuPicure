# -*-coding:utf-8 -*-

import requests
from requests.adapters import HTTPAdapter
# import urllib
# import urllib2
import cookielib
import re
import time
import os.path
from PIL import Image


user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
headers = {'User-Agent': user_agent}

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print "Cookie 未能加载"

def get_xsrf():
    '''_xsrf 是一个动态变化的参数'''
    index_url = "http://www.zhihu.com"
    index_page = session.get(index_url, headers=headers)
    html = index_page.text
    pattern = r'name="_xsrf" value="(.*?)"'
    _xsrf = re.findall(pattern, html)
    return _xsrf[0]

def get_captcha():
    t = str(int(time.time() * 1000))
    captcha_url = 'http://www.zhihu.com/captcha.gif?r' + t + "&type=login"
    print captcha_url
    r = session.get(captcha_url, headers = headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print u'captcha.jpg 所在目录:%s, 手动输入'% os.path.abspath('captcha.jpg')
    captcha = input("input captcha\n")
    return captcha

def isLogin():
    url = "https://www.zhihu.com/settings/profile"
    login_code = session.get(url, allow_redirects=False).status_code
    print "login code: ", login_code
    if int(x=login_code) == 200:
        return True
    else:
        return False

def login(secret, account):
    if isLogin():
        print "已经登录"
        return
    if re.match(r"^1\d{10}$", account):
        print "手机号登陆\n"
        post_url = 'http://www.zhihu.com/login/phone_num'
        postdata = {
            '_xsrf': get_xsrf(),
            'password': secret,
            'remember_me': 'true',
            'phone_num': account,
        }
    else:
        print '邮箱登录\n'
        post_url = 'http://www.zhihu.com/login/email'
        postdata = {
            '_xsrf': get_xsrf(),
            'password': secret,
            'remember_me': 'true',
            'email': account,
        }
    try:
        login_page = session.post(post_url, data=postdata, headers=headers)
        login_code = login_page.text
        print login_page.status
        print login_code
        print 'what?'
    except:
        print '需要验证码'
        postdata['captcha'] = get_captcha()
        login_page = session.post(post_url, data=postdata, headers=headers)
        login_code = eval(login_page.text)   #eval 从字符串中提取字典
        u = login_code['msg']
    session.cookies.save()


def getImageUrl():
    url = "https://www.zhihu.com/node/QuestionAnswerListV2"
    method = 'next'
    size = 10
    allImageUrl = []

    #循环直至爬完整个问题的回答
    while(True):
        print '===========offset: ', size
        postdata = {
            'method': 'next',
            'params': '{"url_token":' + str(46435597) + ',"pagesize": "10",' +\
                      '"offset":' + str(size) + "}",
            '_xsrf':get_xsrf(),

        }
        size += 10
        page = session.post(url, headers=headers, data=postdata)
        ret = eval(page.text)
        listMsg = ret['msg']

        if not listMsg:
            print "图片URL获取完毕, 页数: ", (size-10)/10
            return allImageUrl
        pattern = re.compile('data-actualsrc="(.*?)">', re.S)
        for pageUrl in listMsg:
            items = re.findall(pattern, pageUrl)
            for item in items:      #这里去掉得到的图片URL中的转义字符'\\'
                imageUrl = item.replace("\\", "")
                allImageUrl.append(imageUrl)


def saveImagesFromUrl(filePath):
    imagesUrl = getImageUrl()
    print "图片数: ", len(imageUrl)
    if not imagesUrl:
        print 'imagesUrl is empty'
        return
    nameNumber = 0;
    for image in imagesUrl:
        suffixNum = image.rfind('.')
        suffix = image[suffixNum:]
        fileName = filePath + os.sep + str(nameNumber) + suffix
        nameNumber += 1
        try:
            # 设置超时重试次数及超时时间单位秒
            session.mount(image, HTTPAdapter(max_retries=3))
            response = session.get(image, timeout=20)
            contents = response.content
            with open(fileName, "wb") as pic:
                pic.write(contents)

        except IOError:
            print 'Io error'
        except requests.exceptions.ConnectionError:
            print '连接超时,URL: ', image
    print '图片下载完毕'

login('这是你的知乎密码','这是你的知乎账户')
saveImagesFromUrl('/Volumes/HDD/Picture')