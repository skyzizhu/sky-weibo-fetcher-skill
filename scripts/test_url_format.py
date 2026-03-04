#!/usr/bin/env python3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
"""
测试不同的URL格式
"""
import requests
import json

# 从配置文件加载
with open(os.path.join(BASE_DIR, 'weibo_config.json'), 'r', encoding='utf-8') as f:
    config = json.load(f)

ACCESS_TOKEN = config['access_token']
UID = config['uid']

print("=" * 60)
print("🔍 测试不同的URL格式")
print("=" * 60)

# 测试不同的URL格式
test_cases = [
    {
        'name': 'api.weibo.com/2/friendships/followers (无.json)',
        'url': 'https://api.weibo.com/2/friendships/followers',
        'params': {'access_token': ACCESS_TOKEN, 'uid': UID, 'count': 10}
    },
    {
        'name': 'api.weibo.com/2/friendships/followers.json (有.json)',
        'url': 'https://api.weibo.com/2/friendships/followers.json',
        'params': {'access_token': ACCESS_TOKEN, 'uid': UID, 'count': 10}
    },
    {
        'name': 'api.weibo.cn/2/friendships/followers (无.json)',
        'url': 'https://api.weibo.cn/2/friendships/followers',
        'params': {'access_token': ACCESS_TOKEN, 'uid': UID, 'count': 10}
    },
    {
        'name': 'api.weibo.cn/2/friendships/followers.json (有.json)',
        'url': 'https://api.weibo.cn/2/friendships/followers.json',
        'params': {'access_token': ACCESS_TOKEN, 'uid': UID, 'count': 10}
    },
]

working_cases = []

for test in test_cases:
    print(f"\n测试: {test['name']}")
    print(f"URL: {test['url']}")

    try:
        response = requests.get(test['url'], params=test['params'], timeout=10)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                if 'error_code' in data:
                    print(f"❌ API错误: {data.get('error', '未知错误')} (错误码: {data['error_code']})")
                else:
                    print(f"✅ 成功!")
                    working_cases.append(test['name'])

                    # 显示部分数据
                    if 'users' in data and len(data['users']) > 0:
                        print(f"   - 获取到 {len(data['users'])} 个用户")
                    elif 'statuses' in data and len(data['statuses']) > 0:
                        print(f"   - 获取到 {len(data['statuses'])} 条微博")
            except Exception as e:
                print(f"⚠️ 响应不是有效的JSON")
                print(f"   前100字符: {response.text[:100]}")
        else:
            print(f"❌ 失败: {response.text[:100]}")

    except Exception as e:
        print(f"❌ 异常: {e}")

# 总结
print("\n" + "=" * 60)
print("📊 测试总结:")
print("=" * 60)
print(f"✅ 可用的URL格式: {len(working_cases)}")
for case in working_cases:
    print(f"   - {case}")

print("\n" + "=" * 60)
