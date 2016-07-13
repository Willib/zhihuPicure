# -*-coding:utf-8 -*-

import requests
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
    print
    "Cookie 未能加载"


def get_xsrf():
    '''''_xsrf 是一个动态变化的参数'''
    index_url = "http://www.zhihu.com"
    index_page = session.get(index_url, headers=headers)
    html = index_page.text
    pattern = r'name="_xsrf" value="(.*?)"'
    _xsrf = re.findall(pattern, html)
    return _xsrf[0]


def get_captcha():
    t = str(int(time.time() * 1000))
    captcha_url = 'http://www.zhihu.com/captcha.gif?r' + t + "&type=login"
    print
    captcha_url
    r = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print
        u'captcha.jpg 所在目录:%s, 手动输入' % os.path.abspath('captcha.jpg')
    captcha = input("input captcha\n")
    return captcha


def isLogin():
    url = "https://www.zhihu.com/settings/profile"
    login_code = session.get(url, allow_redirects=False).status_code
    print
    "login code: ", login_code
    if int(x=login_code) == 200:
        return True
    else:
        return False


def login(secret, account):
    if re.match(r"^1\d{10}$", account):
        print
        "手机号登陆\n"
        post_url = 'http://www.zhihu.com/login/phone_num'
        postdata = {
            '_xsrf': get_xsrf(),
            'password': secret,
            'remember_me': 'true',
            'phone_num': account,
        }
    else:
        print
        '邮箱登录\n'
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
        print
        login_page.status
        print
        login_code
        print
        'what?'
    except:
        print
        '需要验证码'
        postdata['captcha'] = get_captcha()
        login_page = session.post(post_url, data=postdata, headers=headers)
        login_code = eval(login_page.text)  # eval 从字符串中提取字典
        u = login_code['msg']
    session.cookies.save()


def getPageCode(pageUrl):
    try:
        req = session.get(pageUrl, headers=headers)
        print
        req.request.headers
        return req.text
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print
            u"打开链接失败...", e.reason
            return None


def getImageUrl(pageUrl):
    pageCode = getPageCode(pageUrl)
    if not pageCode:
        print
        "打开网页链接失败.."
        return None
    pattern = re.compile('<a class="author-link".*?<span title=.*?<div class="zh-summary.*?' +
                         '<div class="zm-editable-content.*?>(.*?)</div>', re.S)
    items = re.findall(pattern, pageCode)
    imagesUrl = []
    pattern = re.compile('data-actualsrc="(.*?)">', re.S)
    for item in items:
        urls = re.findall(pattern, item)
        imagesUrl.extend(urls)
    for url in imagesUrl:
        print
        url
    return imagesUrl


def saveImagesFromUrl(pageUrl, filePath):
    imagesUrl = getImageUrl(pageUrl)
    if not imagesUrl:
        print
        'imagesUrl is empty'
        return
    nameNumber = 0;
    for image in imagesUrl:
        suffixNum = image.rfind('.')
        suffix = image[suffixNum:]
        fileName = filePath + os.sep + str(nameNumber) + suffix
        nameNumber += 1
        print
        'save in: ', fileName
        response = requests.get(image)
        contents = response.content
        try:
            with open(fileName, "wb") as pic:
                pic.write(contents)
        except IOError:
            print
            'Io error'


login('这里是密码', '这里是你的知乎账户')
saveImagesFromUrl('https://www.zhihu.com/question/46435597', '/Volumes/HDD/image')