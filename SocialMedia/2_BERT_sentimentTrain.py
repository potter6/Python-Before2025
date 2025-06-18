import csv
import torch
import pandas as pd
import numpy as np
import psutil
from pandarallel import pandarallel
from transformers import BertForSequenceClassification, BertTokenizer, BertConfig, AdamW, get_linear_schedule_with_warmup
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from tqdm import trange, tqdm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

def clean_content(content):
    import re
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

# 定义分词函数
def get_tokens(text, tokenizer, max_seq_length, add_special_tokens=True):
    input_ids = tokenizer.encode(text, add_special_tokens=add_special_tokens, truncation=True, max_length=max_seq_length, pad_to_max_length=True)
    attention_mask = [int(id > 0) for id in input_ids]
    assert len(input_ids) == max_seq_length
    assert len(attention_mask) == max_seq_length
    return (input_ids, attention_mask)

if __name__=='__main__':
    # 初始化pandarallel
    pandarallel.initialize(nb_workers=psutil.cpu_count(logical=False))

    # 读取数据
    df_label = pd.read_csv('weibo_senti_100k.csv')
    print(len(df_label))
    # 清洗数据
    df_label['review'] = df_label['review'].parallel_apply(clean_content)
    print(len(df_label))
    # 去除空的行
    df_label= df_label[df_label['review'] != '']
    print(len(df_label))
    df_label=df_label[(df_label['review'].apply(lambda x: len(x)>3))]
    print("保留字数大于3完成"+str(len(df_label)))

    # 数据预处理
    df_label.label.value_counts()
    df = df_label.copy()
    # df=df[(df['sentiment']==-1)|(df['sentiment']==0)|(df['sentiment']==1)]
    

    # df.loc[df[df.sentiment!=6].index,'sentiment'] = 1
    # df = df[(df['sentiment']==1) | (df['sentiment']==6)]
    # drop_size = len(df[df['sentiment']==1].sentiment) - len(df[df['sentiment']==6].sentiment)
    # df.drop(df[df['sentiment']==1].sample(drop_size).index, inplace=True)
    # df.loc[df[df.sentiment==6].index,'sentiment'] = 0
    
    print(df.label.unique())
    print(df)

    # 划分训练集和测试集(8:2)
    X_train, X_test, Y_train, Y_test = train_test_split(df['review'], df['label'], test_size=0.2, random_state=42, stratify=df['label'])
    # X_train, X_test, Y_train, Y_test = train_test_split(df['message'], df['sentiment'], test_size=0.7, random_state=42, stratify=df['sentiment'])

    # 加载BERT模型和分词器
    model_name = 'bert-base-chinese'
    config = BertConfig.from_pretrained('model/' + model_name)
    tokenizer = BertTokenizer.from_pretrained('model/' + model_name)
    model = BertForSequenceClassification.from_pretrained('model/' + model_name, num_labels=2)
    # 三分法
    # config = BertConfig.from_pretrained('model/' + model_name, num_labels=3)
    # tokenizer = BertTokenizer.from_pretrained('model/' + model_name)
    # model = BertForSequenceClassification.from_pretrained('model/' + model_name, config=config)

    # 对训练集和测试集进行分词
    X_train_tokens = X_train.apply(get_tokens, args=(tokenizer, 150))
    X_test_tokens = X_test.apply(get_tokens, args=(tokenizer, 150))

    # 转换为PyTorch张量
    input_ids_train = torch.tensor([features[0] for features in X_train_tokens.values], dtype=torch.long)
    input_mask_train = torch.tensor([features[1] for features in X_train_tokens.values], dtype=torch.long)
    label_ids_train = torch.tensor(Y_train.values, dtype=torch.long)

    input_ids_test = torch.tensor([features[0] for features in X_test_tokens.values], dtype=torch.long)
    input_mask_test = torch.tensor([features[1] for features in X_test_tokens.values], dtype=torch.long)
    label_ids_test = torch.tensor(Y_test.values, dtype=torch.long)

    # 创建数据集
    train_dataset = TensorDataset(input_ids_train, input_mask_train, label_ids_train)
    test_dataset = TensorDataset(input_ids_test, input_mask_test, label_ids_test)

    # 训练参数
    train_batch_size = 64
    num_train_epochs = 3
    train_sampler = RandomSampler(train_dataset)
    train_dataloader = DataLoader(train_dataset, sampler=train_sampler, batch_size=train_batch_size)
    t_total = len(train_dataloader) // num_train_epochs

    # 输出一些训练相关的信息
    print("样本数量 =", len(train_dataset))  # 输出训练集样本数量
    print("训练周期数 =", num_train_epochs)  # 输出训练周期数
    print("总的训练批次大小 =", train_batch_size)  # 输出总的训练批次大小
    print("总的优化步数 =", t_total)  # 输出总的优化步数

    # 优化器和学习率调度器
    learning_rate = 5e-5
    adam_epsilon = 1e-8
    warmup_steps = 0
    optimizer = AdamW(model.parameters(), lr=learning_rate, eps=adam_epsilon)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=t_total)

    # 设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 训练模型
    model.train()
    train_iterator = trange(num_train_epochs, desc="Epoch")
    for epoch in train_iterator:
        epoch_iterator = tqdm(train_dataloader, desc="Iteration")
        # 创建csv文件并写入表头
        with open('loss.csv', 'a', newline='') as csvfile:
            fieldnames = ['epoch', 'step', 'loss']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for step, batch in enumerate(epoch_iterator):
                model.zero_grad()
                model.to(device)
                cuda=next(model.parameters()).device
                batch = tuple(t.to(device) for t in batch)
                inputs = {
                    'input_ids': batch[0], # 输入特征ID
                    'attention_mask': batch[1],  # 输入掩码
                    'labels': batch[2]} # 标签
                # 通过模型进行 前向传播：输入->模型->输出
                outputs = model(**inputs)
                # 计算损失
                loss = outputs[0]
        
                # 在循环内部保存epoch、step和loss到csv文件
                writer.writerow({'epoch': epoch, 'step': step, 'loss': loss.item()})

                # 打印损失值
                print("\r%f" % loss,end='')

                # 反响传播损失，自动计算梯度
                loss.backward()
        
                # 通过将梯度限制在一定范围内来防止梯度爆炸
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

                # 更新模型参数和学习率
                optimizer.step()
                scheduler.step()


    # 保存模型
    model.save_pretrained('Model10k')

    # 评估模型
    test_batch_size = 64
    test_sampler = SequentialSampler(test_dataset)
    test_dataloader = DataLoader(test_dataset, sampler=test_sampler, batch_size=test_batch_size)

    model.eval()
    preds = None
    out_label_ids = None

    for batch in tqdm(test_dataloader, desc="评估中"):
        model.to(device)
        batch = tuple(t.to(device) for t in batch)
        with torch.no_grad():
            inputs = {'input_ids': batch[0], 'attention_mask': batch[1], 'labels': batch[2]}
            outputs = model(**inputs)
            tmp_eval_loss, logits = outputs[:2]
            if preds is None:
                preds = logits.detach().cpu().numpy()
                out_label_ids = inputs['labels'].detach().cpu().numpy()
            else:
                preds = np.append(preds, logits.detach().cpu().numpy(), axis=0)
                out_label_ids = np.append(out_label_ids, inputs['labels'].detach().cpu().numpy(), axis=0)

    preds = np.argmax(preds, axis=1)
    acc_score = accuracy_score(preds, out_label_ids)
    f1_score = f1_score(preds, out_label_ids)
    # f1_score_macro = f1_score(preds, out_label_ids, average='macro')
    print('测试集中的Accuracy分数: ', acc_score)
    print('测试集中的F1分数: ', f1_score)
    # print('测试集中的F1分数(macro): ', f1_score_macro)
