#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博内容抓取器
功能：
1. 获取关注用户的最新微博
2. 关键词筛选（科技、AI、智能体、大模型、机器人）
3. 去重（避免重复推送）
4. 格式化输出
"""

import requests
import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib

# ==================== 配置区域 ====================

# 获取脚本所在目录与项目根目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

# 配置文件路径
CONFIG_FILE = os.path.join(BASE_DIR, "weibo_config.json")
CACHE_FILE = os.path.join(BASE_DIR, "data", "weibo_cache.json")

# API 基础 URL
WEIBO_API_BASE = "https://api.weibo.com/2"

# 关键词配置
KEYWORDS = [
    '科技', 'AI', '智能体', '大模型', '机器人',
    '人工智能', 'GPT', 'Claude', 'LLM', 'ChatGPT',
    '机器学习', '深度学习', '神经网络', '自动驾驶',
    'agent', 'Agentic'
]

def load_config() -> Dict:
    """加载配置文件"""
    # 默认配置
    config = {
        "app_key": "",
        "app_secret": "",
        "access_token": "",
        "uid": ""
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
        print(f"💡 请从 weibo_config.example.json 复制并填写配置")

    return config

# 加载配置
WEIBO_CONFIG = load_config()

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

def is_keyword_in_text(text: str) -> bool:
    """检查文本是否包含关键词"""
    if not text:
        return False
    
    text_lower = text.lower()
    for keyword in KEYWORDS:
        if keyword.lower() in text_lower:
            return True
    return False

def format_weibo_text(text: str, max_length: int = 200) -> str:
    """格式化微博文本，去除多余的空格和换行"""
    if not text:
        return ""
    
    # 去除 HTML 标签
    import re
    text = re.sub(r'<[^>]+>', '', text)
    
    # 替换连续的空格和换行
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 截断
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text

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

def get_friends_list() -> List[Dict]:
    """获取关注列表"""
    print("📋 获取关注列表...")
    
    params = {
        'uid': WEIBO_CONFIG['uid'],
        'count': 200,  # 最多获取 200 个关注
        'cursor': 0
    }
    
    result = call_weibo_api('friendships/friends', params)
    
    if result and 'users' in result:
        friends = result['users']
        print(f"✅ 获取到 {len(friends)} 个关注用户")
        return friends
    
    return []

def get_user_timeline(uid: str, count: int = 20) -> List[Dict]:
    """获取用户最新微博"""
    params = {
        'uid': uid,
        'count': count,
        'feature': 0  # 0:全部, 1:原创, 2:图片, 3:视频
    }
    
    result = call_weibo_api('statuses/user_timeline', params)
    
    if result and 'statuses' in result:
        return result['statuses']
    
    return []

def get_home_timeline(count: int = 100) -> List[Dict]:
    """获取首页时间线（包含所有关注）"""
    print("📱 获取首页时间线...")
    
    params = {
        'count': count,
        'feature': 0,
        'trim_user': 0  # 返回完整用户信息
    }
    
    result = call_weibo_api('statuses/home_timeline', params)
    
    if result and 'statuses' in result:
        print(f"✅ 获取到 {len(result['statuses'])} 条微博")
        return result['statuses']
    
    return []

# ==================== 核心逻辑 ====================

def fetch_and_filter_weibo() -> List[Dict]:
    """获取并筛选微博"""
    # 获取缓存
    cache = load_cache()
    sent_ids = set(cache.get('sent_weibo_ids', []))
    
    # 获取首页时间线
    statuses = get_home_timeline(count=100)
    
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
        
        # 关键词筛选
        if not is_keyword_in_text(text):
            continue
        
        # 获取用户信息
        user = status.get('user', {})
        user_name = user.get('screen_name', '未知用户')
        user_avatar = user.get('profile_image_url', '')
        
        # 获取微博图片
        image_url = get_weibo_image_url(status)
        
        # 获取创建时间
        created_at = status.get('created_at', '')
        
        # 获取微博链接
        weibo_url = f"https://weibo.com/{user.get('id')}/{weibo_id}"
        
        relevant_weibos.append({
            'id': weibo_id,
            'text': format_weibo_text(text),
            'user_name': user_name,
            'user_id': user.get('id'),
            'user_avatar': user_avatar,
            'image_url': image_url,
            'created_at': created_at,
            'weibo_url': weibo_url
        })
        
        # 记录为已推送（避免重复）
        sent_ids.add(weibo_id)
    
    # 更新缓存
    cache['sent_weibo_ids'] = list(sent_ids)[:1000]  # 最多保留 1000 条
    cache['last_fetch_time'] = datetime.now().isoformat()
    save_cache(cache)
    
    print(f"✅ 筛选出 {len(relevant_weibos)} 条相关微博")
    
    return relevant_weibos

def format_output_message(weibos: List[Dict]) -> str:
    """格式化输出消息"""
    if not weibos:
        return "📊 今日微博内容更新\n━━━━━━━━━━━━━━━━\n\n暂无相关内容"
    
    lines = [
        "📊 今日微博内容更新",
        "━━━━━━━━━━━━━━━━",
        ""
    ]
    
    for i, weibo in enumerate(weibos, 1):
        lines.append(f"【{i}】{weibo['user_name']}")
        lines.append(f"📝 {weibo['text']}")
        if weibo['image_url']:
            lines.append(f"🖼️ {weibo['image_url']}")
        lines.append(f"⏰ {weibo['created_at']}")
        lines.append(f"🔗 {weibo['weibo_url']}")
        lines.append("")
    
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append(f"📱 来源：微博 | 筛选关键词：科技、AI、智能体、大模型、机器人")
    
    return "\n".join(lines)

def output_message(message: str) -> bool:
    """输出到标准输出"""
    print("📤 输出结果...")

    try:
        print(f"\n{message}\n")
        print("✅ 输出已准备就绪")
        return True
    except Exception as e:
        print(f"❌ 输出失败: {e}")
        return False

# ==================== 主函数 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 微博内容抓取器启动")
    print("=" * 60)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查配置
    if not WEIBO_CONFIG['access_token']:
        print("❌ 错误: access_token 未配置")
        print("请先在脚本中配置 WEIBO_CONFIG['access_token']")
        return
    
    # 获取并筛选微博
    relevant_weibos = fetch_and_filter_weibo()
    
    # 格式化消息
    message = format_output_message(relevant_weibos)
    
    # 输出结果
    if relevant_weibos:
        output_message(message)
    else:
        print("ℹ️ 今日无相关内容，跳过输出")
    
    print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
