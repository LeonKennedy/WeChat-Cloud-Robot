# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         CherryHttpWeChat
# Purpose:      Identify the existence of a given acount on various sites.
#
# Author:       hkk
#
# Created:      17/11/2015
# Copyright:    (c) Steve Micallef 2015
# -------------------------------------------------------------------------------
import sys, re, pdb
import os,inspect,json,random
import shutil
import socket
from auth import database,WeChat_Auth
from auth.configobj import ConfigObj
#脱离系统模块路径
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "ext")))

if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)
deps = ['cherrypy', 'mako']
for mod in deps:
    try:
        if mod.startswith("ext."):
            modname = mod.split('.')
            print modname
            __import__('ext', fromlist=[modname[1]])
        else:

            __import__(mod)
    except ImportError as e:
        print ""
        print "Critical Start-up Failure: " + str(e)
        print "================================="
        print "It appears you are missing a module required for CherryHttpWeChat"
        print "to function. Please refer to the documentation for the list"
        print "of dependencies and install them."
        print ""
        print "Python modules required are: "
        for mod in deps:
            print " - " + mod
        print ""
        print "If you are running on Windows and getting this error, please"
        print "report this as a bug to hkk@sniffer.pro"
        print ""
        sys.exit(-1)


import cherrypy,time
from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions
def main():
    HTTP_HOST = '0.0.0.0'
    HTTP_PORT = 1314
    conf = {
        '/': {
            'tools.staticdir.root': os.path.join(getMainPath(), 'static'),
            'tools.gzip.on':True,
        },
        '/fonts':{
            'tools.staticdir.on': True,
            'tools.staticdir.dir': "fonts"
        },
        '/img':{
            'tools.staticdir.on': True,
            'tools.staticdir.dir': "img"
        },
        '/css':{
            'tools.staticdir.on': True,
            'tools.staticdir.dir': "css"
        },
        '/js':{
            'tools.staticdir.on': True,
            'tools.staticdir.dir': "js"
        },
        '/plugins':{
            'tools.staticdir.on': True,
            'tools.staticdir.dir': "plugins"
        },
        '/favicon.ico':{
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.join(getMainPath(),"static/img/favicon.ico")
        }
    }
    options_dict = {
        # 'tools.encode.on': True,
        # 'tools.encode.encoding': 'utf-8',
        # 'tools.decode.on': True,
        'log.screen':           True,
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Server', '')],
        #'server.thread_pool':   10,
        'server.socket_port':   HTTP_PORT,
        'server.socket_host':   HTTP_HOST,
        #'engine.autoreload_on': False
        'tools.sessions.on':True,
        'tools.sessions.storage_type':'file',
 #       'tools.sessions.storage_path':getMainPath()+"\\tmp\\",
        'tools.sessions.storage_path':getMainPath()+"/tmp/",
        'tools.sessions.timeout': 3600*24,
        'tools.sessions.httponly': True
        }
    socket.setdefaulttimeout(5)
    cherrypy.config.update(options_dict)
    cherrypy.engine.autoreload.unsubscribe()
    cherrypy.quickstart(CherryHttpWeChat(),'/', config=conf)

def render_template(templatename, **kwargs):

    static_dir = os.path.join(str(getMainPath()), 'static/')
    template_dir = static_dir #os.path.join(str(static_dir), cherrystrap.HTTP_LOOK)

    _hplookup = TemplateLookup(directories=[template_dir])

    try:
        template = _hplookup.get_template(templatename)
        return template.render(**kwargs)
    except:
        return exceptions.html_error_template().render()

def getMainPath():
    # This will get us the program's directory, even if we are frozen using py2exe.

    # Determine whether we've been compiled by py2exe
    if hasattr(sys, "frozen"):
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding()))

    if sys.platform == "linux2":
        return sys.path[1]

    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))
def iif(condition, true_part, false_part):
    return (condition and [true_part] or [false_part])[0]
def txt_wrap_by(start_str, end, html):
    start = html.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = html.find(end, start)
        if end >= 0:
            return html[start:end].strip()
class CherryHttpWeChat(object):
    """docstring for CherryHttp"""

    My_Wechat = WeChat_Auth.WeChat()
    def index(self):

        #ti = u'微信云端机器人 v1.0 Alpha版'

        try:

            if cherrypy.session['_sessionid'] == cherrypy.session.id:
                try:
                        
                    _username = cherrypy.session['_username']
                    _config_c = ConfigObj(getMainPath()+'/wxUserCookies/'+_username+'.ini',encoding='GBK')
                    #登录配置
                    _Login_Time = _config_c[u'登陆配置'][u'登陆时间']
                    _Login_id = _config_c[u'登陆配置']['UID']
                    #print _Login_Time
                    _loginfile = getMainPath()+"/wxRoot/"+ _Login_id + "/loginfile.ini"
                    _config_l = ConfigObj(_loginfile,encoding='GBK')
                    _headimg = _config_l[u'用户配置'][u'头像数据'][0]+','+_config_l[u'用户配置'][u'头像数据'][1]
                    _flag = True

                    return render_template(templatename="index.html", title=u'微信云端机器人 v1.0 Alpha版',PHOTO=_headimg,flag = _flag)
                except KeyError, e:
                    _flag = False
                    return render_template(templatename="index.html", title=u'微信云端机器人 v1.0 Alpha版',PHOTO='https://mmbiz.qlogo.cn/mmbiz/BXwbKibOw0LBDkuesGUgffMY8RzwMJB3INQjExYynvLZMdgj4tfjiblNeb8aHgwqjbdaibm0TDbLqMDFUcc9FicX3w/0?wx_fmt=png',flag = _flag)

        except KeyError, e:

            raise cherrypy.HTTPRedirect("/logout")

    index.exposed=True
    def logout(self):
        #ti = u'微信云端机器人 v1.0 Alpha版'
        cherrypy.lib.sessions.expire()
        return render_template(templatename="login.html", title=u'微信云端机器人 - 登录')
    logout.exposed=True
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.json_in(on = True)
    @cherrypy.tools.json_out(on = True)
    def login(self):
        #ti = u'微信云端机器人 v1.0 Alpha版'
        #return render_template(templatename="login.html", title=u'微信云端机器人 - 登录')
        json_in = cherrypy.request.json
        db = database.DBConnection(getMainPath()+'/User.db')
        db_result = db.check_user(json_in['user'],json_in['pass'])
        if  db_result is not None:
            cherrypy.session['_username'] = json_in['user']
            cherrypy.session['_istype'] = db_result[1]
            cherrypy.session['_sessionid'] = cherrypy.session.id
            #cherrypy.request.login = json_in['user']
            json_out = { 'login' : True }
            return json_out
        else:

           json_out = { 'login' : False }
           return json_out
    login.exposed=True
    @cherrypy.tools.json_in(on = True)
    @cherrypy.tools.json_out(on = True)
    def check_sustus(self):
        json_in = cherrypy.request.json
        _uuid = json_in['uuid']

        if  _uuid is not None:
            res = self.My_Wechat.ScanStauts(_uuid)
            #print '\n'
            #print res
            code = res[12:15]
            if code =='408' or code =='400':#未扫描
                json_out = { 'code' : code }
            if code == '201':#扫描未确认//获得头像
                cherrypy.session['_headphoto'] = res[37:].replace('\';','')
                json_out = { 'code' : code,'msg':res[37:].replace('\';','') }
            if code == '200': #扫描并确认
                regx = r'window.redirect_uri="(\S+)";'
                url  = re.search(regx, res).group(1)
                result = self.My_Wechat.GetWeChatCookies(url)
                if result is not None:

                    _username = cherrypy.session['_username']
                    _config_Login = ConfigObj(getMainPath()+'/wxUserCookies/'+_username+'.ini',encoding='GBK')
                    uid = txt_wrap_by('<wxuin>','</wxuin>',result['MSG'])
                    _config_Login[u'登陆配置'] = {}
                    _config_Login[u'登陆配置'][u'登陆时间'] = str(time.time())[:10]
                    _config_Login[u'登陆配置']['UID'] = uid
                    _config_Login.write()

                    _config_Login = ConfigObj(getMainPath()+'/wxUserConfig/'+uid+'.ini',encoding='GBK')
                    _config_Login[u'用户配置'] = {}
                    _config_Login[u'用户配置'][u'头像数据'] = cherrypy.session['_headphoto']
                    _config_Login[u'用户配置'][u'登陆ID']   = _username
                    _config_Login[u'用户配置'][u'登陆成功信息']   = result['MSG']
                    _config_Login[u'用户配置'][u'登陆Cookies']   = result['COOKIES']
                    _config_Login[u'用户配置'][u'登陆时间']   = str(time.time())[:10]
                    _config_Login[u'用户配置'][u'online']   = '1'
                    _config_Login[u'用户配置'][u'URL'] = url+"&fun=new&version=v2&lang=zh_CN"
                    _config_Login.write()
                    #if  os.path.exists(getMainPath()+"/wxRoot/"+uid+'/wxapi.dll') == False:
                    #    shutil.copytree(getMainPath()+'/WEB/', getMainPath()+"/wxRoot/"+uid)

                    shutil.copyfile(getMainPath()+'/wxUserConfig/'+uid+'.ini', getMainPath()+"/wxRoot/"+uid+'/'+'loginfile.ini')
                    print 'run'
                    print  '\n'



                json_out = { 'code' : code,'msg':'ok' }

            return json_out
        else:
           json_out = { 'code' : "Error" }
           return json_out
    check_sustus.exposed=True
    @cherrypy.tools.json_in(on = True)
    def register(self):
        if cherrypy.request.method == 'GET':
            return render_template(templatename="register.html", title=u'微信云端机器人 - 注册')
        if cherrypy.request.method == 'POST':
            json_in = cherrypy.request.json
            #{"user":"123","pass":"123","wechatid":"123"}
            db = database.DBConnection(getMainPath()+'/User.db')
            db_result = db.regist_user(json_in['user'],json_in['pass'],json_in['wechatid'])
            if db_result == 'user':
                return '{"result":false,"msg":"注册用户已存在！请不要重复注册"}'
            if db_result:
                return '{"result":true,"msg":"注册成功！"}'
            else:
                #print  type(
                return '{"result":false,"msg":"注册失败,邀请人ID:'+str(json_in['wechatid'])+'不存在"}'
            #print db_result
            #return cherrypy.request.body.read()

    register.exposed=True
    def update_history(self):
        return render_template(templatename="update_history.html")


    update_history.exposed=True
    def cloud_status(self,v='4.0'):

        try:

            if cherrypy.session['_sessionid'] == cherrypy.session.id:

                try:
                    raise KeyError 
                    _username = cherrypy.session['_username']
                    _config_c = ConfigObj(getMainPath()+'/wxUserCookies/'+_username+'.ini',encoding='GBK')
                    #登录配置
                    _Login_Time = _config_c[u'登陆配置'][u'登陆时间']
                    _Login_id = _config_c[u'登陆配置']['UID']
                    #print _Login_Time
                    _loginfile = getMainPath()+"/wxRoot/"+ _Login_id + "/loginfile.ini"
                    _config_l = ConfigObj(_loginfile,encoding='GBK')

                    _headimg = _config_l[u'用户配置'][u'头像数据'][0]+','+_config_l[u'用户配置'][u'头像数据'][1]
                    _online = _config_l[u'用户配置']['online']
                    _loginfile = getMainPath()+"/wxRoot/"+ _Login_id + "/Config/wxset.ini"

                    _confi_r = ConfigObj(_loginfile,encoding='GBK')
                    #_robotname = _confi_r[u'机器人设置'][u'机器人姓名']
                    _robotname = 'olenji'
                    _uuid = ''
                    _isLogin =True

                    if _online == '1':
                        _online=U'在线'
                    else:

                        _online = U'离线'
                        _uuid  = self.My_Wechat.genQrcodeUuid()
                        _isLogin = True
                        _online = _online+"|https://login.weixin.qq.com/qrcode/"+_uuid +"?t=webwx"
                    return render_template(templatename="index_v1.html", title=u'微信云端机器人 v1.0 Alpha版',
                             TIME = int(str(time.time())[:10])-int(_Login_Time),
                             MEMORY = str(random.randint(0,100))+"%",
                             DAIKUAN = str(random.randint(0,100))+"%",
                             CPU = str(random.randint(0,100))+"%",
                             WeChatID = _username ,
                             PHOTO    =  _headimg ,
                             online   = _online,
                             uuid = _uuid,
                             isLogin =_isLogin,

                         WeChatRobootName = _robotname)

                except KeyError, e:
                    _online = U'离线'
                    _isLogin = False
                    _uuid  = self.My_Wechat.genQrcodeUuid()
                    _online = _online+"|https://login.weixin.qq.com/qrcode/"+_uuid +"?t=webwx"

                    return render_template(templatename="index_v1.html", title=u'微信云端机器人 v1.0 Alpha版',

                        isLogin =_isLogin,
                        online  = _online,
                        uuid    = _uuid)

                    print  e

        except KeyError, e:
            print e
            
    cloud_status.exposed=True
    @cherrypy.tools.json_in(on = True)
    def cloud_setting(self,v='4.0'):

        try:
            if cherrypy.session['_sessionid'] == cherrypy.session.id:
                if cherrypy.request.method == 'GET':

                    #return render_template(templatename="register.html", title=u'微信云端机器人 - 注册')
                    #
                    _username = cherrypy.session['_username']
                    _config_c = ConfigObj(getMainPath()+'/wxUserCookies/'+_username+'.ini',encoding='GBK')
                    #登录配置
                    _Login_Time = _config_c[u'登陆配置'][u'登陆时间']
                    _Login_id = _config_c[u'登陆配置']['UID']
                    #print _Login_Time
                    _loginfile = getMainPath()+"/wxRoot/"+ _Login_id + "/loginfile.ini"
                    _config_l = ConfigObj(_loginfile,encoding='GBK')
                    _headimg = _config_l[u'用户配置'][u'头像数据'][0]+','+_config_l[u'用户配置'][u'头像数据'][1]

                    _loginfile = getMainPath()+"/wxRoot/"+ _Login_id + "/Config/wxset.ini"
                    _confi_r   = ConfigObj(_loginfile,encoding='GBK')
                    _robotname = _confi_r[u'机器人设置'][u'机器人姓名']
                    _robotadd  = _confi_r[u'群管设置'][u'群管_加']
                    _robotinvt = _confi_r[u'群管设置'][u'群管_邀']
                    _robotremo = _confi_r[u'群管设置'][u'群管_移']
                    _robotadm  = _confi_r[u'通知设置'][u'管理员UIN']
                    _robotrelpy = _confi_r[u'回复设置'][u'回复几率']
                    _robotads  = _confi_r[u'广告设置'][u'广告语']
                    _robotcont = _confi_r[u'刷屏设置'][u'刷屏内容']
                    #逻辑配置
                    _friend_learning = _confi_r[u'机器人设置'][u'好友学习']
                    _group_learning = _confi_r[u'机器人设置'][u'群学习']
                    _wx_replay =  _confi_r[u'回复设置'][u'启用回复']
                    _wx_group_replay = _confi_r[u'回复设置'][u'群默认']
                    _wx_friend_replay = _confi_r[u'回复设置'][u'好友默认']
                    _group_admin = _confi_r[u'群管设置'][u'启用群管']
                    _group_admin_repaly = _confi_r[u'通知设置'][u'通知群管']
                    _friend_man = _confi_r[u'添加好友设置'][u'通过男性好友']
                    _friend_men = _confi_r[u'添加好友设置'][u'通过女性好友']


                    #plugins
                    _plugins =dict()
                    for filename in os.listdir(getMainPath() + '/wxRoot/'+ _Login_id + '/Plugin/'):
                        if filename.endswith("wx.dll"):
                            plugins_name = filename.split('.wx.dll')[0]
                            #plugins_name =unicode(plugins_name,'GBK')
                            #print type(plugins_name)


                            path = getMainPath() + '/wxRoot/'+ _Login_id + '/Plugin/'+plugins_name+".wx.dll.ini"

                            file_object = open(path)
                            try:
                                 all_the_text = file_object.read( )
                            finally:
                                 file_object.close( )
                            if '1' in all_the_text:
                                _plugins[plugins_name]='1'
                            else:
                                _plugins[plugins_name]='0'
                            #print _plugins






                    #_robotname =_confi_r[u'机器人设置'][u'机器人姓名']
                    return render_template(templatename="index_v2.html", title=u'微信智能云端机器人 - 云端配置',
                    username = _username ,
                    PHOTO    =  _headimg ,
                    robotname = _robotname,
                    admin_ad =  _robotcont ,
                    admin = _robotadm ,
                    reply = _robotrelpy ,
                    friend_repaly =  _robotads ,
                    group_join = _robotadd ,
                    group_invent = _robotinvt ,
                    group_remove = _robotremo ,
                    friend_learning = iif(int(_friend_learning),'checked',''),
                    group_learning = iif(int(_group_learning),'checked',''),
                    wx_replay = iif(int(_wx_replay),'checked',''),
                    wx_group_replay = iif(int(_wx_group_replay),'checked',''),
                    wx_friend_replay = iif(int(_wx_friend_replay),'checked',''),
                    group_admin = iif(int(_group_admin),'checked',''),
                    group_admin_repaly = iif(int(_group_admin_repaly),'checked',''),
                    friend_man = iif(int(_friend_man),'checked',''),
                    friend_men = iif(int(_friend_men),'checked',''),
                    plugins =_plugins


                     )
                if cherrypy.request.method == 'POST':
                    json_in = cherrypy.request.json
                    _username = cherrypy.session['_username']
                    _config_c = ConfigObj(getMainPath()+'\wxUserCookies\\'+_username+'.ini',encoding='GBK')
                    #登录配置
                    #_Login_Time = _config_c[u'登陆配置'][u'登陆时间']
                    _Login_id = _config_c[u'登陆配置']['UID']
                    _loginfile = getMainPath()+"\wxRoot\\"+ _Login_id + "\Config\wxset.ini"
                    _config_write = ConfigObj(_loginfile,encoding='GBK')
                    #{"UID":"test","type":"0","msg":"机器人设置|好友学习","action":"0"}

                    if json_in['type'] == '0':
                        msg = json_in['msg'].split("|")
                        _config_write[msg[0]][msg[1]] = json_in['action']
                        #print type(msg[0])
                        #print (msg[0])
                        _config_write.write()
                        return '{"result":true}'
                    if json_in['type'] == '1':

                        path = getMainPath() + '/wxRoot/'+ _Login_id + '/Plugin/'+json_in['msg']+".wx.dll.ini"

                        file_object = open(path,'r+')


                        try:

                            all_the_text = file_object.read( )
                            if json_in['action'] == '1':
                                all_the_text = all_the_text.replace('0','1')
                            else:
                                all_the_text = all_the_text.replace('1','0')

                        finally:
                             file_object.close( )


                        file_object = open(path,'r+')
                        file_object.write(all_the_text)
                        file_object.close( )


                        return '{"result":true}'



                        pass
                    if json_in['type'] == '2':
                        _action = json_in['action'].split('@')
                        _action_demo =_action

                        for i in range(8):
                            _action_demo =_action[i].split('|')
                            _config_write[_action_demo[0]][_action_demo[1]] = _action_demo[2]
                        _config_write.write()
                        return '{"result":true}'

        except KeyError, e:
            raise cherrypy.HTTPRedirect("/logout")
    def cloud_info(self,v='4.0'):

        #ti = u'微信云端机器人 v1.0 Alpha版'

        try:

            if cherrypy.session['_sessionid'] == cherrypy.session.id:
                try:

                    _username = cherrypy.session['_username']
                    _config_c = ConfigObj(getMainPath()+'\wxUserCookies\\'+_username+'.ini',encoding='GBK')
                    #登录配置
                    _Login_Time = _config_c[u'登陆配置'][u'登陆时间']
                    _Login_id = _config_c[u'登陆配置']['UID']
                    #print _Login_Time
                    _loginfile = _loginfile = getMainPath()+"\wxRoot\\"+ _Login_id + "\Config\wxset.ini"
                    _config_l = ConfigObj(_loginfile,encoding='GBK')
                    _today =_config_l[u'数据统计'][u'今天日期']
                    _history_requests = _config_l[u'数据统计'][u'历史请求数']
                    _today_requests  = _config_l[u'数据统计'][u'今日请求数']

                    _history_reply = _config_l[u'数据统计'][u'历史回复数']
                    _today_reply  = _config_l[u'数据统计'][u'今日回复数']

                    _today_fans = _config_l[u'数据统计'][u'今日被动粉丝']
                    _history_fans = _config_l[u'数据统计'][u'历史被动粉丝']
                    #print _history_fans

                    if _today_requests == '' or _history_requests =='' or len(_history_requests)<7:
                        print '\n\n'
                        print '1'
                        _history_requests = '11,11,15,13,2,13,10'
                    else:
                        print '\n\n'
                        print '2'
                        _lenth = len(_history_requests)
                        _history_requests = _history_requests[_lenth-6]+","+_history_requests[_lenth-5]+","+_history_requests[_lenth-4]+","+_history_requests[_lenth-3]+","+_history_requests[_lenth-2]+","+_history_requests[_lenth-1]+_today_requests

                    if _history_reply == '' or _today_reply =='' or len(_history_reply)<7:
                        _history_reply = '11,11,15,13,12,13,30'
                    else:
                        _lenth = len(_history_reply)
                        _history_reply = _history_reply[_lenth-6]+","+_history_reply[_lenth-5]+","+_history_reply[_lenth-4]+","+_history_reply[_lenth-3]+","+_history_reply[_lenth-2]+","+_history_reply[_lenth-1]+_today_reply
                    if _today_fans == '' or _history_fans =='' or len(_history_fans)<7:
                        _history_fans = '11,11,15,13,12,13,10'
                    else:

                        _lenth = len(_history_fans)
                        _history_fans = _history_fans[_lenth-6]+","+_history_fans[_lenth-5]+","+_history_fans[_lenth-4]+","+_history_fans[_lenth-3]+","+_history_fans[_lenth-2]+","+_history_fans[_lenth-1]+_today_fans
                    if _today != str(time.strftime('%m-%d')):

                        _config_l[u'数据统计'][u'历史请求数'] = _history_requests
                        _config_l[u'数据统计'][u'历史回复数'] = _history_reply
                        _config_l[u'数据统计'][u'历史被动粉丝'] = _history_fans
                        _config_l.write()

                    return render_template(templatename="index_v3.html", title=u'微信云端机器人 v1.0 Alpha版',
                        QQS = "["+_history_reply+"]",
                        BDFSS =_today_fans,
                        HFS = "["+_history_requests+"]"
                        )
                except KeyError, e:
                    return render_template(templatename="index_v3.html", title=u'微信云端机器人 v1.0 Alpha版',PHOTO='https://mmbiz.qlogo.cn/mmbiz/BXwbKibOw0LBDkuesGUgffMY8RzwMJB3INQjExYynvLZMdgj4tfjiblNeb8aHgwqjbdaibm0TDbLqMDFUcc9FicX3w/0?wx_fmt=png')

        except KeyError, e:

            raise cherrypy.HTTPRedirect("/logout")

    cloud_info.exposed=True
    def pc_fun(self,v='4.0'):

        #ti = u'微信云端机器人 v1.0 Alpha版'

        try:

            if cherrypy.session['_sessionid'] == cherrypy.session.id:
                try:



                    return render_template(templatename="index_v4.html", title=u'微信云端机器人 PC娱乐'
                        )
                except KeyError, e:
                    return render_template(templatename="index_v3.html", title=u'微信云端机器人 v1.0 Alpha版',PHOTO='https://mmbiz.qlogo.cn/mmbiz/BXwbKibOw0LBDkuesGUgffMY8RzwMJB3INQjExYynvLZMdgj4tfjiblNeb8aHgwqjbdaibm0TDbLqMDFUcc9FicX3w/0?wx_fmt=png')

        except KeyError, e:

            raise cherrypy.HTTPRedirect("/logout")

    pc_fun.exposed=True





    cloud_setting.exposed=True
if __name__ == "__main__":
    print os.path.join(getMainPath(),"img/favicon.ico")
    main()
