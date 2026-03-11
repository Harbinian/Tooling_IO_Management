# -*- coding: utf-8 -*-
"""
Feishu API Module for Tooling IO Management
"""

import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class FeishuBase:
    """飞书 API 基础类"""

    def __init__(self):
        self.app_id = os.getenv("FEISHU_APP_ID")
        self.app_secret = os.getenv("FEISHU_APP_SECRET")
        self.app_token = os.getenv("FEISHU_APP_TOKEN")
        self.token = self.get_tenant_access_token(self.app_id, self.app_secret)
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json; charset=utf-8"
        } if self.token else {}

    def get_tenant_access_token(self, app_id, app_secret):
        """获取飞书访问令牌"""
        if not app_id or not app_secret:
            logger.warning("未配置飞书应用凭证")
            return None
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {"app_id": app_id, "app_secret": app_secret}
        try:
            res = requests.post(url, json=payload)
            if res.status_code == 200:
                return res.json().get("tenant_access_token")
        except Exception as e:
            logger.error(f"获取飞书 Token 失败: {e}")
        return None

    def send_webhook_message(self, webhook_url: str, message: str, msg_type: str = "text") -> bool:
        """
        发送 Webhook 消息到飞书群机器人
        """
        if not webhook_url:
            logger.warning("未配置飞书 Webhook URL")
            return False

        try:
            payload = {
                "msg_type": msg_type,
                "content": {}
            }

            if msg_type == "text":
                payload["content"]["text"] = message
            elif msg_type == "markdown":
                payload["content"]["markdown"] = {"content": message}

            response = requests.post(webhook_url, json=payload, headers={
                "Content-Type": "application/json; charset=utf-8"
            }, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    logger.info("飞书 Webhook 消息发送成功")
                    return True
                else:
                    logger.error(f"飞书 Webhook 发送失败: {result.get('msg')}")
                    return False
            else:
                logger.error(f"飞书 Webhook 请求失败: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"飞书 Webhook 发送异常: {e}")
            return False

    def send_transport_notification(self, order_no: str, transport_type: str,
                                   from_location: str, to_location: str,
                                   tools: list, contacts: dict) -> bool:
        """发送运输通知到飞书"""
        message = f"""【工装运输任务通知】

单号：{order_no}
运输类型：{transport_type}

工装列表：
"""
        for tool in tools:
            message += f"- {tool.get('code')} {tool.get('name')} ({from_location} → {to_location})\n"

        message += f"""
联系人：{contacts.get('initiator', '-')} / {contacts.get('keeper', '-')}
"""

        webhook_url = os.getenv("FEISHU_WEBHOOK_TRANSPORT", os.getenv("FEISHU_WEBHOOK_URL"))
        return self.send_webhook_message(webhook_url, message, "text")
