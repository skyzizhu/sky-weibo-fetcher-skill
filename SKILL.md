---
name: sky-weibo-fetcher-skill
description: |
  获取微博已关注用户的最新动态，支持分页与关键词智能筛选，并结构化输出。
triggers:
  - 获取关注微博
  - 关注人最新微博
  - 查询关注动态
  - 最新关注微博
  - 查看关注微博列表
  - 我的最新微博
  - 好友最新微博
  - 最新微博列表
  - 最新微博动态
---

# Weibo Fetcher

获取微博已关注用户的最新动态，支持分页和关键词智能筛选，结构化输出匹配内容。

## 功能特点

1. **分页获取** - 支持多页数据获取，突破单页限制
2. **关键词筛选** - 智能筛选科技、AI、智能体等主题内容
3. **缓存去重** - 基于历史缓存避免重复输出同一内容
4. **智能排序** - 按时间倒序，最新的在前
5. **图片支持** - 自动提取并显示图片链接
6. **结构化输出** - 用户、时间、关键词、内容、图片、链接

## 快速开始

### 1. 依赖与环境

- Python 3.8+
- 依赖库：`requests`

安装依赖：
```bash
pip3 install requests
```

### 2. 配置微博API

创建微博开放平台账号并获取API密钥：
- 访问 [微博开放平台](https://open.weibo.com)
- 注册/登录后创建应用
- 获取 App Key、App Secret
- 通过OAuth授权获取 Access Token

### 3. 获取微博UID

调用接口获取自己的微博UID：
```bash
curl "https://api.weibo.com/2/account/get_uid.json?access_token=YOUR_ACCESS_TOKEN"
```

### 4. 配置技能

复制示例配置并填入你的信息：
```bash
cp weibo_config.example.json weibo_config.json
```

编辑 `weibo_config.json`：
```json
{
  "app_key": "YOUR_APP_KEY",
  "app_secret": "YOUR_APP_SECRET",
  "access_token": "YOUR_ACCESS_TOKEN",
  "uid": "YOUR_UID",
  "fetch_count": 100,
  "page": 1,
  "push_count": 10,
  "keywords": ["科技", "AI", "智能体", "大模型", "机器人"]
}
```

### 5. 测试运行

```bash
python3 friends_weibo_fetcher.py
```

## 配置参数

脚本中所有权限与配置参数均从 `weibo_config.json` 读取。

### 基础参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `app_key` | 微博开放平台 App Key | 必填 |
| `app_secret` | 微博开放平台 App Secret | 必填 |
| `access_token` | OAuth 授权后的 Access Token | 必填 |
| `uid` | 微博用户ID | 必填 |

### 抓取参数

| 参数 | 说明 | 默认值 | 范围 |
|------|------|--------|------|
| `fetch_count` | 每页返回的记录条数 | 100 | 1-100 |
| `page` | 获取的页数 | 1 | 1-N |
| `push_count` | 输出的微博数量上限 | 10 | 0-N |

- **page 参数说明**：
  - `page = 1`：只获取第1页（最新数据）
  - `page = 2`：获取第1页 + 第2页的数据
  - `page = 3`：获取第1页 + 第2页 + 第3页的数据
  - `page = N`：获取第1页到第N页的数据

- **push_count 参数说明**：
  - `push_count <= 0`：输出所有匹配到的微博
  - `push_count > 0`：输出指定数量的微博

### 筛选参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `keywords` | 关键词列表，空数组表示不筛选 | [] |

## 使用方式

### 手动运行

```bash
python3 friends_weibo_fetcher.py
```

## 输出格式

每条微博包含4个部分：

### 1. 用户信息
```
【序号】用户名称 | 发表时间(YYYY-MM-DD HH:MM:SS +0800) | 匹配关键词: 关键词1, 关键词2
```

### 2. 微博内容
```
微博文本内容（已去除HTML标签）
```

### 3. 图片链接（如果有）
```
图片: https://wxX.sinaimg.cn/thumbnail/xxx.jpg
```

### 4. 微博链接
```
链接: https://weibo.com/uid/weibo_id
```

### 完整示例

```
【1】人民日报 | 2026-03-04 17:32:28 +0800 | 匹配关键词: 科技
【#创新决胜未来#】在深圳市南山区，上下楼就是上下游...
图片: http://wx1.sinaimg.cn/thumbnail/xxx.jpg
链接: https://weibo.com/2803301701/5272799166862679
```

## 缓存机制

- **缓存文件**：`data/friends_weibo_cache.json`
- **缓存内容**：已推送的微博ID列表
- **缓存容量**：最多保留 1000 条历史记录
- **自动管理**：自动清理旧记录，保持最新状态
- **清空缓存**：删除该文件后会自动重新生成

## 故障排查

### API返回错误

检查应用是否已开通 `statuses/friends_timeline` 等相关接口权限，并确认未超出调用频率或配额限制。

检查配置文件中的API密钥和Token是否正确。

### 未获取到数据

检查网络连接和API调用频率限制。

### 关键词不生效

确认关键词数组格式正确，检查关键词拼写。

### 分页参数无效

检查 `page` 参数值，确保是正整数。

### 日志排查

脚本默认输出到标准输出，必要时可自行重定向到日志文件进行排查。

## 注意事项

1. **API频率限制**：微博API有调用频率限制，建议不要过于频繁调用
2. **Token有效期**：Access Token有效期由微博开放平台策略决定，请以控制台为准
3. **数据完整性**：API返回的数据可能因网络或API限制而不完整
4. **图片链接**：部分微博可能没有图片链接
5. **编码问题**：微博内容可能包含特殊字符，已做HTML标签清理
6. **短链说明**：正文可能包含 `m.weibo.cn` 短链，属于微博原文内容

## 相关资源

- [微博开放平台](https://open.weibo.com)
- [微博API文档](https://open.weibo.com/wiki/API)
- [API测试工具](https://open.weibo.com/tools/console)

---

**版本**：v1.0.0  
**最后更新**：2026-03-04  
**维护者**：OpenClaw Assistant
