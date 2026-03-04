#!/usr/bin/env python3
"""
测试不同的微博API端点
"""
import requests
import json

# 从配置文件加载
with open('weibo_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

ACCESS_TOKEN = config['access_token']
UID = config['uid']

print("=" * 60)
print("🔍 测试不同的微博API端点")
print("=" * 60)

# 测试多个可能的API端点
api_endpoints = [
    {
        'name': 'friendships/followers (旧)',
        'url': 'https://api.weibo.com/2/friendships/followers',
        'params': {'access_token': ACCESS_TOKEN, 'uid': UID, 'count': 10}
    },
    {
        'name': 'friendships/followers (新)',
        'url': 'https://api.weibo.cn/2/friendships/followers',
        'params': {'access_token': ACCESS_TOKEN, 'uid': UID, 'count': 10}
    },
    {
        'name': 'users/show (获取用户信息)',
        'url': 'https://api.weibo.com/2/users/show',
        'params': {'access_token': ACCESS_TOKEN, 'uid': UID}
    },
    {
        'name': 'statuses/user_timeline (获取微博列表)',
        'url': 'https://api.weibo.com/2/statuses/user_timeline',
        'params': {'access_token': ACCESS_TOKEN, 'uid': UID, 'count': 5}
    },
    {
        'name': 'statuses/home_timeline (获取首页时间线)',
        'url': 'https://api.weibo.com/2/statuses/home_timeline',
        'params': {'access_token': ACCESS_TOKEN, 'count': 5}
    },
]

working_endpoints = []

for api in api_endpoints:
    print(f"\n测试: {api['name']}")
    print(f"URL: {api['url']}")

    try:
        response = requests.get(api['url'], params=api['params'], timeout=10)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                if 'error_code' in data:
                    print(f"❌ API错误: {data.get('error', '未知错误')} (错误码: {data['error_code']})")
                else:
                    print(f"✅ 成功!")
                    working_endpoints.append(api['name'])

                    # 显示部分数据
                    if 'statuses' in data and len(data['statuses']) > 0:
                        print(f"   - 获取到 {len(data['statuses'])} 条微博")
                    elif 'user' in data:
                        print(f"   - 用户: {data['user'].get('screen_name', '未知')}")
                    elif 'users' in data:
                        print(f"   - 获取到 {len(data['users'])} 个用户")
            except:
                print(f"⚠️ 响应不是JSON格式")
                print(f"   前100字符: {response.text[:100]}")
        else:
            print(f"❌ 失败: {response.text[:100]}")

    except Exception as e:
        print(f"❌ 异常: {e}")

# 总结
print("\n" + "=" * 60)
print("📊 测试总结:")
print("=" * 60)
print(f"✅ 可用的端点: {len(working_endpoints)}")
for endpoint in working_endpoints:
    print(f"   - {endpoint}")

if len(working_endpoints) == 0:
    print("\n⚠️ 没有可用的API端点")
    print("\n💡 可能的原因:")
    print("   1. Access Token权限不足")
    print("   2. 应用未获得相应权限")
    print("   3. API版本已更新，需要查看最新文档")
    print("   4. 某些功能已不再开放给第三方应用")

print("\n" + "=" * 60)
