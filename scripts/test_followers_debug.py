#!/usr/bin/env python3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
"""
调试：查看API原始响应
"""
import requests
import json

# 从配置文件加载
with open(os.path.join(BASE_DIR, 'weibo_config.json'), 'r', encoding='utf-8') as f:
    config = json.load(f)

ACCESS_TOKEN = config['access_token']
UID = config['uid']

print("=" * 60)
print("🔍 调试：查看API原始响应")
print("=" * 60)

# 获取粉丝列表
followers_url = "https://api.weibo.com/2/friendships/followers"
params = {
    'access_token': ACCESS_TOKEN,
    'uid': UID,
    'count': 10,
    'cursor': 0
}

print(f"\n请求URL: {followers_url}")
print(f"请求参数: {json.dumps(params, ensure_ascii=False, indent=2)}")

response = requests.get(followers_url, params=params, timeout=10)

print(f"\n响应状态码: {response.status_code}")
print(f"响应头:")
for key, value in response.headers.items():
    print(f"  {key}: {value}")

print(f"\n原始响应内容:")
print(response.text)

print(f"\n" + "=" * 60)
