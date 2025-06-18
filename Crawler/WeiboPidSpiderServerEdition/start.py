import crawler
import buildip
import time
import yagmail
import pandas as pd
import sqlite3
import datetime
import time


if __name__ == "__main__":
    ########################### 自己设置区 ###############################
    emailhost = "smtp.qq.com"
    emailname = "473161189@qq.com"
    emailpassword = "hspxxpupkwowbggg"  # 授权码 需要到邮箱的设置里面 开启授权
    #####################################################################

    # 发送者的邮箱名和授权码以及host
    yag = yagmail.SMTP(user=emailname, password=emailpassword, host=emailhost)
    # 被发送的邮箱名和内容
    yag.send(to=emailname, subject="开始爬取微博内容", contents="爬取文本信息\n"+"运行时间"+f"{str(datetime.datetime.now())}")

    # 位置个数 读取带有pid的位置csv文件 获得长度
    temp_pd = pd.read_csv("data/Shanghai_Pid_buy.csv",encoding='utf-8-sig')  # 出错的话改成gbk
    
    # temp_pd = pd.read_csv("data\shanghai.csv")  # 出错的话改成gbk
    
    n = len(temp_pd)
    print(temp_pd)

    while True:
        time_start = time.time()

        # 建立代理池
        ippool = buildip.buildippool()
        print(
            "*************************现在开始爬取总共%s个地点的微博*********************"
            % str(n)
        )

        # 建立进程
        for i in range(n):
            crawler.main(i, ippool, yag, emailname)
            # crawler.main(i, ippool)

        time_end = time.time()
        print(" time cost ", time_end - time_start, "s")
        print("***********************休息三小时再继续爬********************")

        # ↓↓这段代码用于连接到一个名为"weibo.sqlite"的SQLite数据库，然后从中选择名为"weibo"的表。
        # 接着，它使用Pandas的read_sql_query函数将数据从数据库中读取到一个名为weibo_pd的数据框中。
        # 然后，它使用value_counts方法来统计每个地点出现的次数，并将结果转换为一个字典。
        # 最后，它计算了数据框的行数，并将结果存储在wb_m变量中，最后关闭了数据库连接
        # conn = sqlite3.connect("weibo.sqlite")
        # weibo_pd = pd.read_sql_query("SELECT * FROM weibo", conn)
        # wb_detail = weibo_pd["place"].value_counts().to_dict()
        # wb_m = weibo_pd.shape[0]
        # conn.close()

        yag.send(
            to=emailname,
            subject="All Done",
            contents=[
                # "这一段时间的都爬完了，三个小时后继续。耗时{}秒。现在共有微博{}条。具体微博情况为{}".format(
                #     time_end - time_start, wb_m, wb_detail
                "这一段时间的都爬完了，三个小时后继续。耗时{}秒。现在共有微博{}条。具体微博情况为{}".format(
                    time_end - time_start, " 微博条数 ", " 具体微博情况 "
                )
            ],
        )

        time.sleep(10800)
