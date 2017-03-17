#!/usr/bin/env python
#-*- coding: utf-8 -*-
# @Filename: auth/message.py
# @Author: olenji - lionhe0119@hotmail.com
# @Description: ---
# @Create: 2017-03-09 15:55:14
# @Last Modified: 2017-03-09 15:55:14
#

import pdb

def handle_group_msg(wx, msg):
    content = wx.robot.chat(msg['Content'].split('<br/>')[1])
    wx.send_msg(msg['FromUserName'], content)
    

def produce_msg(wx, msgList):
    for msg in msgList:
        if '@@' in msg['FromUserName'] and msg['MsgType'] == 1:
            if msg['FromUserName'] == wx.contact_t:
                print(msg)
                #detect_contact(wx.contact, msg['FromUserName'])
                handle_group_msg(wx, msg)
            


def detect_contact(contactList, name):
    for contact in contactList:
        if contact['UserName'] == name:
            print(contact['NickName'].encode('utf8'))
        else:
            for member in contact['MemberList']:
                if member['UserName'] == name:
                    print(contact['NickName'].encode('utf8'))
                    print member
            
        

