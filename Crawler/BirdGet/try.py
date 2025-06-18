import json
import requests
from functools import partial
import time
import hashlib
import subprocess
subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")
import execjs
from urllib.parse import urlencode
from Crypto.Cipher import AES
import base64
from Crypto.Util.Padding import pad,unpad


url = "https://api.birdreport.cn/front/record/activity/search"

e = {
    "limit":"20",
    "page":"4",
    "pointname":"梧桐沟"
}

# url编码
e = urlencode(e)

# 读取并执行js代码
with open("bird.js", 'r') as f:
    jscode = f.read()
js = execjs.compile(jscode)
res = js.call("jiami",e)

# 获取请求头和data
headers = res.get('header')
data = res.get("data")

# 补充请求头
headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
    "Referer":"https://www.birdreport.cn/",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
})

res = requests.post(url=url, data=data, headers=headers)
data = res.json().get("data")

# base64解码
data = base64.b64decode(data)

# aes解密
key = "3583ec0257e2f4c8195eec7410ff1619"
iv = "d93c0d5ec6352f20"
aes = AES.new(key.encode('utf-8'), AES.MODE_CBC,iv.encode())
ret = aes.decrypt(data)
print(ret.decode())