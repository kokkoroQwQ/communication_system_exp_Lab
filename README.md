# 项目简介  

复旦大学2023年秋通信系统实验下第六组期末项目代码仓库

## 程序流程图 v0.0.1

![这是图片](/imgs/%E8%87%AA%E5%8A%A9%E7%94%B5%E8%AF%9D%E9%97%A8%E8%AF%8A%E6%8C%82%E5%8F%B7%E7%B3%BB%E7%BB%9F%E6%B5%81%E7%A8%8B%E5%9B%BEv0.0.1.jpg "")

## 环境

python 3.11

## 使用方法  

### 1 下载代码

```bash
git clone https://github.com/kokkoroQwQ/communication_system_exp_Lab.git
cd communication_system_exp_Lab
```

### 2 任意文本编辑器打开 server_run.py，自行修改以下信息

```python
#########################################################################
# custom config here

OM_IP = "10.16.18.150"  # your OM device's ip 你的 OM 设备 IP
HOST_ADDR = ("10.230.32.31", 8989) # your machine's ip and port 你的 PC 的 IP 和端口
AMOUNT_LIMIT = 100  # register amount limit 每个 科室-门诊级别-时间段 挂号的数量限额
HUMAN_SERVE_PHONE_NUMBER = '6214' # 人工服务的分机号
```

### 3 运行

```bash
python server_run.py
```

## 修订信息

* 时间：2023-12-12 版本：[发布]v1.0.0 概要：实现完全功能
