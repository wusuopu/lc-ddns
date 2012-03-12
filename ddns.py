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
# @文件名(file): ddns.py
# @作者(author): 龙昌锦(LongChangjin)
# @博客(blog): http://www.xefan.com
# @邮箱(mail): admin@xefan.com
# @时间(date): 2012-03-12
# 


import api
import sys
import os
import socket
import getpass
try:
    import json
except:
    import simplejson as json
import time

lines = ['默认', '电信', '联通', '教育网', '移动', '铁通', '国内',
        '国外', '搜索引擎', '百度', 'Google', '有道', '必应', '搜搜', '搜狗']

def Config():
    #登陆信息
    mail = raw_input("input login_email:>")
    pswd = getpass.getpass("input login_password:>")

    #域名列表
    print("\nget domain list....")
    dlist = api.DomainList(mail, pswd)
    dlist()
    if dlist.code == '9':
        print("domain list is empty!")
        exit(1)
    if dlist.code != '1':
        print("login error!")
        exit(1)
    print("\ndomain list:")
    i = 0
    for domain in dlist.domains:
        print("[%d]%s[%s]\t" % (i+1, domain['name'], domain['status'])),
        i = i+1
        if i%4 == 0:
            print("")
    #选择域名
    try:
        num = input("\nplease choose domain(1~%d):>" % i)
    except Exception,e:
        print("input domain error!")
        exit(1)
    if num<0 or num >i:
        print("input domain error!")
        exit(1)
    d_id = dlist.domains[num-1]['id']
    domain = dlist.domains[num-1]['name']

    #记录列表
    print("\nget record list....")
    rlist = api.RecordList(mail, pswd, domain_id=d_id)
    rlist()
    if rlist.code == '10':
        print("record list is empty!")
        exit(1)
    if rlist.code != '1':
        print("login error!")
        exit(1)
    print("\nrecord list:")
    i = 0
    for record in rlist.records:
        status = "enable" if record['enabled'] == '1' else "pause"
        print("[%d]%s.%s[%s]\t" % (i+1, record['name'], domain, status)),
        i = i+1
        if i%4 == 0:
            print("")
    #选择记录
    try:
        num = input("\nplease choose record(1~%d):>" % i)
    except Exception,e:
        print("input record error!")
        exit(1)
    if num<0 or num >i:
        print("input record error!")
        exit(1)
    r_id = rlist.records[num-1]['id']

    #主机记录
    sub = raw_input("\nplease input sub_domain[%s]:>"% rlist.records[num-1]['name'])
    if sub == "":
        sub = rlist.records[num-1]['name']

    #线路列表
    #print("\nget line list....")
    #llist = api.RecordLine(mail, pswd,domain_grade="D_Free")
    #llist()
    #if llist.code != '1':
    #    print("login error!")
    #    exit(1)
    print("\nline list:")
    i = 0
    for line in lines:
        print("[%d]%s\t" % (i+1, line)),
        i = i+1
        if i%4 == 0:
            print("")
    #选择线路
    try:
        num = input("\nplease choose line(1~%d):>" % i)
    except Exception,e:
        print("input line error!")
        exit(1)
    if num<0 or num >i:
        print("input line error!")
        exit(1)
    line = str(num-1)
    #line = lines.encode('utf-8') if isinstance(lines, unicode) else str(lines)
 
    js = '"login":{\n"email":"' + mail + '",\n"password":"' + pswd +'"\n},\n'
    js += '"info":{\n"domain":"%s",\n"domain_id":"%s",\n"record_id":"%s",\n"sub_domain":"%s",\n"line":"%s"\n}'%(domain, d_id, r_id, sub, line)
    fp = open('.config', 'w')
    fp.write("{\n")
    fp.write(js)
    fp.write("\n}")
    fp.close()

def PrintHelp():
    print("lc-ddns v1.0")
    print("Usage:")
    print("\t%s config\t----domain config" % sys.argv[0])
    print("\t%s run\t----start ddns" % sys.argv[0])
    print("\nblog:http://www.xefan.com")

def getip():
    sock = socket.create_connection(('ns1.dnspod.net', 6666))
    ip = sock.recv(16)
    sock.close()
    return ip

def Run():
    if os.path.exists('.config') == False:
        print(".config file is not exists!")
        exit(1)
    print("DDNS is starting...")
    fp = open('.config', 'r')
    s = fp.read()
    fp.close()
    cfg = json.loads(s)
    mail = cfg.get("login", {}).get("email")
    pswd = cfg.get("login", {}).get("password")

    info = cfg.get("info", {})
    domain = info.get("domain")
    current_ip = None
    dns = api.RecordDdns(mail, pswd, domain_id = info.get("domain_id"), 
            record_id = info.get("record_id"),
            sub_domain = info.get("sub_domain"),
            record_line = lines[int(info.get("line"))])
    while True:
        try:
            ip = getip()
            if current_ip != ip:
                dns()
                if dns.code == '1':
                    current_ip = ip
                    print("[%s] %s.%s ==> %s" %(time.ctime(), dns.name, domain, dns.value))
                elif dns.code == '400':
                    print("net error!")
                    exit(1)
                else:
                    print("error:%s" % dns.message)
        except Exception, e:
            print e
            pass
        time.sleep(60)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        PrintHelp()
        exit(1)

    if sys.argv[1] == "config":
        Config()
    elif sys.argv[1] == "run":
        Run()
    else:
        PrintHelp()
