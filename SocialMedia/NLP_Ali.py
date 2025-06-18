import pandas as pd

data=pd.read_csv('data/上海2019_2023年按月分类文件/20190101_20190201 22491 条.csv')
print(len(data)) #数据的行数
print(data.head(5))

# 阿里的Key导入 ################################################################################################
import json

# 这里以分词为例，其它算法的API名称和参数请参考文档
from aliyunsdkalinlp.request.v20200629 import GetWsCustomizedChGeneralRequest
# 调用阿里的NLP
from aliyunsdkalinlp.request.v20200629 import GetSaChGeneralRequest

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException

'''
 * 阿里云账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM用户进行API访问或日常运维，请登录RAM控制台创建RAM用户。
 * 此处以把AccessKey和AccessKeySecret保存在环境变量为例说明。您也可以根据业务需要，保存到配置文件里。
 * 强烈建议不要把AccessKey和AccessKeySecret保存到代码里，会存在密钥泄漏风险
'''

# access_key_id = os.environ['NLP_AK_ENV']
# access_key_secret = os.environ['NLP_SK_ENV']

key = pd.read_csv('data\key\AliAccessKey.csv')
# Key的读取  读取AccessKey和AccessKeySecret  
access_key_id = key['AccessKey ID'][0]
access_key_secret = key['AccessKey Secret'][0]

def ali_nlp(text):
    # 创建AcsClient实例
    client = AcsClient(
        access_key_id,
        access_key_secret,
        "cn-hangzhou"
    )
    request=GetSaChGeneralRequest.GetSaChGeneralRequest()
    # request.set_Text("云麦好轻智能体脂秤精准蓝牙秤体重测人体脂肪秤家用称健康电子秤")
    request.set_Text(text)
    request.set_ServiceCode("alinlp")
    response = client.do_action_with_exception(request)

    resp_obj = json.loads(response)

    # print(resp_obj)
    # print(resp_obj['Data'])

    jd=json.loads(resp_obj['Data'])
    # print(jd)

    # 提取所需的值
    positive_prob = jd['result']['positive_prob']
    sentiment = jd['result']['sentiment']
    neutral_prob = jd['result']['neutral_prob']
    negative_prob = jd['result']['negative_prob']


    return positive_prob, sentiment, neutral_prob, negative_prob

# 测试
text="你好, 我是一名学生, 我很开心, 你呢？"

pos,sen,neu,neg=ali_nlp(text)
print("阿里\npositive_prob",pos,"\nsentiment",sen,"\nneutral_prob",neu,"\nnegative_prob",neg)


# 进行数据清洗、情绪值提取#############################################################################
import pandas as pd
import re
import jieba
import numpy as np
import datetime
import csv
import time
from tqdm import tqdm


def clean_content(content,place):
    # 去除地名
    content = content.replace(place, '')
    # 去除一些关键词
    content = content.replace('分享图片', '').replace('分享视频', '').replace('微博视频', '').replace('的微博视频', '').replace('网页链接','').replace('超话','').replace('新浪图片','').replace('<br>','')
    # 去除英文
    content = re.sub(r'[a-zA-Z]+', '', content)
    content = re.sub(r'\d+', '', content).replace(' ', '').replace('.', '').replace('_','')
    # 去除所有非中文符号
    content = re.sub(r'[^\u4e00-\u9fa5]', '', content)
    # 去除空白字符
    content = re.sub(r'\s+', '', content)
    return content

# 对content列进行清洗 由对应的地名在文本中去除content文本中的内容
data['clean_content'] = data.apply(lambda row: clean_content(row['content'], row['content_location_name']), axis=1)
print("清洗完成")

# 如果文本为空 去掉该行
data = data[data['clean_content'] != '']
print("去除空白行完成")

# 保留字数大于3的
data=data[data['clean_content'].apply(lambda x: len(x)>3)]
print("保留字数大于3完成")

# 对清洗后的文本 进行 分词 放入jieba_cut列中
data['jieba_cut'] = data['clean_content'].apply(lambda x: jieba.lcut(x))
print("分词完成")
        
def process_row(row):
    try:
        time.sleep(0.1)
        positive_prob, sentiment, neutral_prob, negative_prob=ali_nlp(row['clean_content'])
        return positive_prob, sentiment, neutral_prob, negative_prob
    except:
        try:
            positive_prob, sentiment, neutral_prob, negative_prob=ali_nlp(row['clean_content'])
            return positive_prob, sentiment, neutral_prob, negative_prob
        except:
            return np.nan,np.nan,np.nan,np.nan

results = data.apply(process_row, axis=1)
data['ali_positive'], data['ali_sentiment'], data['ali_neutral'], data['ali_negative'] = zip(*results)
print("情感分析完成")

# 保存
filename = 'data\WeiboTrainData\sentiment_analysis_data(Ali)_{}_5.csv'.format(str(datetime.datetime.now()).split(' ')[0])
with open(filename, 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(data.columns)  # 写入列名
    for row in data.itertuples(index=False):
        writer.writerow(row)

data.head(5)
print("保存完成")

