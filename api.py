#!/usr/bin/env python
#-*- coding:utf-8 -*-
## 
#  Copyright (C) 
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation.
# 本程序是免费软件，基于GPL许可发布。
# 
##
# @文件名(file): api.py
# @作者(author): 龙昌锦(LongChangjin)
# @博客(blog): http://www.xefan.com
# @邮箱(mail): admin@xefan.com
# @时间(date): 2012-03-12
# 


import httplib, urllib
try: import json
except: import simplejson as json
import socket
import re


class Error(StandardError):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        StandardError.__init__(self, message)

class DnsApi:
    """Api base class"""
    def __init__(self, login_email, login_pswd, **kw):
        self.message = ""
        self.base_url = "dnsapi.cn"
        self.params = {
            "login_email":login_email,
            "login_password":login_pswd,
            "format":"json"
        }
        self.params.update(kw)
        self.path = None

    def request(self, **kw):
        """
            request function,POST methon
            -1: login fail
            -8: login too often
            1: success
            2: only allow post
            3: unknown error
        """
        self.params.update(kw)
        if self.__class__.__name__ == "DnsApi":
            return
        name = re.sub(r'([A-Z])', r'.\1', self.__class__.__name__)
        self.path = "/" + name[1:]
        conn = httplib.HTTPSConnection(self.base_url)
        headers = {"Content-type":"application/x-www-form-urlencoded", "Accept":"text/json", "User-Agent":"LC-pydns/1.0 (admin@longchangjin.cn)"}
        conn.request("POST", self.path, urllib.urlencode(self.params), headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        ret = json.loads(data)
        if ret.get("status", {}).get("code") == "1":
            return ret
        else:
            #raise Exception(ret.get("status", {}).get("code"))
            raise Error(ret.get("status", {}).get("code"), ret.get("status", {}).get("message"))



#获取域名列表
class DomainList(DnsApi):
    """get domains list"""
    def __init__(self, email, pswd, **kw):
        """
        type:{all,mine,share,ismark,pause}
        offset:first is NO. 0
        length:total item number
        group_id:get the group's domain
        """
        DnsApi.__init__(self,email, pswd, **kw)

    def __call__(self):
        """
        code 6:offset is invalid
        code 7:length is invalid
        code 9:list is empty
        """
        try:
            ret = self.request()
            self.code = ret['status']['code']
            
            info = ret['info']
            self.domain_total = info['domain_total']
            self.all_total = info['all_total']
            self.mine_total = info['mine_total']
            self.share_total = info['share_total']
            self.ismark_total = info['ismark_total']
            self.pause_total = info['pause_total']
            self.domains = ret['domains']
        except Error, e:
            self.code = e.code
            self.message = e.message
        except Exception, e:
            self.code = '400'

#记录列表
class RecordList(DnsApi):
    """get record list"""
    def __init__(self, email, pswd, **kw):
        """
        domain_id:get from DomainList
        offset:the first is NO.0
        length:the total item number
        """
        DnsApi.__init__(self,email, pswd, **kw)

    def __call__(self):
        """
        code -7:enterprise user need to upgrade
        code -8:agent user need to upgrade
        code 6:domain_id is error
        code 7:offset is invalid
        code 8:length is invalid
        code 9:is not the owner of domain
        code 10:no item
        """
        try:
            ret = self.request()
            self.code = ret['status']['code']
            self.total = ret['info']['record_total']
            self.records = ret['records']
        except Error, e:
            self.code = e.code
            self.message = e.message
        except Exception, e:
            self.code = '400'

#更新动态DNS记录
class RecordDdns(DnsApi):
    def __init__(self, email, pswd, **kw):
        """
        domain_id:get from DomainList
        record_is:get from RecordList
        sub_domain:the host record,eg:www
        record_line:get from RecordLine,Chinese,eg:默认
        """
        DnsApi.__init__(self,email, pswd, **kw)

    def __call__(self):
        """
        code -15:domain has been disable
        code -7:enterprise user need to upgrade
        code -8:agent user need to upgrade
        code 6:domian_id is error
        code 7:is not the owner of domain
        code 8:record_id is error
        code 21:domain is locked
        code 22:sub_domain is invalid
        code 23:sub domain count is max
        code 24:analyze error
        code 25:record count is max
        code 26:record_line is error
        """
        try:
            ret = self.request()
            self.code = ret['status']['code']
            record = ret['record']
            self.id = record['id']
            self.name = record['name']
            self.value = record['value']
        except Error, e:
            self.code = e.code
            self.message = e.message
        except Exception, e:
            self.code = '400'

