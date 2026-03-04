#!/usr/bin/env python3
"""
测试不同page值的效果
"""
import requests
import json

# 从配置文件加载
with open('weibo_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

ACCESS_TOKEN = config['access_token']
UID = config['uid']

print("=" * 60)
print("🔍 测试不同page值的效果")
print("=" * 60)

# 测试不同的page值
for page in [1, 2, 3]:
    print(f"\n测试 page = {page}")

    url = "https://api.weibo.com/2/statuses/home_timeline.json"
    params = {
        'access_token': ACCESS_TOKEN,
        'count': 100,
        'page': page,
        'feature': 0,
        'trim_user': 0
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"   ❌ API请求失败: 状态码 {response.status_code}")
            continue

        data = response.json()

        if 'error_code' in data:
            error = data.get('error', '未知错误')
            error_code = data.get('error_code', '未知')
            print(f"   ❌ API错误: {error} ({error_code})")
            continue

        if 'statuses' not in data:
            print(f"   ⚠️ 响应中没有微博数据")
            continue

        statuses = data['statuses']
        total_number = data.get('total_number', 0)

        print(f"   ✅ 获取到 {len(statuses)} 条微博")
        print(f"   📊 total_number: {total_number}")

        if len(statuses) > 0:
            first_id = statuses[0].get('id')
            last_id = statuses[-1].get('id')
            first_time = statuses[0].get('created_at')
            last_time = statuses[-1].get('created_at')
            print(f"   📅 时间范围: {last_time} → {first_time}")
            print(f"   🆔 ID范围: {last_id} → {first_id}")

    except Exception as e:
        print(f"   ❌ 异常: {e}")

print("\n" + "=" * 60)
