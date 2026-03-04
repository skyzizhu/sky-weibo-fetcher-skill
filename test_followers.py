#!/usr/bin/env python3
"""
测试获取用户粉丝列表及粉丝最新微博
"""
import requests
import json
from datetime import datetime

# 从配置文件加载
with open('weibo_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

ACCESS_TOKEN = config['access_token']
UID = config['uid']

print("=" * 60)
print("🔍 测试获取粉丝列表及粉丝微博")
print("=" * 60)

# 第一步：获取粉丝列表
print(f"\n📋 正在获取用户 {UID} 的粉丝列表...")
followers_url = "https://api.weibo.com/2/friendships/followers"
params = {
    'access_token': ACCESS_TOKEN,
    'uid': UID,
    'count': 10,  # 先获取10个测试
    'cursor': 0
}

try:
    response = requests.get(followers_url, params=params, timeout=10)
    data = response.json()

    if 'users' not in data:
        print(f"❌ 获取粉丝列表失败")
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        exit(1)

    followers = data['users']
    total_count = data.get('total_number', len(followers))

    print(f"✅ 获取到粉丝列表")
    print(f"📊 总粉丝数: {total_count}")
    print(f"📋 本次获取: {len(followers)} 个粉丝")

    if len(followers) == 0:
        print("⚠️ 暂无粉丝数据")
        exit(0)

    # 显示粉丝列表
    print("\n" + "=" * 60)
    print("👥 粉丝列表:")
    print("=" * 60)
    for i, follower in enumerate(followers, 1):
        screen_name = follower.get('screen_name', '未知')
        followers_count = follower.get('followers_count', 0)
        statuses_count = follower.get('statuses_count', 0)
        description = follower.get('description', '')[:30]

        print(f"\n{i}. {screen_name}")
        print(f"   UID: {follower['id']}")
        print(f"   粉丝数: {followers_count} | 微博数: {statuses_count}")
        if description:
            print(f"   简介: {description}...")

    # 第二步：获取粉丝的最新微博
    print("\n" + "=" * 60)
    print("📝 获取粉丝最新微博（前5位）:")
    print("=" * 60)

    followers_weibo = []

    for i, follower in enumerate(followers[:5], 1):
        follower_uid = follower['id']
        follower_name = follower.get('screen_name', '未知')

        print(f"\n{i}. 正在获取 {follower_name} 的微博...")

        user_timeline_url = "https://api.weibo.com/2/statuses/user_timeline"
        params_timeline = {
            'access_token': ACCESS_TOKEN,
            'uid': follower_uid,
            'count': 3,  # 每人获取3条最新微博
            'feature': 0
        }

        try:
            timeline_response = requests.get(user_timeline_url, params=params_timeline, timeout=10)
            timeline_data = timeline_response.json()

            if 'statuses' in timeline_data and len(timeline_data['statuses']) > 0:
                statuses = timeline_data['statuses']
                print(f"   ✅ 获取到 {len(statuses)} 条微博")

                for j, status in enumerate(statuses, 1):
                    weibo_text = status.get('text', '')[:100]
                    created_at = status.get('created_at', '')
                    reposts_count = status.get('reposts_count', 0)
                    comments_count = status.get('comments_count', 0)
                    attitudes_count = status.get('attitudes_count', 0)

                    print(f"\n   📌 微博 {j}:")
                    print(f"   内容: {weibo_text}...")
                    print(f"   时间: {created_at}")
                    print(f"   互动: 转发{reposts_count} 评论{comments_count} 点赞{attitudes_count}")

                    followers_weibo.append({
                        'follower_name': follower_name,
                        'follower_uid': follower_uid,
                        'text': weibo_text,
                        'created_at': created_at,
                        'reposts_count': reposts_count,
                        'comments_count': comments_count,
                        'attitudes_count': attitudes_count
                    })
            else:
                print(f"   ⚠️ 该用户无微博或数据不可见")

        except Exception as e:
            print(f"   ❌ 获取失败: {e}")

    # 第三步：总结
    print("\n" + "=" * 60)
    print("📊 测试总结:")
    print("=" * 60)
    print(f"✅ 总粉丝数: {total_count}")
    print(f"✅ 成功获取粉丝微博: {len(followers_weibo)} 条")

    if len(followers_weibo) > 0:
        print(f"\n💡 建议:")
        print(f"   - 可以按时间顺序整理粉丝微博")
        print(f"   - 可以按互动数排序（转发/评论/点赞）")
        print(f"   - 可以过滤低质量内容（广告、刷屏等）")

except Exception as e:
    print(f"❌ 发生错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print(f"⏰ 测试完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
