import requests
from bs4 import BeautifulSoup
import json
import re
import time
import sqlite3
import pandas as pd
import random
import traceback
from time import sleep
from datetime import datetime, timedelta
import datetime
import csv
import numpy as np
import transformer

# import emoji

# header = {'User-Agent': "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/78.0.3904.108 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "cookie": "_T_WM=69752906325; XSRF-TOKEN=5d4784; WEIBOCN_FROM=1110006030; SCF=AluwODJI40amKvbiRhhr3x3X5WFJsmVFhCfV1x9vjoqOClbvDk24AJK6MQMfVgkC3FFEseLDs4KhPH02Q4EA8NQ.; SUB=_2A25KbLpEDeRhGeFP4lMR8SvIyTmIHXVpA7OMrDV6PUJbktAYLUvjkW1NQOrKxSJF8u8GbzfHJKt65nu07Un7TlsU; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFJf.nPypequXxyIBhJbGay5NHD95QNeK.peh2fShzfWs4DqcjPi--ci-z0i-2Ei--NiKn4i-z41h.Eehzt; SSOLoginState=1734920724; ALF=1737512724; mweibo_short_token=404ae72811; MLOGIN=1; M_WEIBOCN_PARAMS=lfid%3D102803%26luicode%3D20000174%26uicode%3D20000174",
}

# 高德API 请求地址前缀
req_url_pref = "https://restapi.amap.com/v3/geocode/geo?"
amp_api_key = '61c256acd1b853e34a6b9a31033c399d'
amp_api_city='上海市'
#count = 0

def weibotable():
    create_weibotable = """CREATE TABLE weibo(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                                       weibo_id TEXT UNIQUE,
                                       crawler_time TEXT,
                                       created_time TEXT,
                                       content TEXT,
                                       textLength INTEGER,
                                       isLongText TEXT,
                                       source TEXT, 
                                       user_id INTEGER,
                                       user_screen_name TEXT,
                                       user_gender TEXT,
                                       statuses_count INTEGER,
                                       followers_count INTEGER,
                                       follow_count INTEGER,
                                       user_verified TEXT,
                                       verified_type INTEGER,
                                       description TEXT,
                                       close_blue_v TEXT,
                                       user_mbtype INTEGER,
                                       user_urank INTEGER,
                                       user_mbrank INTEGER,
                                       user_profile_url TEXT,
                                       toux_avatar_hd TEXT,
                                       reposts_count INTEGER,
                                       comments_count INTEGER,
                                       attitudes_count INTEGER,
                                       pending_approval_count INTEGER,
                                       mblog_vip_type INTEGER,
                                       mblogtype INTEGER,
                                       mlevel INTEGER,
                                       more_info_type INTEGER,
                                       pic_num INTEGER,
                                       pic_types TEXT,
                                       weibo_position INTEGER,
                                       url_scheme TEXT,
                                       place TEXT,
                                       category TEXT,
                                       category_id INTEGER,
                                       total_id INTEGER,
                                       city TEXT,
                                       city_id INTEGER)"""
    cur.execute(create_weibotable)  # 插入字段
    conn.commit()  # 数据库提交保存


def db_init():
    weibotable()


def random_ip(ippool):
    num = random.randint(0, len(ippool) - 1)
    return ippool[num]

def GaoDeLocation(address):
        # 没有上海市的地址在前面加上上海市
        if address.find("上海市") == -1:
            address = "上海市" + address
        
        rep_params={"key":amp_api_key,"address":address,"city":amp_api_city}
        response=requests.get(req_url_pref,params=rep_params)
        locationinfo=response.json()
        status=locationinfo["status"]
        if status !="0":
            outputaddress=locationinfo["geocodes"][0]["formatted_address"]
            gcj02_lng=float(locationinfo["geocodes"][0]["location"].split(",")[0])
            gcj02_lat=float(locationinfo["geocodes"][0]["location"].split(",")[1])
            wgs84_lng,wgs84_lat=transformer.gcj02towgs84(gcj02_lng,gcj02_lat)
            wgs84_lng=float(wgs84_lng)
            wgs84_lat=float(wgs84_lat)
        else:
            outputaddress=np.nan
            gcj02_lng=np.nan
            gcj02_lat=np.nan
            wgs84_lng=np.nan
            wgs84_lat=np.nan

        return outputaddress,gcj02_lng,gcj02_lat,wgs84_lng,wgs84_lat

def write_nameaddress_csv(filename, fields, data):
    with open(filename, mode="a", newline="",encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(data)


def get_tweets(URL, page, ippool):
    url = URL.format(str(page))

    while True:
        try:
            proxy_ip = random_ip(ippool)
            res = requests.get(url, proxies=proxy_ip, headers=headers)
            res.encoding = "utf-8-sig"
            # print(res)

            # 间隔时间
            # sleep(random.randint(5, 9))
            sleep(random.randint(2,5))
            # soup = BeautifulSoup(res.text, 'html.parser')

            jd = json.loads(res.text)
            jd = res.json()

        except:
            print("代理有问题呀，换个ip试试")
            continue
        if (jd["ok"] == 0) and ("这里还没有内容" in str(jd)):
            print(jd)
            return 0
        if jd["ok"] == 0:
            print("获取地点的页面失败啊，换个ip试试")
        else:
            break
    # 第一页的结果会有点不一样
    if page == 1:
        # if jd['data']['cards'][0]['card_id']=='card_hq_poiweibo':  #微博数据结构的表头为data——cards—— "card_id": "card_hq_poiweibo",
        if (
            jd["data"]["cards"][0]["card_id"] == "hot_search"
        ):  # 微博数据结构的表头为data——cards—— "card_id": "card_hq_poiweibo",
            tweets = jd["data"]["cards"]
            # tweets=jd['data']['cards'][0]['card_group']
        else:
            tweets = jd["data"]["cards"]  # 爬取city的这个地方我自己改为0了.
            # tweets=jd['data']['cards'][1]['card_group']
        
        #name=jd["data"]["cardlistInfo"]["title_top"]
        #address=jd["data"]["cardlistInfo"]["address"]
        #subtitle=jd["data"]["cardlistInfo"]["sub_title"]
        
        #outputaddress,gcj02_lng,gcj02_lat,wgs84_lng,wgs84_lat=GaoDeLocation(address)

        #write_nameaddress_csv(
            #"out/POILocationInfo.csv",
            #["name", "address","subtitle","outputaddress","gcj02_lng","gcj02_lat","wgs84_lng","wgs84_lat"],
            #{
            #    "name": name,
            #    "address": address,
            #    "subtitle":subtitle,
              #  "outputaddress":outputaddress,
             #   "gcj02_lng":gcj02_lng,
            #    "gcj02_lat":gcj02_lat,
           #     "wgs84_lng":wgs84_lng,
          #      "wgs84_lat":wgs84_lat
         #   },
        #)
    else:
        tweets = jd["data"]["cards"]
        # tweets=jd['data']['cards'][0]['card_group']

    print("获取到{}条微博".format(len(tweets)))
    return tweets


def writedb(tweets, page):

    # 遍历每条微博
    break_flag = False
    for tweet in tweets:
        for twee in tweet["card_group"]:
            # if ('mblog' in twee):
            if (
                ("mblog" in twee)
                and ("card_id" in twee)
                and ("created_at" in twee["mblog"])
                and ("textLength" in twee["mblog"])
            ):
                created_at = twee["mblog"]["created_at"]
                # created_at = twee['mblog'].get['created_at']

                """
                if u"刚刚" in created_at:
                    created_at = datetime.now().strftime("%Y-%m-%d")
                elif u"分钟" in created_at:
                    minute = created_at[:created_at.find(u"分钟")]
                    minute = timedelta(minutes=int(minute))
                    created_at = (datetime.now() - minute).strftime("%Y-%m-%d")
                elif u"小时" in created_at:
                    hour = created_at[:created_at.find(u"小时")]
                    hour = timedelta(hours=int(hour))
                    created_at = (datetime.now() - hour).strftime("%Y-%m-%d")
                elif u"昨天" in created_at:
                    day = timedelta(days=1)
                    created_at = (datetime.now() - day).strftime("%Y-%m-%d")
                elif created_at.count('-') == 1:
                    year = datetime.now().strftime("%Y")
                    created_at = year + "-" + created_at
                """

                temp = [0 for i in range(40)]  # 初始化一行，一共有37列
                temp[0] = twee["mblog"]["id"]
                temp[1] = datetime.datetime.now()
                temp[2] = created_at
                temp[3] = re.sub(
                    "[A-Za-z0-9\!\%\[\]\,\。\<\-\=\"\:\/\.\?\&\_\>'\;\ ]",
                    "",
                    twee["mblog"]["text"],
                )
                temp[4] = twee["mblog"]["textLength"]
                temp[5] = twee["mblog"]["isLongText"]
                temp[6] = twee["mblog"]["source"]
                temp[7] = twee["mblog"]["user"]["id"]
                temp[8] = twee["mblog"]["user"]["screen_name"]
                temp[9] = twee["mblog"]["user"]["gender"]
                temp[10] = twee["mblog"]["user"]["statuses_count"]
                temp[11] = twee["mblog"]["user"]["followers_count"]
                temp[12] = twee["mblog"]["user"]["follow_count"]
                temp[13] = twee["mblog"]["user"]["verified"]
                temp[14] = twee["mblog"]["user"]["verified_type"]
                temp[15] = twee["mblog"]["user"]["description"]
                temp[16] = twee["mblog"]["user"]["close_blue_v"]
                temp[17] = twee["mblog"]["user"]["mbtype"]
                temp[18] = twee["mblog"]["user"]["urank"]
                temp[19] = twee["mblog"]["user"]["mbrank"]
                temp[20] = twee["mblog"]["user"]["profile_url"]
                temp[21] = twee["mblog"]["user"]["avatar_hd"]
                temp[22] = twee["mblog"]["reposts_count"]
                temp[23] = twee["mblog"]["comments_count"]
                temp[24] = twee["mblog"]["attitudes_count"]
                temp[25] = twee["mblog"]["pending_approval_count"]
                temp[26] = twee["mblog"]["mblog_vip_type"]
                temp[27] = twee["mblog"]["mblogtype"]
                temp[28] = twee["mblog"]["show_mlevel"]
                # temp[29] = twee['mblog']['more_info_type']
                temp[29] = 0
                temp[30] = twee["mblog"]["pic_num"]
                # temp[31] = twee['mblog']['pic_types']
                temp[31] = 0
                temp[32] = 0
                temp[33] = twee["scheme"]
                temp[34] = 0
                temp[35] = 0
                temp[36] = 0
                temp[37] = 0
                # temp[38] = twee['mlog']['region_name']
                temp[38] = 0
                temp[39] = 0
                # print(temp[0], temp[1], temp[2], temp[3])
                # 不记录重复的微博。
                temp_pd = pd.read_sql_query("SELECT * FROM weibo", conn)
                all_id = temp_pd["weibo_id"].values
                if temp[0] in all_id:  # 通过weibo的ID判断是否爬过。
                    continue

                # 可以直接替换的字符
                # text_res1 = text_res.replace(place, '').replace('分享图片', '').replace('分享视频', '').replace('微博视频', '').replace('的微博视频', '').replace('，', ' ').replace('。', ' ').replace('；', ' ').replace('、', ' ').replace('！', ' ').replace('+', ' ').replace('：', ' ').replace('"', '').replace("'", '').replace('/', ' ').replace("|", ' ').replace('……', '')
                # 第1个删除表情的代码
                # co = re.compile(u'[\U00010000-\U0010ffff]')
                # text_res2=co.sub(u'',text_res1)
                # 第2个删除表情的代码
                # text_res3 = emoji.demojize(text_res2)
                # text_res4 = re.sub(':\S+?:', '', text_res3)
                # 替换 两个特殊字符之间的文本
                # text_res5 = text_res4.replace("#", "a")
                # pattern = re.compile(r'(a)(.*)(a)')
                # text_res6=pattern.sub(r'', text_res5)
                # text_res7 = text_res6.replace("【", "b")
                # text_res8 = text_res7.replace("】", "b")
                # pattern = re.compile(r'(b)(.*)(b)')
                # text_res9=pattern.sub(r'', text_res8)
                # text_res10 = text_res9.replace("（", "c")
                # text_res11 = text_res10.replace("）", "c")
                # pattern = re.compile(r'(c)(.*)(c)')
                # text_res12 = pattern.sub(r'', text_res11)
                # text_res13 = text_res12.replace("「", "d")
                # text_res14 = text_res13.replace("」", "d")
                # pattern = re.compile(r'(d)(.*)(d)')
                # text_res15 = pattern.sub(r'', text_res14)
                # 删除特殊字符及之后的内容
                # sep="@"
                # text_res16 = text_res15.split(sep, 1)[0]
                # sep = "北京·"
                # text_res17 = text_res16.split(sep, 1)[0]
                # 删除空格
                # text_res18=text_res17.strip()
                # 只保留中文
                # pattern = re.compile(r'[^\u4e00-\u9fa5]')
                # temp[3] = re.sub(pattern, '', text_res18)

                # ????????????????????????????
                # temp[6]=temp[6].replace("'","") #单引号替换为空
                # temp[6]=temp[6].replace('"','') #双引号替换为空

                # result_df=result_df.append(pd.Series(temp,index=result_df.columns),ignore_index=True)
                # result_df.to_csv('weibo.csv',encoding='utf-8-sig',index=False)

                ins = (
                    "INSERT INTO weibo VALUES (null,"
                    + ",".join(['"%s"' % x for x in temp])
                    + ")"
                )
                cur.execute(ins)
                conn.commit()


def main(row, ippool,yag,emailname):

    global conn, cur, place, pid, category, category_id, total_id, city, city_id
    # 读取资料文档
    # f = pd.read_csv('data/pid.csv', encoding='gbk')  # 出错的话改成gbk
    f = pd.read_csv("data/Shanghai_Pid_buy.csv",encoding='utf-8-sig')
    # f = pd.read_csv("data\shanghai.csv")  # 出错的话改成gbk

    place = f["pname"][row]
    pid = f["pid"][row]
    category = f["category"][row]
    category_id = f["category_id"][row]
    total_id = f["total_id"][row]
    city = f["city"][row]
    city_id = f["city_id"][row]
    # 连接数据库
    # conn = sqlite3.connect('weibo.sqlite',check_same_thread=False)
    conn = sqlite3.connect("C:/Users/Administrator/Desktop/WeiboPidSpiderServerEdition/sqlite/{}.sqlite".format(place), check_same_thread=False)
    cur = conn.cursor()
    conn.text_factory = lambda x: str(x, "gbk", "ignore")  # 后来添加的
    # 初始化数据库，如果已经存在了就接着爬就好了
    try:
        # db_init()
        weibotable()
    except:
        pass
    # 微博位置URL
    # URL = 'https://m.weibo.cn/api/container/getIndex?containerid='+pid+'_-_weibofeed&luicode=10000011&lfid=100103type%3D1%26q%3D%E6%AD%A6%E6%B1%89%E5%A4%A7%E5%AD%A6&page={}'
    URL = "https://m.weibo.cn/api/container/getIndex?containerid=" + pid + "&page={}"
    print(
        '******************开始爬"%d-%s"的微博了*******************************'
        % (total_id, place)
    )
    try:
        time_start = time.time()

        page = 1
        while True:
            print("开始爬", total_id, "-", place, "第", page, "页")
            # 获取当前时间
            global current_time
            current_time = time.strftime(
                "%Y-%m-%d-%H-%M-%S", time.localtime(time.time())
            )
            tweets = get_tweets(URL, page, ippool)
            # print(tweets)
            # 判断是不是到底了
            if "周边值得去" in str(tweets):
                print("爬到底了！")
                break
            if tweets == 0:
                print("已经到第", page, "页了，没有内容了")
                break
            # 写入数据库
            writedb(tweets, page)
            print(place, " 第", page, "页爬完了！")
            page += 1

            # 进行爬取目标的空判定，如果为空就进行下一个循环
            # 一般120页左右
            if page > 150:
                write_nameaddress_csv(
                    "out/.Emptyshanghaipid.csv",
                    ["pname", "pid"],
                    {"pname": place, "pid": pid}
                )
                break

        time_end = time.time()
        print(place, " time cost ", time_end - time_start, "s")
        print("******************%s的微博爬完了*******************************" % place)
        # 如果total_id是100的倍数
        if total_id % 500 == 0:
             yag.send(to=emailname, subject="{} - {}".format(total_id,place), contents="爬完了有{}\n".format(page)+"结束时间:"+f"{str(datetime.datetime.now())}")
    except:
        e = traceback.format_exc()
        print(e)
        yag.send(to = emailname, subject = place +' Break!!!!!', contents = [e])
    finally:
        # 关闭数据库
        cur.close()
        conn.close()

    print(place, "爬完了！等待下一次")
