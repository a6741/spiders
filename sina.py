#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 23 13:20:44 2018

@author: ljk
"""
from os import path
import threading
import datetime
import requests
from bs4 import BeautifulSoup
import pymysql
import re
import json
import time
from scipy.misc import imread
import matplotlib.pyplot as plt
import jieba
from wordcloud import WordCloud, ImageColorGenerator
global totalnum
totalnum=0
def connect(headers,url):#从数据库ip池获取代理ip
    db=dbconnect()
    #ipp=ips[random.randint(0,len(ips)-1)]
    sql="select ip from ips order by rand() limit 1"
    cursor=db.cursor()
    cursor.execute(sql)
    db.close()
    try:
        proxy=cursor.fetchone()[0]
    except:
        getip()
    k={'http': 'http://{ip}','https': 'https://{ip}'}
    k['http']=k['http'].format(ip=proxy)
    k['https']=k['https'].format(ip=proxy)
    req=''
    fla=True
    tryt=0
    while fla:
        try:
            req=requests.get(url=url,headers=headers,proxies=k)
            fla=False
        except:
            print('233333')
            tryt+=1
            if tryt>3:
                sql="delete from ips where ip='"+str(proxy)+"'"
                db=dbconnect()
                cursor=db.cursor()
                cursor.execute(sql)
                db.commit()
                db.close()
                fla=False
                req=connect(headers,url)
    return req
def testip(myids,proxy):#测试代理ip是否可用
    #global ips
    #if len(ips)<5:
        headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}
        url = "http://ip.chinaz.com/getip.aspx"
        url='http://icanhazip.com/'
        try:
            k={'http': 'http://{ip}','https': 'https://{ip}'}
            k['http']=k['http'].format(ip=proxy)
            k['https']=k['https'].format(ip=proxy)
            res = requests.get(url,proxies=k,headers=headers)
            so=BeautifulSoup(res.text,'lxml')
            #prip=re.search('(?<=://).*\d+:',str(proxy)).group().replace(':','')
            #print(proxy,so.text)
            if proxy.split(':')[0] in so.text:
            #if myids not in so.text and '{ip:' in so.text:
                db=dbconnect()
                cursor = db.cursor()
                sql="select * from ips where ip='"+str(proxy).replace("'","")+"'"
                #print(sql)
                k=cursor.execute(sql)
                if k==0:
                    #ips.append(proxy)
                    sql="insert into ips value('"+str(proxy).replace("'","")+"')"
                    #print(sql)
                    cursor.execute(sql)
                    db.commit()
                    print(so.get_text())
                db.close()
        except:
            pass
def getip():#从ip代理网站获取ip
    headers={
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
"Accept-Encoding":"gzip, deflate",
"Accept-Language":"zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
"Cache-Control":"max-age=0",
"Connection":"keep-alive",
"Cookie":"_free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJWYwNDBiMjNlZDNkMWU5MTMzZTllODhiYTcxZWZmMDQ4BjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMUMraTBQclNKN0VjTXNUVnBIQmhFV09sNk1MUWFlWU5Qb1NzS3JOd2oxaXM9BjsARg%3D%3D--03cfdc3029f7ab0bfdddc79973642fe22c7f746b",
"Host":"www.xicidaili.com",
"Upgrade-Insecure-Requests":"1",
"User-Agent":"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
            }
    global proxys
    proxys=[]
    ttt=[]
    n=1
    url = "http://ip.chinaz.com/getip.aspx"
    res = requests.get(url)
    myid=BeautifulSoup(res.text,'lxml')
    idm=re.findall("\d+",myid.text)
    myids='.'.join(idm)
    while(n<5):
        url = 'http://www.xicidaili.com/nn/'+str(n)
        shtml=requests.get(url,headers=headers)
        Soup=BeautifulSoup(shtml.text,'lxml')
        if 'block' in Soup:
            #time.sleep(3600)
            print('You are blocked')
            return
        theurl=Soup.find_all('tr',class_="odd")
        for ur in theurl:
            #if ur.find_all('td')[5].get_text().lower()=='https':
            proxys.append(ur.find_all('td')[1].get_text()+":"+ur.find_all('td')[2].get_text())
            #proxys.append({ur.find_all('td')[5].get_text().lower(): "http://"+ur.find_all('td')[1].get_text()+":"+ur.find_all('td')[2].get_text()})
        url = "http://ip.chinaz.com/getip.aspx"
        for proxy in proxys:
            t=threading.Thread(target=testip,args=(myids,proxy,))
            t.setDaemon(False)
            t.start()
            ttt.append(t)
        print(n)
        n+=1
    for t in ttt:
        t.join()
def getotherinfo(tid,url):#通过对电脑网页页面解析获得地理位置等
    headers={'Cookie':'SINAGLOBAL=5815815601728.413.1511951280583; _T_WM=1d5046c163c1809d29363bf5f9f36b3c; un=13395954553; SCF=Ah9Z2C3ADNiy9vuSKiiSdXJSTusbY6iE1lKq_OhbnP1zT-XXd9pUcMmolOXsxqqrtiJZjqDv70Z3-76yQrgDIhg.; SUHB=0M20AtqlqB-yzF; wvr=6; UOR=database.51cto.com,widget.weibo.com,www.baidu.com; YF-Page-G0=0dccd34751f5184c59dfe559c12ac40a; SUB=_2AkMsWtO0dcPxrAFTnvERzGznZI5H-jyfj7pCAn7uJhMyOhgv7ksrqSVutBF-XJ9chda5SUPlgPGIXOmFuSX7AA5k; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WWXnpekgKee-9l7rhggUYvB5JpX5K2hUgL.FozESo.XehMf1he2dJLoI79ywsHrws2t; _s_tentry=passport.weibo.com; Apache=6194752446538.489.1527143556687; ULV=1527143556692:9:3:3:6194752446538.489.1527143556687:1527054040214',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}
    rurl='https://weibo.com/'+url+"/info?mod=pedit_more"
    try:
        req=connect(headers,rurl)
        rb=BeautifulSoup(req.text,'lxml')
        rc=str(rb).split('PCD_text_b2')[1]
        rr=BeautifulSoup(rc.replace('\\',''),'lxml')
        qq=rr.find_all('li')
        dic={}
        dic['所在地：']=''
        dic['生日：']=''
        try:
            for r in qq:
                dic[r.find(class_='pt_title').get_text()]=r.find(class_='pt_detail').get_text()
        except:
            pass
        sql="insert into sinaadd value('"+tid+"','"+dic['所在地：']+"','"+dic['生日：']+"')"
        db=dbconnect()
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            db.commit()
        except:
            pass
        db.close()
    except:
        print('......',url)
def getinfo(mid):#通过手机微博的API获取基础信息
    url='https://m.weibo.cn/api/container/getIndex?is_all[]=1&is_all[]=1&jumpfrom=weibocom&type=uid&value='+str(mid)
    headers={'Cookie':'SINAGLOBAL=5815815601728.413.1511951280583; _T_WM=1d5046c163c1809d29363bf5f9f36b3c; un=13395954553; SCF=Ah9Z2C3ADNiy9vuSKiiSdXJSTusbY6iE1lKq_OhbnP1zT-XXd9pUcMmolOXsxqqrtiJZjqDv70Z3-76yQrgDIhg.; SUHB=0M20AtqlqB-yzF; wvr=6; UOR=database.51cto.com,widget.weibo.com,www.baidu.com; YF-Page-G0=0dccd34751f5184c59dfe559c12ac40a; SUB=_2AkMsWtO0dcPxrAFTnvERzGznZI5H-jyfj7pCAn7uJhMyOhgv7ksrqSVutBF-XJ9chda5SUPlgPGIXOmFuSX7AA5k; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WWXnpekgKee-9l7rhggUYvB5JpX5K2hUgL.FozESo.XehMf1he2dJLoI79ywsHrws2t; _s_tentry=passport.weibo.com; Apache=6194752446538.489.1527143556687; ULV=1527143556692:9:3:3:6194752446538.489.1527143556687:1527054040214',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}
    req=connect(headers,url)
    global rj
    rj=req.json()
    while rj['ok']!=1:
        print('fuck')
        #time.sleep(3600)
        req=connect(headers,url)
        try:
            rj=req.json()
        except:
            rj['ok']=0
    if rj['ok']==1:
        info=rj['data']['userInfo']
        ids[mid]['粉丝数']=info['followers_count']
        ids[mid]['关注数']=info['follow_count']
        ids[mid]['微博数']=info['statuses_count']
        ids[mid]['微博认证']=info['verified']
        try:
            ids[mid]['认证原因']=info['verified_reason']
        except:
            ids[mid]['认证原因']=''
        try:
            ids[mid]['简介']=re.search('[\w\（\）\《\》\——\；\，\。\“\”\<\>\！]+',info['description']).group()
        except:
            ids[mid]['简介']=''

        ids[mid]['isfans']=False
    global totalnum
    totalnum+=1
    if totalnum%100==1:
        insert()
    print(totalnum/5000,'\n')
def getreport(i):
    url='https://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id=4242426837783780&max_id=4242909416777480&page={num}&__rnd=1527072504738'
    urls=url.format(num=str(i))
    headers={'Cookie':'SINAGLOBAL=5815815601728.413.1511951280583; _T_WM=1d5046c163c1809d29363bf5f9f36b3c; un=13395954553; SCF=Ah9Z2C3ADNiy9vuSKiiSdXJSTusbY6iE1lKq_OhbnP1zT-XXd9pUcMmolOXsxqqrtiJZjqDv70Z3-76yQrgDIhg.; SUHB=0M20AtqlqB-yzF; wvr=6; UOR=database.51cto.com,widget.weibo.com,www.baidu.com; YF-Page-G0=0dccd34751f5184c59dfe559c12ac40a; SUB=_2AkMsWtO0dcPxrAFTnvERzGznZI5H-jyfj7pCAn7uJhMyOhgv7ksrqSVutBF-XJ9chda5SUPlgPGIXOmFuSX7AA5k; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WWXnpekgKee-9l7rhggUYvB5JpX5K2hUgL.FozESo.XehMf1he2dJLoI79ywsHrws2t; _s_tentry=passport.weibo.com; Apache=6194752446538.489.1527143556687; ULV=1527143556692:9:3:3:6194752446538.489.1527143556687:1527054040214',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}

    req=connect(headers,urls)
    fla=True
    while fla:
        try:
            rj=req.json()
            fla=False
        except:
            #time.sleep(3600)
            req=connect(headers,urls)
            fla=True
    so=BeautifulSoup(rj['data']['html'],'lxml')
    q=so.find_all(class_='list_li S_line1 clearfix')
    for t in q:
        iid=t.find('a')['usercard'].replace('id=','')
        if selectot(iid):
                href=t.find('a')['href'].replace('https://weibo.com/','')
                getotherinfo(iid,href)#获取地理位置等信息
        if select(iid):
	    if iid not in ids:
                ids[iid]={}
                name=t.find(class_='WB_text').find('a').get_text()
                times='2018-'+t.find(class_='WB_from S_txt2').find('a').get_text()
                if('分钟前' in times):
                    times=str(datetime.datetime.now()-datetime.timedelta(minutes = int(re.search('\d+',time).group())))
                times=times.replace('今天','5-'+str(datetime.datetime.now().day)).replace('月','-').replace('日','')#处理转发时间
                ids[iid]['name']=name
                ids[iid]['time']=times
                getinfo(iid)#获取基础信息
        print(iid)
def getcomment(i):#获取评论信息并放入字典word中
    t=0
    while t<5:
        print(t,i)
        url='https://m.weibo.cn/api/comments/show?id=4242426837783780&page='+str(5*i+t)
        headers={
                'User-Agent':'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Mobile Safari/537.36',
                'cookie':'_T_WM=c72195184a30f8b2390ca97dcf809fc0; SCF=Ah9Z2C3ADNiy9vuSKiiSdXJSTusbY6iE1lKq_OhbnP1z6O5x9LNLQ1Kl6c0VSRqN-SBj6qAI_NXzuicCnOMM9CE.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWXnpekgKee-9l7rhggUYvB5JpX5K-hUgL.FozESo.XehMf1he2dJLoI79ywsHrws2t; SUHB=0mxlh5gw2bo8K4; SUB=_2AkMsUGMQdcPxrAFTnvERzGznZI5H-jyfhQrmAn7oJhMyPRh87gdWqSdutBF-XKyJgYwx1b516qAORQWuKi20g_zM; WEIBOCN_FROM=1110005030; MLOGIN=0; M_WEIBOCN_PARAMS=luicode%3D20000061%26lfid%3D4242426837783780%26oid%3D4242426837783780%26uicode%3D20000061%26fid%3D4242426837783780'
                }
        fla=True
        while fla:
            try:
                req=connect(headers,url)
                rj=req.json()
                if rj['ok']==1:
                    fla=False
            except:
                print('try')
                pass
        data=rj['data']['data']
        global word
        for dat in data:
            iid=dat['id']
            text=BeautifulSoup(dat['text'],'lxml').get_text()
            word[iid]=text
            print(text)
        t+=1

def selectot(iid):#查看该记录是否已存在
    db=dbconnect()
    cursor = db.cursor()
    sql="select id from sinaadd where id='"+iid+"'"
    k=cursor.execute(sql)
    db.close()
    if k==0:
        return True
    else:
        return False
def select(iid):#查看该记录是否已存在
    db=dbconnect()
    cursor = db.cursor()
    sql="select id from sina2 where id='"+iid+"'"
    k=cursor.execute(sql)
    db.close()
    if k==0:
        return True
    else:
        return False
def dbconnect():
    return pymysql.connect("127.0.0.1", "root", "123456", "sina", charset='utf8' )#连接数据库
def builddb():
    db=dbconnect()
    t="show tables like 'sina2'"
    t2="show tables like 'sinaadd'"#确认数据库是否已创建
    t3="show tables like 'ips' "
    cursor = db.cursor()
    a='create table sina2(id varchar(100) primary key,name varchar(20),time datetime,fans int,follow int,wb int,varify tinyint,varifyreason text,word text,isfans tinyint)'#储存基础信息
    a2='create table sinaadd(id varchar(100) primary key,loc varchar(50),birth varchar(50))'#储存地理位置、生日等其他信息
    a3='create table ips(ip varchar(80) primary key)'#ip池
    k=cursor.execute(t)
    if(k==0):
        cursor.execute(a)
    k=cursor.execute(t2)
    if(k==0):
        cursor.execute(a2)
    k=cursor.execute(t3)
    if(k==0):
        cursor.execute(a3)
    db.commit()
    db.close()
def insert():
    db=dbconnect()
    sqls=[]
    cursor = db.cursor()
    for i in ids:
        if len(ids[i])>2:
            try:
                sql="insert into sina2 value("+str(i)+",'"+ids[i]['name']+"','"+ids[i]['time']+"',"+str(ids[i]['粉丝数'])+","+str(ids[i]['关注数'])+","+str(ids[i]['微博数'])+","+str(ids[i]['微博认证'])+",'"+ids[i]['认证原因']+"','"+ids[i]['简介']+"',"+str(ids[i]['isfans'])+")"
                try:
                    cursor.execute(sql)
                except:
                    sqls.append(sql)
            except:
                print('?')
                pass
    db.commit()
    db.close()



def ciyun(word):#生成词云
	d = path.dirname('.')
	stopwords = {}
	isCN = 1 #默认启用中文分词
	back_coloring_path = "6.png" # 设置背景图片路径
	font_path = '1.ttf' # 为matplotlib设置中文字体路径没
	imgname1 = "WordCloudDefautColors.png" # 保存的图片名字1(只按照背景图片形状)
	imgname2 = "WordCloudColorsByImg.png"# 保存的图片名字2(颜色按照背景图片颜色布局生成)

	back_coloring = imread(path.join(d, back_coloring_path))# 设置背景图片

	# 设置词云属性
	wc = WordCloud(font_path=font_path,  # 设置字体
		       background_color="white",  # 背景颜色
		       max_words=2000,  # 词云显示的最大词数
		       mask=back_coloring,  # 设置背景图片
		       max_font_size=100,  # 字体最大值
		       random_state=42,
		       width=1000, height=860, margin=2,# 设置图片默认的大小,但是如果使用背景图片的话,那么保存的图片大小将会按照其大小保存,margin为词语边缘距离
		       )




	text = ''
	for i in word:
		text+=i

	def jiebaclearText(text):
	    mywordlist = []
	    seg_list = jieba.cut(text, cut_all=False)
	    liststr="/ ".join(seg_list)
	    for myword in liststr.split('/'):
		    mywordlist.append(myword)
	    return ''.join(mywordlist)

	if isCN:
	    text = jiebaclearText(text)

	# 生成词云
	wc.generate(text.replace('回复',''))
	# wc.generate_from_frequencies(txt_freq)
	# txt_freq例子为[('词a', 100),('词b', 90),('词c', 80)]
	# 从背景图片生成颜色值
	image_colors = ImageColorGenerator(back_coloring)

	plt.figure()
	# 以下代码显示图片
	plt.imshow(wc)
	plt.axis("off")
	plt.show()
	# 绘制词云

	# 保存图片
	wc.to_file(path.join(d, imgname1))

	image_colors = ImageColorGenerator(back_coloring)

	plt.imshow(wc.recolor(color_func=image_colors))
	plt.axis("off")
	# 绘制背景图片为颜色的图片
	plt.figure()
	plt.imshow(back_coloring, cmap=plt.cm.gray)
	plt.axis("off")
	#plt.show()
	# 保存图片
	wc.to_file(path.join(d, imgname2))


global word,ids
word={}
ids={}
builddb()#建立数据库
ts=[]
getip()#获取代理IP
i=0
#以下为获取评论的线程 由于新浪的限制 只能获取前100页
while i<20:
    t=threading.Thread(target=getcomment,args=(i,))
    t.start()
    ts.append(t)  
    i+=1
#以下为获取转发的线程
while i<400:
    t=threading.Thread(target=getreport,args=(i,))
    t.start()
    ts.append(t)
    i+=1
for t in ts:
    t.join()
insert()#插入转发信息
