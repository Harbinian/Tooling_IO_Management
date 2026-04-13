# -*- coding: utf-8 -*-
"""
飞书长连接客户端 - 接收消息不需要公网地址
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lark_oapi.ws import Client as WsClient
from lark_oapi.event.dispatcher_handler import EventDispatcherHandlerBuilder
from lark_oapi.api.im.v1.model.p2_im_message_receive_v1 import P2ImMessageReceiveV1
from scripts.feishu_bridge.feishu_queue import MessageQueue
from scripts.feishu_bridge.parser import CommandParser


def create_websocket_client(app_id: str, app_secret: str) -> WsClient:
    """
    创建飞书长连接客户端

    Args:
        app_id: 飞书应用 ID
        app_secret: 飞书应用密钥

    Returns:
        WebSocket 客户端
    """
    queue = MessageQueue()

    def handle_message_receive(event: P2ImMessageReceiveV1) -> None:
        """
        处理接收到的消息

        Args:
            event: 消息事件
        """
        try:
            message = event.event.message
            if message is None:
                return

            content = message.content
            chat_id = message.chat_id
            open_id = message.sender.open_id if message.sender else ""
            message_id = message.message_id

            print(f"[WS] 收到消息: {content[:50] if content else '(empty)'}... (chat={chat_id})")

            # 检查是否是 /claude 指令
            if content and content.strip().lower().startswith("/claude"):
                feishu_info = {
                    "chat_id": chat_id or "",
                    "open_id": open_id or "",
                    "message_id": message_id or ""
                }
                queue.enqueue(content, feishu_info)
                print(f"[WS] /claude 指令已入队: {content[:50]}")

                # 回复用户确认已收到
                reply_text = f"已收到指令: {content[:30]}...，正在处理中..."
                _send_feishu_message(app_id, app_secret, chat_id, reply_text)
            else:
                # 非 /claude 指令，简单提示
                print(f"[WS] 非 /claude 指令，跳过: {content[:50]}")

        except Exception as e:
            print(f"[WS] 处理消息异常: {e}")

    def _send_feishu_message(app_id: str, app_secret: str, chat_id: str, content: str) -> bool:
        """发送飞书消息"""
        try:
            from lark_oapi.api.im.v1 import CreateMessageApi
            from lark_oapi import Client

            client = Client(app_id=app_id, app_secret=app_secret)

            result = client.im.v1.message.create(
                {"receive_id": chat_id, "msg_type": "text", "content": f'{{"text":"{content}"}}'}
            )

            return result.code() == 0
        except Exception as e:
            print(f"[WS] 发送消息失败: {e}")
            return False

    # 构建事件处理器
    event_handler = (
        EventDispatcherHandlerBuilder(
            encrypt_key="",  # 长连接模式不需要加密密钥
            verification_token=""
        )
        .register_p2_im_message_receive_v1(handle_message_receive)
        .build()
    )

    # 创建 WebSocket 客户端
    ws_client = WsClient(
        app_id=app_id,
        app_secret=app_secret,
        event_handler=event_handler
    )

    return ws_client


def main():
    """启动长连接客户端"""
    from config.settings import settings

    app_id = getattr(settings, 'FEISHU_APP_ID', None) or os.environ.get('FEISHU_APP_ID')
    app_secret = getattr(settings, 'FEISHU_APP_SECRET', None) or os.environ.get('FEISHU_APP_SECRET')

    if not app_id or not app_secret:
        print("错误: 请设置 FEISHU_APP_ID 和 FEISHU_APP_SECRET 环境变量或 config/settings.py 中的配置")
        print("在飞书开放平台 https://open.feishu.cn/app 获取这些凭证")
        sys.exit(1)

    print("=" * 60)
    print("飞书长连接客户端")
    print("=" * 60)
    print(f"App ID: {app_id[:10]}...")
    print("连接模式: WebSocket 长连接（无需公网地址）")
    print("=" * 60)
    print()

    ws_client = create_websocket_client(app_id, app_secret)

    print("正在连接飞书服务器...")
    print("连接成功后，你可以在飞书中发送 /claude 指令")
    print("按 Ctrl+C 停止")
    print()

    try:
        ws_client.start()
    except KeyboardInterrupt:
        print("\n正在停止...")


if __name__ == "__main__":
    main()
