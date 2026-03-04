# 微博已关注用户最新动态获取

## 📋 功能说明

获取已关注用户的最新微博，支持分页与关键词筛选，并结构化输出。

## 🎯 解决的痛点

1. **按时间倒序拉取“最新微博”**：一次性获取你关注的所有用户最新微博，并按时间倒序排列，避免被平台推荐流打乱节奏。
2. **弥补“最新微博”缺少标记的问题**：微博原生“最新微博”模块没有标记/筛选能力，信息量一大就容易错过高质量内容。
3. **避免重复查看**：通过缓存记录已看内容，避免同一条微博反复出现，提高阅读效率。

## ✅ 环境与依赖

- Python 3.8+
- 依赖库：`requests`

安装依赖：
```bash
pip3 install requests
```

## ⚙️ 配置说明

### 配置文件位置

`weibo_config.json`

### 配置选项

```json
{
  "app_key": "你的App Key",
  "app_secret": "你的App Secret",
  "access_token": "你的Access Token",
  "uid": "你的UID",
  "fetch_count": 100,
  "page": 1,
  "push_count": 10,
  "keywords": [
    "科技",
    "AI",
    "智能体",
    "大模型",
    "机器人"
  ]
}
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `fetch_count` | 一次请求获取的微博数量（1-100） | 100 |
| `page` | 获取的页数（1-N，实际效果取决于API限制） | 1 |
| `push_count` | 输出的微博数量上限 | 10 |
| `keywords` | 关键词列表，空数组表示不筛选 | [] |

### page 参数说明

- **page = 1**：只获取第1页（最新数据）
- **page = 2**：获取第1页和第2页的数据
- **page = N**：获取前N页的数据

**注意**：实际获取的数据量取决于微博API的限制和可用数据量。如果请求的页数超过可用页数，脚本会自动在最后一页停止。

### push_count 输出规则

- **push_count <= 0**：输出所有匹配到的微博
- **push_count > 0**：输出指定数量的微博（如 5、10、20）

### 关键词筛选

- **启用筛选**：在 `keywords` 中添加关键词，只推送包含关键词的微博
- **不筛选**：将 `keywords` 设置为空数组 `[]`，推送所有微博

#### 示例：只推送科技相关微博

```json
"keywords": [
  "科技",
  "AI",
  "智能体",
  "大模型",
  "机器人",
  "人工智能",
  "GPT",
  "Claude",
  "LLM",
  "ChatGPT"
]
```

#### 示例：推送所有微博（不筛选）

```json
"keywords": []
```

## 📊 输出规则

- **来源**：已关注用户的微博
- **排序**：按时间倒序
- **数量**：由 `push_count` 控制
- **去重**：基于缓存避免重复输出
- **缓存**：最多保留 1000 条已推送微博记录

## 🔧 手动运行

```bash
python3 friends_weibo_fetcher.py
```

## 🛠️ 自定义配置

### 修改关键词

编辑 `weibo_config.json` 中的 `keywords` 字段：

```json
"keywords": [
  "你想要的",
  "关键词",
  "添加到这里"
]
```

### 修改请求数量

编辑 `weibo_config.json` 中的 `fetch_count` 字段：

```json
"fetch_count": 200  // 一次请求200条微博
```

### 修改推送数量

编辑 `weibo_config.json` 中的 `push_count` 字段：

```json
"push_count": 20  // 一次推送20条
```

## 📊 缓存文件

位置：`data/friends_weibo_cache.json`

保存已推送的微博ID，避免重复推送。

### 清空缓存（模拟首次运行）

```bash
rm data/friends_weibo_cache.json
```

## 📝 日志查看

脚本默认输出到标准输出，必要时可自行重定向到日志文件进行排查。

## 🧪 测试

### 测试启用关键词筛选

```bash
rm data/friends_weibo_cache.json
python3 friends_weibo_fetcher.py
```

### 测试不筛选（推送所有微博）

1. 编辑 `weibo_config.json`：
   ```json
   "keywords": []
   ```
2. 清空缓存并运行：
   ```bash
   rm data/friends_weibo_cache.json
   python3 friends_weibo_fetcher.py
   ```

## ⚠️ 注意事项

1. **Access Token 有效期**：由微博开放平台策略决定，请以控制台为准
2. **API 限制**：微博有访问频率限制，不要过于频繁调用
3. **关键词匹配**：大小写不敏感
4. **fetch_count**：最大值 100，超过100会被API忽略
5. **短链说明**：正文可能包含 `m.weibo.cn` 短链，属于微博原文内容

## 📞 问题排查

如果运行异常：

1. 手动运行脚本，查看错误：
   ```bash
   python3 friends_weibo_fetcher.py
   ```

## 🎯 使用建议

### 场景1：推送所有科技相关微博（获取2页数据）
```json
{
  "fetch_count": 100,
  "page": 2,
  "push_count": 0,
  "keywords": ["科技", "AI", "智能体", "大模型", "机器人"]
}
```
✅ **结果**：获取第1页和第2页数据，推送所有匹配到的微博

### 场景2：关注所有关注用户的动态（不筛选）
```json
{
  "fetch_count": 50,
  "push_count": 0,
  "keywords": []
}
```
✅ **结果**：推送所有微博（不筛选）

### 场景3：只关注Apple相关内容（推送前5条）
```json
{
  "fetch_count": 100,
  "push_count": 5,
  "keywords": ["Apple", "Mac", "iPhone", "iOS", "iPad"]
}
```
✅ **结果**：只推送Apple相关微博，最多5条

---

**创建时间**：2026-03-04
**更新时间**：2026-03-04
