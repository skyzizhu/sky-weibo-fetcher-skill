#!/usr/bin/env python3
"""
获取粉丝列表及粉丝最新微博
"""
import requests
import json
from datetime import datetime
import re

# 从配置文件加载
with open('weibo_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

ACCESS_TOKEN = config['access_token']
UID = config['uid']

print("=" * 60)
print("🔍 获取粉丝列表及粉丝微博")
print("=" * 60)

# ==================== 获取粉丝列表 ====================

print(f"\n📋 正在获取用户 {UID} 的粉丝列表...")
followers_url = "https://api.weibo.com/2/friendships/followers.json"
params = {
    'access_token': ACCESS_TOKEN,
    'uid': UID,
    'count': 20,
    'cursor': 0
}

try:
    response = requests.get(followers_url, params=params, timeout=10)

    if response.status_code != 200:
        print(f"❌ API请求失败: 状态码 {response.status_code}")
        print(f"响应: {response.text}")
        exit(1)

    data = response.json()

    if 'error_code' in data:
        print(f"❌ API错误: {data.get('error', '未知错误')}")
        print(f"错误码: {data['error_code']}")
        exit(1)

    if 'users' not in data:
        print(f"❌ 响应中没有用户列表")
        print(f"响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
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
        description = follower.get('description', '')

        print(f"\n{i}. {screen_name}")
        print(f"   UID: {follower['id']}")
        print(f"   粉丝数: {followers_count} | 微博数: {statuses_count}")
        if description:
            print(f"   简介: {description}")

    # ==================== 获取粉丝微博 ====================

    print("\n" + "=" * 60)
    print("📝 获取粉丝最新微博（前5位，每人3条）:")
    print("=" * 60)

    all_weibo = []

    for i, follower in enumerate(followers[:5], 1):
        follower_uid = follower['id']
        follower_name = follower.get('screen_name', '未知')

        print(f"\n{i}. 正在获取 {follower_name} 的微博...")

        # 使用正确的API端点
        user_timeline_url = "https://api.weibo.com/2/statuses/user_timeline.json"
        params_timeline = {
            'access_token': ACCESS_TOKEN,
            'uid': follower_uid,
            'count': 3,
            'feature': 0
        }

        try:
            timeline_response = requests.get(user_timeline_url, params=params_timeline, timeout=10)

            if timeline_response.status_code != 200:
                print(f"   ❌ API请求失败: 状态码 {timeline_response.status_code}")
                continue

            timeline_data = timeline_response.json()

            if 'error_code' in timeline_data:
                error = timeline_data.get('error', '未知错误')
                error_code = timeline_data.get('error_code', '未知')
                print(f"   ❌ API错误: {error} ({error_code})")
                continue

            if 'statuses' not in timeline_data:
                print(f"   ⚠️ 响应中没有微博数据")
                continue

            statuses = timeline_data['statuses']

            if len(statuses) == 0:
                print(f"   ℹ️ 该用户无微博或数据不可见")
                continue

            print(f"   ✅ 获取到 {len(statuses)} 条微博")

            for j, status in enumerate(statuses, 1):
                weibo_text = status.get('text', '')
                created_at = status.get('created_at', '')
                reposts_count = status.get('reposts_count', 0)
                comments_count = status.get('comments_count', 0)
                attitudes_count = status.get('attitudes_count', 0)
                weibo_id = status.get('id', '')

                # 清理文本（去除HTML标签）
                weibo_text_clean = re.sub(r'<[^>]+>', '', weibo_text)

                # 获取微博链接
                weibo_url = f"https://weibo.com/{follower_uid}/{weibo_id}"

                print(f"\n   📌 微博 {j}:")
                print(f"   内容: {weibo_text_clean}")
                print(f"   时间: {created_at}")
                print(f"   互动: 转发{reposts_count} 评论{comments_count} 点赞{attitudes_count}")
                print(f"   链接: {weibo_url}")

                all_weibo.append({
                    'follower_name': follower_name,
                    'follower_uid': follower_uid,
                    'weibo_id': str(weibo_id),
                    'text': weibo_text_clean,
                    'created_at': created_at,
                    'reposts_count': reposts_count,
                    'comments_count': comments_count,
                    'attitudes_count': attitudes_count,
                    'weibo_url': weibo_url
                })

        except Exception as e:
            print(f"   ❌ 获取失败: {e}")
            import traceback
            traceback.print_exc()

    # ==================== 总结 ====================

    print("\n" + "=" * 60)
    print("📊 测试总结:")
    print("=" * 60)
    print(f"✅ 总粉丝数: {total_count}")
    print(f"✅ 成功获取粉丝微博: {len(all_weibo)} 条")

    if len(all_weibo) > 0:
        print(f"\n📈 数据质量:")

        # 计算互动数
        total_interactions = sum([w['reposts_count'] + w['comments_count'] + w['attitudes_count'] for w in all_weibo])
        avg_interactions = total_interactions / len(all_weibo)

        # 计算微博长度
        avg_length = sum([len(w['text']) for w in all_weibo]) / len(all_weibo)

        print(f"   - 平均互动数: {avg_interactions:.1f}")
        print(f"   - 平均微博长度: {avg_length:.0f} 字")

        # 按互动数排序
        sorted_weibo = sorted(all_weibo, key=lambda x: x['reposts_count'] + x['comments_count'] + x['attitudes_count'], reverse=True)

        print(f"\n🏆 最受欢迎的3条微博:")
        for i, weibo in enumerate(sorted_weibo[:3], 1):
            total = weibo['reposts_count'] + weibo['comments_count'] + weibo['attitudes_count']
            print(f"\n{i}. @{weibo['follower_name']}")
            print(f"   内容: {weibo['text'][:50]}...")
            print(f"   互动: 转发{weibo['reposts_count']} 评论{weibo['comments_count']} 点赞{weibo['attitudes_count']} (总计: {total})")
            print(f"   链接: {weibo['weibo_url']}")

        print(f"\n💡 建议:")
        print(f"   - 可以按时间顺序整理粉丝微博")
        print(f"   - 可以按互动数排序（转发/评论/点赞）")
        print(f"   - 可以设置互动数阈值，只推送优质内容（如 >10）")
        print(f"   - 可以过滤广告、刷屏等低质量内容")
        print(f"   - 可以按粉丝影响力排序（粉丝数、微博数）")

except Exception as e:
    print(f"❌ 发生错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print(f"⏰ 测试完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
