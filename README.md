# 團訂機器人 (Group Order Bot)

一個基於 LINE Bot 的簡單團體訂餐系統，解決學校、辦公室團訂便當的基本痛點。

## 專案背景

在學校工讀時發現每次團訂便當都很麻煩：
- 需要挨個詢問同事要不要訂餐
- 手動統計人數和餐點
- 容易搞錯訂單或漏掉某些人

所以想做個簡單的自動化解決方案，當作 side project 練習。

## 核心功能 (MVP)

### 🍱 基礎團訂
- 發起團訂：群組成員發起團訂，選擇餐廳
- 私訊訂餐：避免群組洗版，私訊機器人選餐點
- 自動統計：即時統計人數、餐點數量、總金額
- 通知提醒：截止時間提醒、訂購結果通知

### 🏪 簡單餐廳管理
- 手動建立：預先建立常用餐廳和菜單
- 基本資訊：店名、電話、主要餐點和價格
- 快速選擇：從清單快速選擇餐廳

## 技術選擇 (免費優先)

### 主要技術
- Backend Python + Flask (熟悉的技術)
- Database SQLite (開發)  PostgreSQL (部署)
- LINE Bot LINE Messaging API (免費版)
- 部署 Railway  Render (免費額度)

### 系統架構
```
LINE Bot → Flask Webhook → SQLitePostgreSQL
```

## 快速開始

### 環境需求
- Python 3.8+
- LINE Developer Account (免費)

### 本地開發
```bash
# 克隆專案
git clone httpsgithub.comusernamesimple-group-order-bot.git
cd simple-group-order-bot

# 建立虛擬環境
python -m venv venv
source venvbinactivate  # Windows venvScriptsactivate

# 安裝依賴
pip install -r requirements.txt

# 環境變數設定
cp .env.example .env
# 編輯 .env 添加 LINE Bot 金鑰

# 初始化資料庫
python init_db.py

# 啟動開發服務器
python app.py
```

### 部署 (Railway)
1. 註冊 Railway 帳號
2. 連接 GitHub 專案
3. 設定環境變數
4. 自動部署完成

## 使用方法

### 設定步驟
1. 將機器人加入 LINE 群組
2. 管理員預先建立餐廳資料
3. 開始使用團訂功能

### 基本指令
- `start` - 開始使用
- `order` - 發起團訂
- `menu` - 查看餐廳列表
- `help` - 幫助資訊

### 使用流程
1. 任何人輸入 `order` 發起團訂
2. 選擇餐廳和設定截止時間
3. 群組成員私訊機器人選餐
4. 時間到後自動統計並通知

## 專案結構

```
simple-group-order-bot
├── app.py                 # 主程式
├── models.py             # 資料庫模型
├── line_handler.py       # LINE Bot 處理邏輯
├── utils.py              # 工具函數
├── init_db.py           # 資料庫初始化
├── requirements.txt      # 依賴套件
├── .env.example         # 環境變數範例
└── README.md
```

## 開發計劃

### Phase 1 - MVP (6-8週，兼職開發)
- [x] LINE Bot 基礎架構
- [x] 簡單的餐廳資料管理
- [x] 團訂發起和參與功能
- [x] 基本統計和通知
- [x] 本地測試和部署

### 未來可能新增 (如果有時間)
- 網頁後台管理餐廳資料
- 簡單的團購歷史記錄
- 更美觀的訊息格式
- 拍照上傳菜單 (需付費 OCR)

## 限制說明

### 技術限制
- LINE Bot 免費版每月 500 則訊息
- 沒有 OCR 功能，需手動建立菜單
- 沒有複雜的數據分析
- 沒有個人化推薦

### 使用限制
- 適合小型群組 (10-20人)
- 需要管理員預先建立餐廳資料
- 功能相對簡單但實用

## 學習筆記

這個專案主要是為了練習：
- Python Flask 開發
- LINE Bot API 使用
- 資料庫設計和操作
- 雲端部署經驗
- 產品思維和用戶體驗

## 成本控制

### 開發成本
- 完全免費：使用所有免費服務和額度

### 小規模運營成本
- RailwayRender $0月 (免費額度內)
- 資料庫 $0月 (內建 PostgreSQL)
- LINE Bot $0月 (免費額度內)



---

簡單但實用的團訂解決方案！ 🎉

這是個 side project，主要目的是學習和解決實際問題。如果你也遇到類似困擾，歡迎一起改進！
