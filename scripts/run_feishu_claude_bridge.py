from __future__ import annotations

import logging
from pathlib import Path

from backend.services.feishu_claude_bridge import FeishuClaudeBridgeService


def configure_logging() -> None:
    log_dir = Path(__file__).resolve().parents[1] / "logs" / "feishu_claude_bridge"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "bridge.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )


def main() -> None:
    configure_logging()
    service = FeishuClaudeBridgeService()
    service.start()


if __name__ == "__main__":
    main()
