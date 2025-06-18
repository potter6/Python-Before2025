import requests
import re
import pandas as pd


# 爬取代理网站上可以用的代理，建立代理池
class Proxies:
    def __init__(
        self,
    ):  # 我们在学习 Python 类的时候，总会碰见书上的类中有 __init__() 这样一个函数，很多同学百思不得其解，其实它就是 Python 的构造方法。构造方法类似于init() 这种初始化方法，来初始化新创建对象的状态，在一个对象呗创建以后会立即调用。
        self.proxy_list = []  # 创建一个代理列表
        # headers的作用是告诉服务器，我们是从网页过来的，不是从python请求的。伪装浏览器。
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/78.0.3904.108 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br",
            "cookie": "SCF=AluwODJI40amKvbiRhhr3x3X5WFJsmVFhCfV1x9vjoqOxFZ7kpOWYf0PE0IkFY0VtUh_VNEYd4sk9n-yhLGDuHw.; SUB=_2A25Lbq3fDeRhGeFP4lMR8SvIyTmIHXVoBa8XrDV6PUJbktAGLULQkW1NQOrKxZGpxxcpRroXHSZbxqlhxcwIN16I; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFJf.nPypequXxyIBhJbGay5NHD95QNeK.peh2fShzfWs4DqcjPi--ci-z0i-2Ei--NiKn4i-z41h.Eehzt; SSOLoginState=1718279569; ALF=1720871569; _T_WM=70709609309; XSRF-TOKEN=f5a40a; WEIBOCN_FROM=1110006030; MLOGIN=1; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D100101B2094655D36DA6FD449F%26fid%3D100101B2094655D36DA6FD449F%26uicode%3D10000011",
        }

    # 源代码的
    # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
    # "Chrome/45.0.2454.101 Safari/537.36",
    #'Accept-Encoding': 'gzip, deflate, sdch',

    # 读取代理ip
    def get_proxy_nn(self):
        df = pd.read_excel(
            # io='E:/python/python_workspace/Sina Weibo/GitHub_RealIvyWong（根据POI的id爬取POI信息）/WeiboCrawler-master(修改)/WeiboLocationCrawler_poi_noclean/ip.xlsx',
            # 这里要换成使用代理IP的xlsx的绝对路径
            io="data\ip.xlsx",
            sheet_name="Sheet1",  # 指定读取的sheet
            header=0,  # 指定列名的行
            usecols="A",
        )
        proxy_list = df["ip"].values.tolist()
        return proxy_list
        print(proxy_list)

    # 验证代理是否能用
    def verify_proxy(self, proxy_list):
        for proxy in proxy_list:
            proxies = {"http": proxy}
            try:
                # if requests.get('http://www.baidu.com', proxies=proxies, timeout=5).status_code == 200:
                if (
                    requests.get(
                        "https://www.baidu.com", proxies=proxies, timeout=5
                    ).status_code
                    == 200
                ):
                    if proxy not in self.proxy_list:
                        self.proxy_list.append(proxy)
                    print("Success", proxy)
            except:
                print("Fail", proxy)

    # 保存到ippool这个List里
    def save_proxy(self):
        ippool = []
        print("开始存入代理池...")
        # 把可用的代理添加到代理池中
        for proxy in self.proxy_list:
            proxies = {"http": proxy}
            ippool.append(proxies)
        return ippool


# 使用上面的类建立代理池
def buildippool():
    p = Proxies()
    results = p.get_proxy_nn()
    print("爬取到的代理数量", len(results))
    print("开始验证：")
    p.verify_proxy(results)
    print("验证完毕：")
    print("可用代理数量：", len(p.proxy_list))
    ippool = p.save_proxy()
    return ippool
