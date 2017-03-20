#!/usr/bin/env python
#-*- coding: utf-8 -*-
# @Author: hkk
# @Date:   2015-11-20 11:51:48
# @Last Modified by:   anchen
# @Last Modified time: 2015-12-09 12:39:44
import ssl, re, pdb, time, json, cookielib
import urllib2,requests
import httplib,socket
import xml.etree.ElementTree as xmltree
from . import utils
from .message import produce_msg
ssl._create_default_https_context = ssl._create_unverified_context

class WeChat(object):
    """docstring for ClassName"""

    loginInfo = {'BaseRequest':{}}
    header = {
            'ContentType': 'application/json; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
            }
    prehost = 'https://wx.qq.com/cgi-bin/mmwebwx-bin'
    contact = None
    def __init__(self):
        self.cj = cookielib.LWPCookieJar() 
        cookie_support = urllib2.HTTPCookieProcessor(self.cj)
        #创建一个opener，将保存了cookie的http处理器，还有设置一个handler用于处理http的URL的打开
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        # 将包含了cookie、http处理器、http的handler的资源和urllib2对象板顶在一起
        urllib2.install_opener(opener)
        self.s = requests.Session()
        self.robot = ChatRobot()

    def genQrcodeUuid(self):

        url = "https://login.weixin.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN"
        #url = 'https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_=1488425933108'
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
            
        return res[50:62]
    def ScanStauts(self,uuid):
        #返回200：手机已确认登入；返回201：等待手机确认；返回408：还未确认或者还未扫码；返回400：二维码失效
        #https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=QelLRKlwVA==&tip=1
        try:
            url = "https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid="+uuid+"&tip=1"
            req = urllib2.Request(url)
            res_data = urllib2.urlopen(req)
            res = res_data.read()
            return res           
        except ssl.SSLError as e:
            return 'window.code=408;'

    def GetWeChatCookies(self,url):
        if 'wx2.qq.com' in url:
            HOSTNAME = 'wx2.qq.com'
        else:
            HOSTNAME = 'wx.qq.com'
        #parm = url[18:]
        #conn = httplib.HTTPSConnection(HOSTNAME)
        #conn.putrequest('GET', url)
        #conn.endheaders()
        #response = conn.getresponse()
        r = self.s.get(url, headers=self.header, allow_redirects=False)
        xt = xmltree.fromstring(r.text)
        if '0' == xt.findtext('ret'):
            response_keys = ('ret', 'message', 'skey', 'wxsid', 'wxuin', 'pass_ticket', 'isgrayscale')
            for k in response_keys:
                self.loginInfo[k] = xt.findtext(k)
            self.login()
            msg = dict()
            msg['COOKIES'] = self.loginInfo['cookies'] = r.headers['Set-Cookie']
            msg['MSG'] = r.text
            return msg
        else:
            print "error return"
            return None

    def login(self):
        self.loginInfo['deviceid'] = 'e93jfdsaensdf1q'
        self.weChatInit()
        self.weChatStatusNotify()
        self.getContact()
        self.save_cookies()
        self.start_receiving()
        self.logout()

    def weChatInit(self):
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=%s&lang=zh_CN' % int(time.time())
        data = {'BaseRequest': 
                {'DeviceID': self.loginInfo['deviceid'],
                 'Sid' : self.loginInfo['wxsid'].decode('utf-8'),
                 'Skey' : self.loginInfo['skey'].decode('utf-8'),
                 'Uin' : self.loginInfo['wxuin'].decode('utf-8')}}
        self.loginInfo.update(data)
        r = self.s.post(url, data=json.dumps(data), headers=self.header)
        dic = json.loads(r.content.decode('utf-8', 'replace'))
        utils.emoji_formatter(dic['User'], 'NickName')
        self.loginInfo['InviteStartCount'] = int(dic['InviteStartCount'])
        self.loginInfo['User'] = utils.struct_friend_info(dic['User'])
        #self.contact = dic['ContactList']
        self.process_contact(dic['ContactList'])
        self.loginInfo['SyncKey'] = dic['SyncKey']
        self.loginInfo['synckey'] = '|'.join(['%s_%s' % (item['Key'], item['Val'])
            for item in dic['SyncKey']['List']])
        return dic

    def process_contact(self, contactlist):
        conta = list()
        for contact in contactlist:
            user = dict()
            user['UserName'] = contact['UserName']
            user['NickName'] = contact['NickName']
            conta.append(user)
        print(conta)
        self.contact = conta
        for i in conta:
            if 'Core' in i['NickName']:
                print i
                self.contact_t = i['UserName']

    def weChatStatusNotify(self):
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxstatusnotify?lang=zh_CN&pass_ticket=%s' % self.loginInfo['pass_ticket']
        data = {
            'BaseRequest' : self.loginInfo['BaseRequest'],
            'Code' : 3,
            'FromUserName' : self.loginInfo['User']['UserName'],
            'ToUserName'   : self.loginInfo['User']['UserName'],
            'ClientMsgId'  : int(time.time()), }
        r = self.s.post(url, data=json.dumps(data), headers=self.header)

    def getContact(self):
        url = '%s/webwxgetcontact?r=%s&seq=0&skey=%s&pass_ticket=%s' % (self.prehost, int(time.time()), self.loginInfo['skey'], self.loginInfo['pass_ticket'])
        r = self.s.get(url, headers=self.header)
        tempList = json.loads(r.content.decode('utf-8', 'replace'))['MemberList']
        chatroomList, otherList = [], []
        for m in tempList:
            if m['Sex'] != 0:
                otherList.append(m)
            elif '@@' in m['UserName']:
                chatroomList.append(m)
            elif '@' in m['UserName']:
                otherList.append(m)
        return chatroomList

    def sync_check(self):
        url = 'https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck'
        params = {
            'r' : int(time.time() * 1000),
            'skey' : self.loginInfo['skey'],
            'sid'   :   self.loginInfo['wxsid'],
            'uin'   :   self.loginInfo['wxuin'],
            'deviceid'  :   self.loginInfo['deviceid'],
            'synckey'   :   self.loginInfo['synckey'],
            '_'     :   int(time.time() * 1000)}
        r = self.s.get(url, params = params, headers = self.header)
        regx = r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}'
        pm = re.search(regx, r.text)
        if pm is None or pm.group(1) != '0':
            #logger.debug('Unexpected sync check result: %s' % r.text)
            return None
            
        return pm.group(2)

    def webwxsync(self):
        url = '%s/webwxsync?sid=%s&skey=%s&lang=zh_CN&pass_ticket=%s' % (
                self.prehost, self.loginInfo['wxsid'], self.loginInfo['skey'], self.loginInfo['pass_ticket'])
        data = {
            'BaseRequest' : self.loginInfo['BaseRequest'],
            'SyncKey'   : self.loginInfo['SyncKey'],
            'rr'    : int(time.time())}
        r = self.s.post(url, data=json.dumps(data), headers=self.header)
        dic = json.loads(r.content.decode('utf-8', 'replace'))
        self.loginInfo['SyncKey'] = dic['SyncCheckKey']
        self.loginInfo['synckey'] = '|'.join(['%s_%s' % (item['Key'], item['Val'])
            for item in dic['SyncCheckKey']['List']])
        return dic['AddMsgList'], dic['ModContactList']

    def save_cookies(self):
        cookies = list()
        for item in self.s.cookies:
            data = {
                'name' : item.name,
                'value': item.value,
                'domain': item.domain,
                'expires': item.expires
            }
            cookies.append(data) 
        #self.ss = requests.Session() 
        #for c in cookies:
        #    self.ss.cookies.set(**c)

    def start_receiving(self):
        self.alive = True
        cout = 0
        while self.alive:
            i = self.sync_check()
            if i is None:
                self.alive=False
            elif i == '0':
                continue
            else:
                msgList, contactList = self.webwxsync()
                if msgList:
                    produce_msg(self, msgList)
                    msgList = list()

    def send_msg(self,touser, content):
        url = '%s/webwxsendmsg?pass_ticket=%s' % (self.prehost, self.loginInfo['pass_ticket'])
        data = {
            'BaseRequest' : self.loginInfo['BaseRequest'],
            'Msg': {
                'ClientMsgId': int(time.time() *1000),
                'LocalID':int(time.time() *1000),
                'FromUserName' : self.loginInfo['User']['UserName'].decode('utf-8'),
                'Content': content,
                'ToUserName' : touser,
                'Type':1
                },
            'Scene':0
            }
        r = self.s.post(url, data = json.dumps(data, ensure_ascii=False).encode('utf-8'), headers = self.header)

    def logout(self):
        url = '%s/webwxlogout' % self.prehost
        data = {
            'redirect': 1,
            'type'  :   1,
            'skey'  : self.loginInfo['skey']}
        r = self.s.get(url, params = data, headers=self.header)
        print('wechat is logout')

 

class ChatRobot(object):

    def chat(self, text):
        apikey = "b85870a566c94f2c895c149f6fda16c7"
        url = "http://www.tuling123.com/openapi/api"
        body = { 
            "key":apikey,
            "info":text
        }   
        rep = requests.post(url,json.dumps(body))
        jtext = json.loads(rep.content)
        return jtext['text']



# a =  WeChat().GetWeChatCookies('https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=A2j-JSAujsdhX74L_hbojbqH@qrticket_0&uuid=QYHhlI68dg==&lang=zh_CN&scan=1448935970&vcdataticket=AQbbnFwLqqgifEfbcQQ2ro9t&vccdtstr=N-SvpfgDKjk_LbK9VEEllhof1w6Z8gIaqOC2_G2ocdCzD_1kFvHtgoZgpKg5fnrw')
#print a
