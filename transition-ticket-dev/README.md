# Transition Ticket

## 声明

[电报交流群](https://t.me/bilibili_ticket)

本程序仅供学习交流, 不得用于商业用途,

使用本程序进行违法操作产生的法律责任由操作者自行承担,

对本程序进行二次开发/分发时请注意遵守GPL-3.0开源协议,

本脚本仅适用于蹲回流票, 我们反对将其用于抢票,

黄牛/收费代抢４０００＋.

## 使用

[下载地址](https://github.com/biliticket/transition-ticket/releases)

注意:

1. MacOS/Linux用户请根据*手动安装*流程安装进行使用;
2. 现仅支持部分活动, 主要是类似于BW2024这样的*实名制 一人一票 无选座*活动, 后期会增加更多类型的票务支持;
3. 如使用浏览器登录功能, 您的电脑里必须安装Chrome/Edge/Firefox浏览器, 如有安装还是提供无法启动, 则需要自行安装其中一个浏览器的Web Driver,
4. assest/alarm.wav文件为语音提醒文件, 可自行更换其他提示音.

### 手动安装

- Python >=3.10,<3.13

```bash
# MacOS
brew install portaudio
# Ubuntu
sudo apt-get install portaudio19-dev

git clone https://github.com/biliticket/transition-ticket.git
cd transition-ticket
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install virtualenv

virtualenv venv
source venv/script/activate
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt
python cli.py
```

## 运行流程

![FSM](assest/fsm.png)

## 开发计划

- [ ] Async
- [ ] 其他票种可购情况
- [ ] 检测配置文件完整性
- [ ] 修改打包模式为目录模式, 而不是单文件模式
- [ ] 显示版本号
- [ ] 多种类型活动抢票
- [ ] 参数启动
- [ ] 图形界面(PySide6)

## 开发

- Python >=3.10,<3.13

```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install poetry virtualenv

virtualenv venv
source venv/script/activate
poetry install --with dev,graph
pre-commit install

# 更新
poetry update
pip freeze > requirements.txt
pre-commit autoupdate

# 打包
pyinstaller --clean --noconfirm --log-level WARN cli.spec
```

## 感谢

- [Amorter/biliTicker_gt](https://github.com/Amorter/biliTicker_gt)
- [Just-Prog/Bilibili_show_ticket_auto_order](https://github.com/Just-Prog/Bilibili_show_ticket_auto_order)
- [biliticket/BHYG](https://github.com/biliticket/BHYG)
- [mikumifa/biliTickerBuy](https://github.com/mikumifa/biliTickerBuy)
