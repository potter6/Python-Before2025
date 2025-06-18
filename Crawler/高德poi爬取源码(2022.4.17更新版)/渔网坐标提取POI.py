import requests
import json
from pymongo import MongoClient
import time
import pandas as pd

client = MongoClient('localhost',27017)
db = client.POI_Jinanshi
collection = db.table_1
polygon_list = list()

# with open("jn2.txt", 'r', encoding='UTF-8') as txt_file:
with open("data_output\SHP\渔网对角坐标获取.txt", 'r', encoding='UTF-8') as txt_file:
    for each_line in txt_file:
        if each_line != "" and each_line != "\n":
            fields = each_line.split("\n")
            polygon = fields[0]
            polygon_list.append(polygon)

def getjson(polygon, page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
    }
    pa = {
        'key': '61c256acd1b853e34a6b9a31033c399d', #从控制台申请
        'polygon': polygon,
        'types':'970000|990000',    #不要过多
        'city':'0531',
        'offset': 20,
        'page': page,
        'extensions': 'all',
        'output': 'JSON'
    }
    r = requests.get('https://restapi.amap.com/v3/place/polygon?', params=pa, headers=headers)
    decodejson = json.loads(r.text)
    return decodejson

# Create an empty list to store the data
data_list = []

for each_polygon in polygon_list:
    not_last_page = True
    page = 1
    while not_last_page:
        decodejson = getjson(each_polygon, page)
        print(decodejson)
        count = decodejson.get('count',0)
        print(each_polygon, page)
        if decodejson['pois']:
            for eachone in decodejson['pois']:
                data={
                    'name':eachone.get('name',None), #POI名称
                    'types':eachone.get('type',None), #POI所属类别
                    'address':eachone.get('address',None), #POI地址
                    'location':eachone.get('location',None), #POI坐标
                    'city':eachone.get('cityname',None), #城市
                    'county':eachone.get('adname',None), #区县
                    'province':eachone.get('pname',None), # 省份
                    'count':count, # 条数
                    'polygon':each_polygon # 多边形经纬度，便于后边再次抓取
                }
                collection.insert_one(data)
                data_list.append(data)
                time.sleep(0.2)
            page += 1
        else:
            not_last_page = False

# Create a DataFrame from the data list
df = pd.DataFrame(data_list)

# Write the DataFrame to an Excel file
output_file = 'output_data.xlsx'
df.to_excel(output_file, index=False,encoding='utf-8-sig')

# Close the MongoDB connection
client.close()