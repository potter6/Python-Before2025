import pandas as pd
import numpy as np
import torch
from transformers import BertForSequenceClassification, BertTokenizer
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
from tqdm import tqdm

def clean_content(content,place):
    import re
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

if __name__=='__main__':
    # 文件路径（文件名）
    filename='20190301_20190401 26184 条_Baidu&Tencent 21747 条.csv'

    # 读取数据
    df_origin = pd.read_csv(filename)

    # 统一初始化为0
    df_origin['label'] = 0  

    X_pred = df_origin['text']
    Y_pred = df_origin['label']

    # 加载BERT模型和分词器
    model_name = 'bert-base-chinese'
    # tokenizer = BertTokenizer.from_pretrained('My_Model/weibo-bert-rubbish-model')
    # model = BertForSequenceClassification.from_pretrained('My_Model/weibo-bert-rubbish-model')
    model = BertForSequenceClassification.from_pretrained('model_trained/Model2.4万条/weibo-bert-rubbish-model')
    tokenizer = BertTokenizer.from_pretrained('model/bert-base-chinese')

    # 定义分词函数
    def get_tokens(text, tokenizer, max_seq_length, add_special_tokens=True):
        input_ids = tokenizer.encode(text, add_special_tokens=add_special_tokens, truncation=True, max_length=max_seq_length, pad_to_max_length=True)
        attention_mask = [int(id > 0) for id in input_ids]
        assert len(input_ids) == max_seq_length
        assert len(attention_mask) == max_seq_length
        return (input_ids, attention_mask)

    X_pred_tokens = X_pred.apply(get_tokens, args=(tokenizer, 150))

    input_ids_pred = torch.tensor([features[0] for features in X_pred_tokens.values], dtype=torch.long)
    input_mask_pred = torch.tensor([features[1] for features in X_pred_tokens.values], dtype=torch.long)
    label_pred = torch.tensor(Y_pred.values, dtype=torch.long)
    pred_dataset = TensorDataset(input_ids_pred, input_mask_pred, label_pred)

    # pred_batch_size = 256
    # 降低batch_size以减少显存占用
    pred_batch_size = 128
    pred_sampler = SequentialSampler(pred_dataset)
    pred_dataloader = DataLoader(pred_dataset, sampler=pred_sampler, batch_size=pred_batch_size)

    # 预测
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    preds = None
    for batch in tqdm(pred_dataloader, desc="Predict"):
        batch = tuple(t.to(device) for t in batch)
        with torch.no_grad():
            inputs = {
                'input_ids': batch[0],
                'attention_mask': batch[1],
                'labels': batch[2]
            }
            outputs = model(**inputs)
            _, logits = outputs[:2]

            if preds is None:
                preds = logits.detach().cpu().numpy()
            else:
                preds = np.append(preds, logits.detach().cpu().numpy(), axis=0)

    prob = torch.nn.functional.softmax(torch.tensor(preds), dim=1)  # 使用softmax函数计算预测的概率分布
    preds = np.argmax(preds, axis=1)  # 计算每个样本的最终预测类别
    # df_origin['BERT_ad_prob'] = [p[1].item() for p in prob]  # 将概率分布的第二列（表示"1"类别的概率）添加到DataFrame中
    # 将概率分布和预测类别添加到DataFrame中
    df_origin['BERT_prob_0']=[p[0].item() for p in prob] # 类别0的概率
    df_origin['BERT_prob_1']=[p[1].item() for p in prob] # 类别1的概率
    df_origin['BERT_prob_2']=[p[2].item() for p in prob] # 类别2的概率
    df_origin['BERT_pred'] = preds  # 将最终的预测类别添加到DataFrame中

    df_origin.to_csv('20190301_20190401 26184 条_Baidu&Tencent&BERT3th 21747 条.csv', index=False,encoding='utf-8-sig')
    df_origin.sample(10)
