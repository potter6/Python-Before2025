import pandas as pd

filename=r'D:\Code\Python\NLP24\output\20240801_20240901 60312 条_Baidu.csv'

# 数据输入 1 待提取情绪值的csv文件
data=pd.read_csv(filename)
tailname='_Baidu.csv' # 尾名 处理提取sentiment值后的文件

print('数据行数 ',len(data)) #数据的行数
data.sample(2) #查看2

# 百度的Key导入 ################################################################################################
import requests
import json

# 数据输入 2 装有key的csv文件
key = pd.read_csv("key\YaoBaiduAccesskey.csv")
# key的读取 
API_KEY = key['API_KEY'][0]
SECRET_KEY = key['SECRET_KEY'][0]

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

def baidu_nlp(text):
    url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?charset=UTF-8&access_token=" + get_access_token()
    params = {
        'access_token': 'your_access_token',
        'text': text
    }
    headers = {'Content-Type': 'application/json','Accept': 'application/json'}
        
    response = requests.request("POST",url, data=json.dumps(params), headers=headers)
    
    result = json.loads(response.text)
        
    result=response.json()

    for item in result['items']:
        confidence=item['confidence']
        negative_prob=item['negative_prob']
        positive_prob=item['positive_prob']
        sentiment=item['sentiment']
    
    return confidence, negative_prob, positive_prob,sentiment

# 测试 ################################################################################################
text="你好, 我是一名学生, 我很开心, 你呢？"
# text="谭鸭血"

c,n,p,s=baidu_nlp(text)
print("confidence",c,"\nnegative_prob",n,"\npositive_prob",p,"\nsentiment",s)

# 进行数据清洗、情绪值提取#############################################################################
import re
import jieba
import numpy as np
import datetime
from time import sleep
import random
import csv
import time
from tqdm import tqdm

def clean_content(content,place):
    # 去除地名
    content = content.replace(place, '')
    # 去除一些关键词
    content =content.replace('分享图片', '').replace('分享视频', '').replace('微博视频', '').replace('的微博视频', '').replace('网页链接','').replace('超话','').replace('新浪图片','').replace('<br>','')    
    # 去除英文
    content = re.sub(r'[a-zA-Z]+', '', content)
    content = re.sub(r'\d+', '', content).replace(' ', '').replace('.', '').replace('_','')
    # 去除所有非中文符号
    content = re.sub(r'[^\u4e00-\u9fa5]', '', content)
    # 去除空白字符
    content = re.sub(r'\s+', '', content)
    return content

time_start=time.time()
print("开始 ",datetime.datetime.now())

# # 对content列进行清洗 由对应的地名在文本中去除content文本中的内容
# data['clean_content']=data.apply(lambda row: clean_content(row['content'],row['content_location_name']),axis=1)
# print("清洗完成 "+str(len(data)))

# # 如果文本为空 去掉该行
# data=data[data['clean_content']!='']
# print("去除空白行完成 "+str(len(data)))

# # 保留文本字数大于3的和小于512的文本   百度是512字、腾讯是200字
# data=data[(data['clean_content'].apply(lambda x: len(x)<512)) & (data['clean_content'].apply(lambda x: len(x)>3))]
# print("保留字数大于3完成 "+str(len(data)))

# # 对清洗后的文本 进行 分词 放入jieba_cut列中
# data['jieba_cut']=data['clean_content'].apply(lambda x: jieba.lcut(x))
# print("分词完成 "+str(len(data)))

def process_row(row):
    try:
        # 如果是nan 这里被标注的if是后续的处理 不用管
        if pd.isna(row['baidu_confidence']):
            positive_prob, sentiment, neutral_prob, negative_prob=baidu_nlp(row['clean_content'])
            # 休息几秒钟 确保正确跑完 
            # sleep(0.04*random.randint(2,3)) # 0.04秒到0.06秒 之间随机休息比较好
            sleep(0.4) # 大量测试 0.1算比较合适 可以适当减少
            return positive_prob, sentiment, neutral_prob, negative_prob
        else:
            return row['baidu_confidence'], row['baidu_negative'], row['baidu_positive'], row['baidu_sentiment']
    except:
        # print(row["publish_time"] +' '+ row["clean_content"])
        print("百度API调用失败")
        return np.nan,np.nan,np.nan,np.nan

tqdm.pandas()
results=data.progress_apply(process_row, axis=1)
# results = data.apply(process_row, axis=1)
try: 
    data['baidu_confidence'], data['baidu_negative'], data['baidu_positive'], data['baidu_sentiment'] = zip(*results)
except:
    print("百度API调用失败，将results保存后退出")
    results.to_csv('error'+filename,index=False,encoding='utf-8-sig')
print("情感分析完成")

# 保存
with open(filename, 'w', encoding='utf-8-sig', newline='') as file:
# with open(dataoutputpath+filename.split('.')[0]+tailname, 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(data.columns)  # 写入列名
    for row in data.itertuples(index=False):
        writer.writerow(row)

print(data.head(5))
time_end=time.time()
print(filename,"\n本次运行总共耗时：",time_end-time_start,"\n即：",(time_end-time_start)/60,"分钟","\n即：",(time_end-time_start)/3600,"小时")
print("结束",datetime.datetime.now())
