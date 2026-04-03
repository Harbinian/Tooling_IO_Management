# Codex Rectification Log

## Task
- Prompt: `00089_feat_notification_text_improvement.md`
- Scope: keeper notification text, transport notification text, preview text, and requirement/API documentation sync

## Root Cause
- Keeper and transport notifications both reused detailed text, which made mobile keeper messages too verbose.
- Transport notice formatting relied on freeform text shapes that were harder to scan and risked Markdown-style rendering issues across clients.
- The field extraction logic was too narrow for notification data, especially around required time, confirmed quantity, and location fallbacks.

## Rectification Actions
- Replaced keeper notification generation with a short SMS-style template that only carries the order number and action cue.
- Reworked keeper preview generation to emit the same short template directly.
- Rebuilt transport and WeChat copy text into the same structured multiline format with explicit labels and per-item detail lines.
- Expanded order/item value extraction fallbacks using `ORDER_COLUMNS` and `ITEM_COLUMNS` aligned keys.
- Synchronized `docs/API_SPEC.md` and `docs/PRD.md` to the new notification-text contract.

## Verification
- Static validation: `python -m py_compile backend/services/tool_io_service.py` passed.
- Manual review: keeper text is short-form; transport text is structured multiline; no Markdown table separators remain in the generated templates.
- Limitation: no live Feishu/WeChat delivery or end-to-end workflow verification was executed in this run.

## Residual Risk
- Runtime data completeness still depends on upstream order/item payloads carrying the expected assignee and location fields.
- Without live send verification, client-side rendering differences can only be reduced by template shape review, not fully proven here.
