#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取已关注用户的最新微博
功能：
1. 获取已关注用户的最新微博
2. 关键词筛选（科技、AI、智能体、大模型、机器人等）
3. 去重（避免重复推送）
4. 格式化输出
5. 推送到飞书群
"""

import requests
import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib
import re

# ==================== 配置区域 ====================

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 配置文件路径
CONFIG_FILE = os.path.join(SCRIPT_DIR, "weibo_config.json")
CACHE_FILE = os.path.join(SCRIPT_DIR, "data", "friends_weibo_cache.json")

# API 基础 URL
WEIBO_API_BASE = "https://api.weibo.com/2"

# 默认配置
DEFAULT_KEYWORDS = []  # 空列表表示不筛选，推送所有微博
DEFAULT_FETCH_COUNT = 100  # 一次请求的微博数量
DEFAULT_PAGE = 1  # 获取的页数
DEFAULT_PUSH_COUNT = 10  # 一次推送的微博数量

def load_config() -> Dict:
    """加载配置文件"""
    # 默认配置
    config = {
        "app_key": "",
        "app_secret": "",
        "access_token": "",
        "uid": "",
        "feishu_chat_id": "oc_6f7d6e06d8e51b399f03669a5c3849e6",
        "fetch_count": DEFAULT_FETCH_COUNT,
        "page": DEFAULT_PAGE,
        "push_count": DEFAULT_PUSH_COUNT,
        "keywords": DEFAULT_KEYWORDS
    }

    # 尝试从JSON文件加载
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                config.update(file_config)
                print(f"✅ 已从 {CONFIG_FILE} 加载配置")
        except Exception as e:
            print(f"⚠️ 加载配置文件失败: {e}")
    else:
        print(f"⚠️ 配置文件不存在: {CONFIG_FILE}")

    return config

# 加载配置
WEIBO_CONFIG = load_config()
FEISHU_CHAT_ID = WEIBO_CONFIG.get("feishu_chat_id", "oc_6f7d6e06d8e51b399f03669a5c3849e6")

# 从配置文件读取关键词、请求数量、页数和推送数量
KEYWORDS = WEIBO_CONFIG.get("keywords", DEFAULT_KEYWORDS)
FETCH_COUNT = WEIBO_CONFIG.get("fetch_count", DEFAULT_FETCH_COUNT)
PAGE = WEIBO_CONFIG.get("page", DEFAULT_PAGE)
PUSH_COUNT = WEIBO_CONFIG.get("push_count", DEFAULT_PUSH_COUNT)

# 检查是否启用关键词筛选
USE_KEYWORD_FILTER = len(KEYWORDS) > 0

if USE_KEYWORD_FILTER:
    print(f"✅ 启用关键词筛选，关键词数量: {len(KEYWORDS)}")
else:
    print("ℹ️ 未启用关键词筛选，将推送所有微博")

print(f"📄 将获取第 {PAGE} 页数据")

# ==================== 工具函数 ====================

def load_cache() -> Dict:
    """加载缓存数据"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ 加载缓存失败: {e}")
    return {"sent_weibo_ids": [], "last_fetch_time": None}

def save_cache(cache: Dict) -> None:
    """保存缓存数据"""
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ 保存缓存失败: {e}")

def is_keyword_in_text(text: str, keywords: List[str]) -> bool:
    """检查文本是否包含关键词"""
    if not text or not keywords:
        return False

    text_lower = text.lower()
    for keyword in keywords:
        if keyword.lower() in text_lower:
            return True
    return False

def get_matched_keywords(text: str, keywords: List[str]) -> List[str]:
    """获取匹配到的关键词"""
    if not text or not keywords:
        return []

    matched = []
    text_lower = text.lower()
    for keyword in keywords:
        if keyword.lower() in text_lower:
            matched.append(keyword)
    return matched

def format_weibo_text(text: str, max_length: int = 200) -> str:
    """格式化微博文本，去除多余的空格和换行"""
    if not text:
        return ""

    # 去除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)

    # 替换连续的空格和换行
    text = re.sub(r'\s+', ' ', text).strip()

    # 截断
    if len(text) > max_length:
        text = text[:max_length] + "..."

    return text

def parse_weibo_time(created_at: str) -> Dict[str, object]:
    """解析微博时间，返回时间戳与格式化展示时间"""
    if not created_at:
        return {"timestamp": 0, "display": ""}

    # 微博原始时间格式：Wed Mar 04 17:10:09 +0800 2026
    try:
        created_at_dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
        return {
            "timestamp": created_at_dt.timestamp(),
            "display": created_at_dt.strftime("%Y-%m-%d %H:%M:%S %z"),
        }
    except Exception:
        return {"timestamp": 0, "display": created_at}

def get_weibo_image_url(status: Dict) -> Optional[str]:
    """获取微博图片 URL"""
    if 'pic_urls' in status and status['pic_urls']:
        return status['pic_urls'][0]['thumbnail_pic']
    return None

# ==================== 微博 API 函数 ====================

def call_weibo_api(endpoint: str, params: Dict) -> Optional[Dict]:
    """调用微博 API"""
    url = f"{WEIBO_API_BASE}/{endpoint}.json"
    params['access_token'] = WEIBO_CONFIG['access_token']

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'error_code' in data:
            print(f"❌ API 错误: {data.get('error_code')} - {data.get('error')}")
            return None

        return data
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return None
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return None

def get_friends_timeline(count: int = 100, page: int = 1) -> List[Dict]:
    """获取已关注用户的最新微博（支持分页）"""
    print(f"📱 获取已关注用户的最新微博（第 {page} 页，每页 {count} 条）...")

    all_statuses = []

    # 循环获取多页数据
    for current_page in range(1, page + 1):
        params = {
            'count': count,
            'feature': 0,  # 0:全部, 1:原创, 2:图片, 3:视频
            'trim_user': 0,  # 返回完整用户信息
            'page': current_page
        }

        result = call_weibo_api('statuses/friends_timeline', params)

        if result and 'statuses' in result:
            statuses = result['statuses']
            print(f"   ✅ 第 {current_page} 页获取到 {len(statuses)} 条微博")
            all_statuses.extend(statuses)
        else:
            print(f"   ❌ 第 {current_page} 页获取失败")
            break

        # 如果获取到的微博数量为0，说明已经到最后一页
        if len(statuses) == 0:
            print(f"   ℹ️ 已到达最后一页")
            break

        # 添加延迟，避免频繁请求
        if current_page < page:
            time.sleep(1)

    print(f"✅ 总共获取到 {len(all_statuses)} 条微博")
    return all_statuses

# ==================== 核心逻辑 ====================

def fetch_and_filter_weibo() -> List[Dict]:
    """获取并筛选微博"""
    # 获取缓存
    cache = load_cache()
    sent_ids = set(cache.get('sent_weibo_ids', []))

    # 获取已关注用户的时间线（使用配置的请求数量和页数）
    statuses = get_friends_timeline(count=FETCH_COUNT, page=PAGE)

    if not statuses:
        print("❌ 未获取到微博数据")
        return []

    # 筛选相关微博
    relevant_weibos = []

    for status in statuses:
        # 跳过已推送的
        weibo_id = str(status.get('id', ''))
        if weibo_id in sent_ids:
            continue

        # 获取微博文本
        text = status.get('text', '')

        # 检查是否是转发
        if 'retweeted_status' in status:
            retweeted_text = status.get('retweeted_status', {}).get('text', '')
            text = f"{text}\n\n转发: {retweeted_text}"

        # 关键词筛选（如果启用了筛选）
        matched_keywords = []
        if USE_KEYWORD_FILTER:
            if not is_keyword_in_text(text, KEYWORDS):
                continue
            matched_keywords = get_matched_keywords(text, KEYWORDS)

        # 获取用户信息
        user = status.get('user', {})
        user_name = user.get('screen_name', '未知用户')
        user_avatar = user.get('profile_image_url', '')
        user_id = user.get('id', '')
        user_followers_count = user.get('followers_count', 0)

        # 获取微博图片
        image_url = get_weibo_image_url(status)

        # 获取创建时间
        created_at_raw = status.get('created_at', '')

        # 获取互动数据
        reposts_count = status.get('reposts_count', 0)
        comments_count = status.get('comments_count', 0)
        attitudes_count = status.get('attitudes_count', 0)

        # 获取微博链接
        weibo_url = f"https://weibo.com/{user_id}/{weibo_id}"

        # 解析时间戳（用于排序）与展示时间
        time_info = parse_weibo_time(created_at_raw)
        timestamp = time_info["timestamp"]
        created_at_display = time_info["display"]

        relevant_weibos.append({
            'id': weibo_id,
            'text': format_weibo_text(text),
            'raw_text': text,  # 保留原始文本
            'user_name': user_name,
            'user_id': user_id,
            'user_avatar': user_avatar,
            'user_followers_count': user_followers_count,
            'image_url': image_url,
            'created_at': created_at_display,
            'created_at_raw': created_at_raw,
            'reposts_count': reposts_count,
            'comments_count': comments_count,
            'attitudes_count': attitudes_count,
            'weibo_url': weibo_url,
            'total_interactions': reposts_count + comments_count + attitudes_count,
            'timestamp': timestamp,
            'matched_keywords': matched_keywords  # 匹配到的关键词
        })

        # 记录为已推送（避免重复）
        sent_ids.add(weibo_id)

    # 按时间倒序排序（最新的在前面）
    relevant_weibos.sort(key=lambda x: x['timestamp'], reverse=True)

    # 更新缓存
    cache['sent_weibo_ids'] = list(sent_ids)[:1000]  # 最多保留 1000 条
    cache['last_fetch_time'] = datetime.now().isoformat()
    save_cache(cache)

    if USE_KEYWORD_FILTER:
        print(f"✅ 筛选出 {len(relevant_weibos)} 条相关微博")
    else:
        print(f"✅ 获取到 {len(relevant_weibos)} 条微博")

    return relevant_weibos

def format_feishu_message(weibos: List[Dict]) -> str:
    """格式化飞书消息"""
    if not weibos:
        return "📊 已关注用户微博更新\n━━━━━━━━━━━━━━━━\n\n暂无相关内容"

    lines = [
        "📊 已关注用户微博更新",
        "━━━━━━━━━━━━━━━━",
        ""
    ]

    # 使用配置的推送数量
    # 如果 push_count <= 0，推送所有匹配到的微博
    # 如果 push_count > 0，推送指定数量的微博
    if PUSH_COUNT <= 0:
        push_count = len(weibos)
    else:
        push_count = min(len(weibos), PUSH_COUNT)

    for i, weibo in enumerate(weibos[:push_count], 1):
        # 1. 用户名称，发表时间，匹配到的关键词
        matched_keywords_str = ', '.join(weibo.get('matched_keywords', []))
        lines.append(f"【{i}】{weibo['user_name']} | {weibo['created_at']} | 匹配关键词: {matched_keywords_str}")

        # 2. 微博具体的内容
        lines.append(f"{weibo['text']}")

        # 3. 微博涉及到的图片地址
        image_url = weibo.get('image_url', '')
        if image_url:
            lines.append(f"图片: {image_url}")

        # 4. 微博的原地址
        lines.append(f"链接: {weibo['weibo_url']}")
        lines.append("")

    lines.append("━━━━━━━━━━━━━━━━")
    if USE_KEYWORD_FILTER:
        lines.append(f"📱 来源：微博已关注用户 | 筛选关键词：{len(KEYWORDS)}个")
    else:
        lines.append("📱 来源：微博已关注用户 | 无筛选")

    return "\n".join(lines)

def send_to_feishu(message: str) -> bool:
    """发送给当前用户"""
    print("📤 推送给用户...")

    try:
        # 直接输出消息内容（OpenClaw会自动发送到当前会话）
        print(f"\n{message}\n")
        print("✅ 消息已准备就绪")
        return True

    except Exception as e:
        print(f"❌ 推送失败: {e}")
        return False

# ==================== 主函数 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 已关注用户微博抓取器启动")
    print("=" * 60)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 检查配置
    if not WEIBO_CONFIG['access_token']:
        print("❌ 错误: access_token 未配置")
        print("请先在 weibo_config.json 中配置 access_token")
        return

    # 获取并筛选微博
    relevant_weibos = fetch_and_filter_weibo()

    # 格式化消息
    message = format_feishu_message(relevant_weibos)

    # 推送到飞书
    if relevant_weibos:
        send_to_feishu(message)
    else:
        print("ℹ️ 暂无相关内容，跳过推送")

    print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
