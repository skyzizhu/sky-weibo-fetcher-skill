#!/usr/bin/env python3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
"""
测试 statuses/friends_timeline 接口
"""
import requests
import json
from datetime import datetime

# 从配置文件加载
with open(os.path.join(BASE_DIR, 'weibo_config.json'), 'r', encoding='utf-8') as f:
    config = json.load(f)

ACCESS_TOKEN = config['access_token']
UID = config['uid']

print("=" * 60)
print("🔍 测试 statuses/friends_timeline 接口")
print("=" * 60)

# 调用 friends_timeline 接口
print(f"\n📱 正在获取当前用户及其关注用户的最新微博...")
friends_timeline_url = "https://api.weibo.com/2/statuses/friends_timeline.json"
params = {
    'access_token': ACCESS_TOKEN,
    'count': 50,  # 获取50条
    'feature': 0,
    'trim_user': 0  # 返回完整用户信息
}

try:
    response = requests.get(friends_timeline_url, params=params, timeout=10)

    if response.status_code != 200:
        print(f"❌ API请求失败: 状态码 {response.status_code}")
        print(f"响应: {response.text}")
        exit(1)

    data = response.json()

    if 'error_code' in data:
        print(f"❌ API错误: {data.get('error', '未知错误')}")
        print(f"错误码: {data['error_code']}")
        exit(1)

    if 'statuses' not in data:
        print(f"❌ 响应中没有微博数据")
        print(f"响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
        exit(1)

    statuses = data['statuses']
    total_number = data.get('total_number', len(statuses))

    print(f"✅ 获取成功")
    print(f"📊 总微博数: {total_number}")
    print(f"📋 本次获取: {len(statuses)} 条微博")

    if len(statuses) == 0:
        print("⚠️ 暂无微博数据")
        exit(0)

    # 分析微博来源
    print("\n" + "=" * 60)
    print("📊 微博来源分析:")
    print("=" * 60)

    # 统计微博来源
    from collections import Counter
    user_counter = Counter()

    for status in statuses:
        user = status.get('user', {})
        user_name = user.get('screen_name', '未知')
        user_id = user.get('id', '')
        user_counter[user_name] += 1

    print(f"✅ 来自 {len(user_counter)} 个不同的用户\n")

    # 显示每个用户的微博数
    for i, (user_name, count) in enumerate(user_counter.most_common(10), 1):
        print(f"{i}. {user_name}: {count} 条")

    # 显示部分微博内容
    print("\n" + "=" * 60)
    print("📝 微博内容预览 (前5条):")
    print("=" * 60)

    for i, status in enumerate(statuses[:5], 1):
        user = status.get('user', {})
        user_name = user.get('screen_name', '未知')
        weibo_text = status.get('text', '')[:100]
        created_at = status.get('created_at', '')
        reposts_count = status.get('reposts_count', 0)
        comments_count = status.get('comments_count', 0)
        attitudes_count = status.get('attitudes_count', 0)

        print(f"\n{i}. @{user_name}")
        print(f"   内容: {weibo_text}...")
        print(f"   时间: {created_at}")
        print(f"   互动: 转发{reposts_count} 评论{comments_count} 点赞{attitudes_count}")

    # 检查是否有自己的微博
    print("\n" + "=" * 60)
    print("🔍 检查是否包含自己的微博:")
    print("=" * 60)

    my_weibos = [s for s in statuses if str(s.get('user', {}).get('id', '')) == UID]
    if my_weibos:
        print(f"✅ 包含 {len(my_weibos)} 条自己的微博")
    else:
        print(f"❌ 不包含自己的微博")

    print(f"\n💡 说明:")
    print(f"   - friends_timeline 获取的是【关注】用户的微博，不是【粉丝】")
    print(f"   - 如果要获取粉丝的微博，需要先关注这些粉丝")
    print(f"   - 或者使用其他方式（如网页爬虫）")

except Exception as e:
    print(f"❌ 发生错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print(f"⏰ 测试完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
