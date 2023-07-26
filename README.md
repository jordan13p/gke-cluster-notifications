# GKE Cluster Notifications

## 專案說明

此專案為接收 GKE Cluster 的通知，運行在 Cloud Functions 上

GKE Notifications 會發送如下類型的集群通知：

- SecurityBulletinEvent：接收正在使用 Cluster 版本相關的安全公告
- UpgradeEvent：當正在更新，會發送通知
- UpgradeAvailableEvent：當有新版本發佈時通知，但較不及時 (無開啓，使用 RSS 通知替代)

Release Notes：

- 使用 RSS feed 來接收最新的升級版本資訊

Demo：

- SecurityBulletinEvent

    ![SecurityBulletinEvent](https://imgur.com/xQnWwVt.png)

- UpgradeEvent

    ![UpgradeEvent](https://imgur.com/nprRWND.png)

- Release Notes

    ![Release Notes](https://imgur.com/Mb7qCJD.png)

> 訊息標題皆可點擊跳轉至 GCP 公告

參考資料：

- <https://cloud.google.com/kubernetes-engine/docs/concepts/cluster-notifications>
- <https://cloud.google.com/kubernetes-engine/docs/release-notes-stable>

## 架構說明

### GKE Notification

![gke notifications](https://imgur.com/kjA2f9X.png)

1. GKE 發送 Cluster 的事件通知
2. Pub / Sub 會收到告警訊息，並觸發 Cloud Functions
3. Cloud Functions 使用 Python 接收告警訊息，並轉發到 Discord Webhook

### GKE Release Notes (RSS)

![gke release note](https://imgur.com/t0eJYFu.png)

1. 透過 [Make](https://www.make.com/en/integrations) 設定
2. RSS feed 接收 GKE release notes (Stable channel)
3. Text parser 工具轉換字串
4. 透過 Discord Bot 重送訊息

## 資料夾結構

- `main.py`：接收 Pub / Sub 訊息，呼叫 event modules
- `/event/*.py`：將接收資料整理，並傳送至 Discord Webhook
- `requirements.txt`：Python 會使用到的套件版本

```bash
├── README.md
├── event
│   ├── __init__.py
│   ├── security_bulletin_event.py
│   ├── upgrade_avaliable_event.py
│   └── upgrade_event.py
├── main.py
└── requirements.txt
```

## GKE Notifications 設定

### Discord Webhook

1. 編輯頻道 > 整合 > 查看 webhook > 新增 webhook
2. 取得 webhook url

詳細步驟可參考：

- <https://10mohi6.medium.com/super-easy-python-discord-notifications-api-and-webhook-9c2d85ffced9>

### Cloud Functions

- `gke_cluster_notifications()` 為運行的主函式
- `security_bulletin_event.send_message()` 會整理需要的資料，取得要傳送的訊息內容
- `upgrade_avaliable_event.send_message()` 取得 Cloud Logging URL，查看範圍為當下訊息往前一小時
- `upgrade_event.send_message()` 將訊息傳送至 Telegram，格式使用 Markdown

```python
# 以下為 Cloud Functions 主要運行的函式
# Triggered from a message on a Cloud Pub/Sub topic
def gke_cluster_notifications(event, context):
    if "SecurityBulletinEvent" in type_url:
        security_bulletin_event.send_message(event)

    elif "UpgradeAvailableEvent" in type_url:
        upgrade_avaliable_event.send_message(event)

    elif "UpgradeEvent" in type_url:
        upgrade_event.send_message(event)

    else:
        msg = f"Event is not exist, so it will be skipped."
        print(msg)
        return (f"Bad Request: {msg}", 400)
```

在有程式碼的目錄下，執行以下指令上傳

```bash
# Entry point 設定為程式要運行的函式名稱
# 地區設定為臺灣
# Trigger topic 為觸發的 Pub / Sub 名稱，會自動建立
# User ID 及 Token 使用環境變數帶入，也可改用 Secret Manager

$ gcloud functions deploy gke-cluster-notifications \
--docker-registry=artifact-registry \
--entry-point=gke_cluster_notifications \
--region=asia-east1 \
--runtime=python39 \
--trigger-topic=gke-cluster-notifications \
--set-env-vars='USER_ID=<YOUR_USER_ID>,TELEGRAM_TOKEN=<TELEGRAM_BOT_TOKEN>,DISCORD_WEBHOOK_URL=<DISCORD_WEBHOOK_URL>'
```

> 此處 Telegram 設定為測試訊息使用，待之後移除

### Pub / Sub

- Cloud Functions 建立時，會一併建立 Pub / Sub 主題，不需要另外建立
- 權限是否需要設定待測試

### GKE - Notifications

在現有集群上啟用集群通知：

1. 轉到 Cloud Console 中的 Google Kubernetes Engine 頁面
2. 點選要修改的 Cluster
3. 修改在 "自動化" 底下的 "通知"
4. 選擇上述步驟建立的 Pub / Sub

參考資料：

- <https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-notifications>


## RSS 設定
### Make

正在運作：

- GKE release notes (Stable channel)

設定：

1. 建立 Scenarios
2. 新增 RSS 的 trigger，URL 填以下位置：
    - Stable Channel：<https://cloud.google.com/feeds/gke-stable-channel-release-notes.xml>
3. 新增 Text parser 工具
    - HTML 填 RSS 給的 `Description`
    - 此工具會將 HTML 的內容轉換為字串
4. 新增 Discord，選擇 `Post a Message with Embedded Objects`
   - 須設定 Connection 指定訊息的 Channel

訊息內容：

- 參考以下 JSON 格式填入設定

```json
{
    "content": ":newspaper: | {{1.title}}",
    "embeds": [
        {
          "title": ":rotating_light: GKE new version release (No channel) !!",
          "url": "{{1.url}}",
          "description": "Click link to view release schedule :arrow_heading_up:",
          "color": 5222632,
          "fields": [
              {
                  "name": "Author",
                  "value": "{{1.author}}",
                  "inline": true
              },
              {
                  "name": "Timestamp",
                  "value": "{{1.dateUpdated}}",
                  "inline": true
              },
              {
                  "name": "Content",
                  "value": "{{2.text}}",  // 此處的值來自 Text parser 轉換後的內容
                  "inline": false
              }
          ]
        }
    ]   
}
```
