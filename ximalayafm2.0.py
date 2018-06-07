#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 21 23:38:50 2018

@author: ljk
"""

import threading
import requests
from bs4 import BeautifulSoup
import re
import pymysql
import json
import datetime
def connect(url):
    f=False
    while not f:
        try:
            s = requests.session()
            s.keep_alive = False
            r=s.get(url,headers=headers)
            s.keep_alive = False
            f=True
        except:
            f=False#如果没有成功连接网页，则重试
    return r
def getfreeurl(gurl):
    #print(gurl)
    global reb,page
    req=connect(gurl)
    reb=BeautifulSoup(req.text,'lxml')
    try:
        page=int(reb.find_all(class_='page-item')[-2].find('span').get_text())
    except:
        page=1
    sr=reb.find_all(class_='album-wrapper')
    if len(sr)==0:#如果找不到节目，则说明该类别不存在收付费的区别，则改变url以获取正确的网页
        gurl=gurl.replace('mr132t2722/','')
        req=connect(gurl)
        reb=BeautifulSoup(req.text,'lxml')
        try:
            page=int(reb.find_all(class_='page-item')[-2].find('span').get_text())
        except:
            page=1
        sr=reb.find_all(class_='album-wrapper')
    t=0
    print(len(sr))
    for r in sr:
#        getpayit(r)
        name=r.find(class_='album-title')['title']
        num=r.find(class_='listen-count').get_text()
        if 'w' in num:
            num=num.replace('w','')
            num=float(num)*10000
        else:
            num=float(num)
        surl=r.find('a')['href']
        iid=re.search("\d+",surl).group()
        dic.append([name,num,0,iid])
        print(name,'free')
        t+=1
    pg=2
    while pg<page:
        getmoreurl(gurl+"p"+str(pg))
        pg+=1
    if t==0:
        global sb,stp
        sb=gurl
        stp=reb
    print('ok',t)
def getmoreurl(murl):
    req=connect(murl)
    reb=BeautifulSoup(req.text,'lxml')
    sr=reb.find_all(class_='album-wrapper')
    t=0
    for r in sr:
#        getpayit(r)
        name=r.find(class_='album-title')['title']
        num=r.find(class_='listen-count').get_text()
        if 'w' in num:
            num=num.replace('w','')
            num=float(num)*10000
        else:
            num=float(num)
        surl=r.find('a')['href']
        iid=re.search("\d+",surl).group()
        dic.append([name,num,0,iid])
        print(name,'free')
        t+=1
    if t==0:
        global sb,stp
        sb=murl
        stp=reb
    print('ok',t)
def getmorepurl(murl):
    req=connect(murl)
    reb=BeautifulSoup(req.text,'lxml')
    sr=reb.find_all(class_='album-wrapper')
    for r in sr:
        getpayit(r)
def getpayurl(gurl):
    req=connect(gurl)
    if '付费' not in req.text:#如果该类别下不存在收付费的区别，则直接退出
        return
    reb=BeautifulSoup(req.text,'lxml')
    try:
        page=int(reb.find_all(class_='page-item')[-2].find('span').get_text())#获取该类别页数
    except:
        page=1
    sr=reb.find_all(class_='album-wrapper')
    for r in sr:
        getpayit(r)
    pg=2
    while pg<page:
        getmorepurl(gurl+"p"+str(pg))#下一页
        pg+=1
    print('ok')
def getpayit(r):#获取付费节目信息
    surl=r.find('a')['href']
    iid=re.search("\d+",surl).group()
    #if selectid(iid):
    name=r.find(class_='album-title')['title']#名字
    #if select(iid):
    num=r.find(class_='listen-count').get_text()#播放量
    if 'w' in num:
        num=num.replace('w','')
        num=float(num)*10000
    else:
        num=float(num)
    pr=getinfo(turl+surl)
    dic.append([name,num,pr,iid])

    print(name,'pay')
#    else:
#        pass
def getinfo(gurl):#获得节目价格/标签信息
    req=connect(gurl)
    reb=BeautifulSoup(req.text,'lxml')
#    以下注释掉的内容用以获取标签数据
#    flag=True
#    while flag:
#        try:
#            tags=[]
#            tags.append(reb.find(class_='cate')['title'])
#            flag=False
#        except:
#            req=connect(gurl)
#            reb=BeautifulSoup(req.text,'lxml')
#            flag=True
#            print('!!!')
#    rt=reb.find_all(class_='xui-tag-text')
#    for t in rt:
#        tags.append(t.find('a')['title'])
    try:
        return float(re.search('\d+.\d+',reb.find(class_='price-btn').get_text()).group())
    except:
        #print(gurl)
        return 0
def selectid(iid):
    db=dbconnect()
    cursor = db.cursor()
    sql="select name from xmly where id='"+iid+"'"#判断是否存在数据
    k=cursor.execute(sql)
    if k==0:
        return True
    else:
        return False
def select(iid):
    db=dbconnect()
    cursor = db.cursor()
    sql="select id from tags where id='"+iid+"'"#判断该节目的标签数据是否存在
    k=cursor.execute(sql)
    if k==0:
        return True
    else:
        return False
def builddb(db):
    t="show tables like 'xmly'"
    t2="show tables like 'addup'"
    t3="show tables like 'tags'"
    cursor = db.cursor()
    a='create table xmly(id varchar(20),name varchar(100),num int,price float,primary key(id))'
    b='create table addup(id varchar(20),addnum int,nowprice float,day int,primary key(id,day))'
    c='create table tags(id varchar(20),tag varchar(20),primary key(id,tag))'
    k=cursor.execute(t)
    if(k==0):#判断该数据表是否存在
        cursor.execute(a)
    k=cursor.execute(t2)
    if(k==0):
        cursor.execute(b)
    k=cursor.execute(t3)
    if(k==0):
        cursor.execute(c)
    db.commit()
def dbconnect():
    return pymysql.connect("127.0.0.1", "root", "ljk623127", "zhihu", charset='utf8' )
def addup(db):
    global day
    cursor=db.cursor()
    for k in dic:
        sql="select num from xmly where id='"+k[3]+"'"
        u=cursor.execute(sql)
        if u!=0:
            t=cursor.fetchone()[0]#原本的总数据
        else:
            t=0
        sql="insert into addup value('"+k[3]+"',"+str((k[1]-t))+","+str(k[2])+","+str(day)+")"
        try:
            cursor.execute(sql)
        except:
            pass
    db.commit()
    db.close()
def tags(db):
    cursor = db.cursor()
    for k in dic:
        for i in k[2]:
            sql="insert into tags value('"+k[3]+"','"+i+"')"
            try:
                cursor.execute(sql)
            except:
                pass
    db.commit()
    db.close()
def insert(db):
    cursor = db.cursor()
    sql="delete from xmly"
    cursor.execute(sql)
    db.commit()
    for k in dic:
            sql="insert into xmly value('"+k[3]+"','"+k[0].replace("'","").replace('"',"").replace(','," ").replace('，'," ")+"',"+str(k[1])+","+str(k[2])+")"
            try:
                cursor.execute(sql)
                print(sql)
            except:
                pass
    db.commit()
    db.close() 
def makesure():
    db=dbconnect()
url='http://www.ximalaya.com/category/'
turl='http://www.ximalaya.com'

headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}
global day
day=8
sss=datetime.timedelta(days = 1)
nowday=datetime.datetime.now()
nextday=datetime.datetime.now()
aaaa=datetime.datetime(2018, 6, 2, 23, 55, 45, 396437)
while True:
    nowday=datetime.datetime.now()
    if nowday>nextday:
        req=requests.get(url,headers=headers)
        reb=BeautifulSoup(req.text,'lxml')
        sr=reb.find_all(class_='subject_wrapper')#热门类别以外的类别
        ht=reb.find_all(class_='hotword')#热门类别
        dic=[]
        global ts
        ts=[]
        for s in sr:
            stype=s.find('a')['href']
            t=threading.Thread(target=getfreeurl,args=(turl+stype+'mr132t2722/',))#该类别下的免费页面
            t.setDaemon(False)
            t.start()
            ts.append(t)
            t=threading.Thread(target=getpayurl,args=(turl+stype+'mr132t2721/',))#该类别下的收费页面
            t.setDaemon(False)
            t.start()
            ts.append(t)
        for s in ht:
            stype=s.find('a')['href']
            t=threading.Thread(target=getfreeurl,args=(turl+stype+'mr132t2722/',))
            t.setDaemon(False)
            t.start()
            ts.append(t)
            t=threading.Thread(target=getpayurl,args=(turl+stype+'mr132t2721/',))
            t.setDaemon(False)
            t.start()
            ts.append(t)   
        for t in ts:
            t.join()
        db=dbconnect()#连接数据库的函数
        builddb(db)#如果数据表不存在，则创建之
        addup(db)#将一日数据输入数据库
        db=dbconnect()
        #tags(db)#将标签数据存入数据库
        insert(db)#将总数据存入数据库
        day+=1
        nextday+=sss
