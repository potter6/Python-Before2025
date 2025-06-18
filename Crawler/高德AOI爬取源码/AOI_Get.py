'''@author: zql
'''
#!/usr/bin/python
# -*- coding:utf-8 -*-
#项目名称：爬取百度地图的AOI数据
#详细描述：
import json
import urllib
from urllib import request
import requests
from pprint import pprint
from prettytable import PrettyTable
import random
#from station import stations
import warnings
import  xdrlib ,sys
import pandas as pd
import time
import socket
#bd墨卡托转BD-09
import transform as tf


HEADERS = {'Accept':'*/*',
        'Accept-Encoding':'gzip, deflate, sdch, br',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Connection':'keep-alive',
        'Cookie':'BAIDUID=C4D08149D7EE627DC037119413418CA3:FG=1; BIDUPSID=C4D08149D7EE627DC037119413418CA3; PSTM=1540284487; pgv_pvi=9789244416; BDUSS=GF-S3Y5c1MybnhoTkhwMUxyWEhHM3ZreW1UTURiQk1TUFllMWc5V1ZWeUVHNGhkRVFBQUFBJCQAAAAAAAAAAAEAAAA~7j45ztLKx8DtuaTIyzMyMQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAISOYF2EjmBdV; session_id=1567581077599; session_name=; validate=31187; MCITY=-%3A; M_LG_UID=960425535; M_LG_SALT=2cf3bbbbd3e5466b66a2529c037b982b',
        'Host':'map.baidu.com',
        'Referer':'https://map.baidu.com/search/%E9%83%91%E5%B7%9E%E5%B8%82%E4%BA%8C%E4%B8%83%E4%B8%87%E8%BE%BE%E4%B8%89%E5%8F%B7%E9%99%A2/@12650489.832882352,4101769.7450000006,18.35z/maptype%3DB_EARTH_MAP?querytype=s&da_src=shareurl&wd=%E9%83%91%E5%B7%9E%E5%B8%82%E4%BA%8C%E4%B8%83%E4%B8%87%E8%BE%BE%E4%B8%89%E5%8F%B7%E9%99%A2&c=268&src=0&pn=0&sug=0&l=18&b=(12650755.24571287,4101867.1117821783;12651854.04020792,4102020.4126732675)&from=webmap&biz_forward=%7B%22scaler%22:1,%22styles%22:%22pl%22%7D&device_ratio=1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
}

# name_data=pd.read_csv('shanghaipark_transform.csv')
name_data=pd.read_csv('3shanghaipark_transform.csv')

for k in range(len(name_data)):
    name='上海'+name_data['adname'][k]
    url = 'https://map.baidu.com/?newmap=1&qt=s&da_src=searchBox.button&wd='+name+'&c=268'
    warnings.filterwarnings("ignore")
    try:
        response = requests.get(url, headers=HEADERS,allow_redirects=True,verify=False,timeout=3)
        data=''
        with open('shanghaipark_AOI.txt','a') as of:
            with open('shanghaipark_AOI.txt','a') as of1:
                if response.content:
                    data=response.content.decode('utf-8')
                    data=json.loads(data)
                    AOI_id=data['result']['profile_uid']
                    print(data['result']['profile_uid'])
                    uel_AOI = 'https://map.baidu.com/?newmap=1&qt=ext&uid='+AOI_id+'&ext_ver=new&ie=utf-8&l=11'
                    try:
                        r_AOI=requests.get(uel_AOI,headers=HEADERS,allow_redirects=True,verify=False,timeout=3)
                        data_AOI=''

                        if r_AOI.content:
                            data_AOI=r_AOI.content.decode('utf-8')
                            data_AOI=json.loads(data_AOI)
                            try:
                                if 'geo' in data_AOI['content']:
                                    data_AOI['content']['geo']
                                    geo_AOI=data_AOI['content']['geo']
                                    geo_AOI=geo_AOI.split('|')
                                    print(geo_AOI[2])
                                    point=geo_AOI[2].split(',')
                                    point_transform=[]

                                    #全部点的坐标，分别是x,y,的形式
                                    for i in range(int(len(point)/2)):
                                        #第一个点的x坐标删除‘1-’
                                        if i==0:
                                            print(point)
                                            point[2*i]=point[2*i][2:]
                                        #最后的点的y坐标删除‘;’
                                        if i==int(len(point)/2)-1:
                                            point[2*i+1]=point[2*i+1][:-1]
                                        print('各点的坐标',float(point[2*i]),float(point[2*i+1]))
                                        point_Mecator2BD09=tf.Mecator2BD09(float(point[2*i]),float(point[2*i+1]))
                                        point_BD092WGS84=tf.BD092WGS84(point_Mecator2BD09)
                                        point_transform.append(point_BD092WGS84)
                                        print(point_transform)
                                        point_str=''
                                        for j in range(len(point_transform)):
                                            point_str=point_str+(str(point_transform[j])).replace(' ','')[1:-1]+';'
                                            print('转换坐标后的坐标点',point_str)

                                    of.write(name+' '+point_str+'\n')
                                if 'geo' not in data_AOI['content']:
                                    of1.write(name+' '+'\n')
                                
                            

                            except socket.timeout:
                                print('失败')    
                    except socket.timeout:
                        print('失败')

    except socket.timeout:
        print('失败')
        