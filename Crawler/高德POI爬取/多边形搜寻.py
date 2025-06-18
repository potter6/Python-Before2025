import requests
import json
import csv
import re
# from Coordin_transformlat import gcj02towgs84

def Get_poi_polygon(key,polygon,keywords,page):
    '''
    这是一个能够从高德地图获取poi数据的函数
    key：为用户申请的高德密钥
    polygon：目标城市四个点的坐标
    keywords：POI数据的类型
    page：当前页数
    '''
    #设置header
    header = {'User-Agent': "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"}

    #将输进来的矩形进行格式化
    Polygonstr = str(polygon[0]) + ',' + str(polygon[1]) + '|' + str(polygon[2]) + ',' + str(polygon[3])

    #构建url
    # url = 'https://restapi.amap.com/v3/place/polygon?polygon={}&key={}&keywords={}&page={}'.format(Polygonstr, key, keywords, page)
    url = 'https://restapi.amap.com/v3/place/polygon?polygon={}&key={}&types={}&page={}'.format(Polygonstr, key, keywords, page)
    print(url)
    #用get函数请求数据
    r = requests.get(url, headers=header)

    #设置数据的编码为'utf-8'
    # r.encoding = 'utf-8'
    r.encoding = 'utf-8-sig'

    # 将请求得到的数据按照'utf-8'编码成字符串
    data = r.text
    return data

def Get_times_polygon(key,polygon,keywords,city):
    '''
    这是一个控制Get_poi_polygon申请次数的函数
    '''
    page = 1
    # 执行以下代码，直到count为0的时候跳出循环
    while True:
        # 调用第一个函数来获取数据
        result = Get_poi_polygon(key,polygon, keywords, page)
        # json.loads可以对获取回来JSON格式的数据进行解码
        content = json.loads(result)
        pois = content['pois']
        count = content['count']
        print(count)
        #如果区域内poi的数量大于800，则认为超过上限，返回False请求对区域进行切割
        if int(count) > 800:
            return False
        else:
            for i in range(len(pois)):
                id=pois[i]['id']
                biz_type=pois[i]['biz_type']
                name = pois[i]['name']
                type = pois[i]['type']
                location = pois[i]['location']
                if 'address' not in pois[i].keys():
                    address = str(-1)
                else:
                    address = pois[i]['address']
                tel=pois[i]['tel']
                # 坐标转换
                # result = gcj02towgs84(location)
                # lng = result[0]
                # lat = result[1]
                lng=location.split(',')[0]
                lat=location.split(',')[1]
                # 这里尝试解决adname的问题
                # adname=content[i]['adname']
                adname = pois[i]['adname']
                # pcode = content[i]['pcode']
                pname = pois[i]['pname']
                # citycode = pois[i]['citycode']
                cityname = pois[i]['cityname']
                # abcode = content[i]['abcode']
                # business_area = content[i]['business_area']
                rating=pois[i]['biz_ext']
                pcode=''
                citycode=''
                abcode=''
                business_area=''
                print(content)
                # print(pois)
                # row = [name, address, adname, lng, lat]
                row = [id,biz_type,name,type, address, tel,lng,lat,pcode,pname, citycode,cityname,abcode,adname,business_area,rating]
                #调用写入函数来保存数据
                writecsv(row, keywords,city)
            if count == '0':
                break
                # 递增page
            page = page + 1

def writecsv(poilist,keywords,city):
    """
    这是写入成csv文件的函数
    :param poilist:
    :param keywords:
    :return: 输出的结果存放在代码文件夹下
    """
    with open('out\\'+city+'{}.csv'.format(keywords),'a',newline='',encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(poilist)

def get_city_scope(key, cityname):
    # parameters = 'key={}&keywords={}&subdistrict={}&output=JSON&extensions=all'.format(key, cityname, 0)
    parameters = 'key={}&keywords={}&subdistrict={}&output=JSON&extensions=all'.format(key, cityname, 0)
    url = 'https://restapi.amap.com/v3/config/district?'
    # 设置header
    header = {'User-Agent': "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"}
    res = requests.get(url,params=parameters)
    jsonData = res.json()
    if jsonData['status'] == '1':
        district = jsonData['districts'][0]['polyline']
        district_list = re.split(';|\|',district)
        xlist, ylist = [], []
        for d in district_list:
            xlist.append(float(d.split(',')[0]))
            ylist.append(float(d.split(',')[1]))
        xmax = max(xlist)
        xmin = min(xlist)
        ymax = max(ylist)
        ymin = min(ylist)
        return [xmin, ymax, xmax, ymin]
    else:
        print ('fail to acquire: {}'.format(jsonData['info']))

def Quadrangle(key,polygon,keywords,city):
    """
    :param key:高德地图密钥
    :param polygon: 矩形左上跟右下坐标的列表
    :param keywords: poi关键词
    :return:
    """
    #准备一个空列表，存放切割后的子区域
    PolygonList = []
    for i in range(len(polygon)):
        currentMinlat = round(polygon[i][0],6)#当前区域的最小经度
        currentMaxlat = round(polygon[i][2],6)#当前区域的最大经度
        currentMaxlon = round(polygon[i][1],6)#当前区域的最大纬度
        currentMinlon = round(polygon[i][3],6)#当前区域的最小纬度

        cerrnt_list = [currentMinlat, currentMaxlon, currentMaxlat, currentMinlon]
        #将多边形输入获取函数中，判断区域内poi的数量
        status = Get_times_polygon(key,cerrnt_list,keywords,city)
        #如果数量大于800，那么返回False，对区域进行切分,否则返回区域的坐标对
        if status != False:
            print('该区域poi数量小于800，正在写入数据')
        else:
            #左上矩形
            PolygonList.append([
                currentMinlat, #左经
                currentMaxlon, #上纬
                (currentMaxlat+currentMinlat)/2, #右经
                (currentMaxlon+currentMinlon)/2]) #下纬
            #右上矩形
            PolygonList.append([
                (currentMaxlat+currentMinlat)/2,#左经
                currentMaxlon, #上纬
                currentMaxlat, #右经
                (currentMaxlon+currentMinlon)/2#下纬
            ])
            #左下矩形
            PolygonList.append([
                currentMinlat,#左经
                (currentMaxlon+currentMinlon)/2,#上纬
                (currentMaxlat+currentMinlat)/2,#右经
                currentMinlon#下纬
            ])
            #右下矩形
            PolygonList.append([
                (currentMaxlat+currentMinlat)/2,#左经
                (currentMaxlon+currentMinlon)/2,#上纬
                currentMaxlat,#右经
                currentMinlon#下纬
            ])
            print(len(PolygonList))
            if len(PolygonList) == 0:
                break
            else:
                Quadrangle(key,PolygonList,keywords)


#这里修改为自己的高德密钥 高的开放平台web服务申请
key ='61c256acd1b853e34a6b9a31033c399d'

#这里修改自己的poi类型
# keywords = '公共设施'
keywords = '购物服务'
# keywords = '交通设施服务'
# keywords = '金融保险服务'
# keywords = '体育休闲服务'

#这里输入想要查询的城市 # 310101 代表黄浦区
city = '310116'

#调用高德查询行政区的API接口来返回矩形坐标对
Retance = get_city_scope(key,city)

#存储区域矩形的列表
input_polygon = []
input_polygon.append(Retance)

Quadrangle(key,input_polygon,keywords,city)

