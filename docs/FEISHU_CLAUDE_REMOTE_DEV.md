# Feishu Claude Remote Development

## Purpose

This addendum describes a low-friction remote development path for local machines that do not have a public IP address. The bridge uses Feishu long-connection event delivery so the workstation only needs outbound internet access.

## Runtime Layout

- Feishu self-built app bot receives `im.message.receive_v1` by long connection
- A local Node.js bridge service runs under `scripts/feishu_claude_bridge/`
- The bridge launches local `claude -p` commands inside the repository working directory
- Claude responses are pushed back to the same Feishu chat
- Session IDs are persisted locally so the same chat can continue the same Claude session

## Security Boundary

- Only users in `ALLOW_OPEN_IDS` can drive the bridge when the allowlist is configured
- `ALLOW_CHAT_IDS` can further restrict which chats are allowed
- Claude runs only inside the configured `CLAUDE_WORKDIR`
- Group chats require a command prefix to avoid accidental execution
- Tool permissions are controlled by `CLAUDE_ALLOWED_TOOLS_PLAN` and `CLAUDE_ALLOWED_TOOLS_APPLY`

## Supported Commands

- `/<prefix> <task>` or direct message text: run with the default mode
- `/plan <task>`: read-only analysis profile
- `/apply <task>`: apply profile for code changes
- `/new <task>`: start a fresh Claude session for the current chat
- `/status`: show the current bound Claude session
- `/reset`: clear the current bound Claude session
- `/help`: show bridge help

## Operational Notes

- Feishu long connection is suitable for environments without a public IP, but event handlers still need to return quickly. The bridge therefore acknowledges tasks immediately and processes Claude work asynchronously.
- Long-connection delivery is cluster-random rather than broadcast. If you run multiple copies of the bridge for the same Feishu app, only one instance will receive a given event.
- The bridge is intentionally isolated from the Flask request path. It can be deployed and iterated independently from `web_server.py`.

## Deployment Steps

1. Create a Feishu self-built app and enable bot capability.
2. Subscribe to the message receive event and switch event delivery to long connection mode.
3. Grant the app the permissions needed to receive messages and send messages.
4. Install Claude CLI on the workstation and make sure `claude auth login` is already completed.
5. In `scripts/feishu_claude_bridge/`, copy `.env.example` to `.env` and fill in the app credentials, allowed users, and Claude tool policy.
6. Run `npm install` and then `npm start` in `scripts/feishu_claude_bridge/`.

## Repository Files

- `scripts/feishu_claude_bridge/src/index.js`
- `scripts/feishu_claude_bridge/package.json`
- `scripts/feishu_claude_bridge/.env.example`

## Future Integration Points

- Replace CLI subprocess execution with the Claude Agent SDK if stronger workflow control is needed
- Add structured approval workflow for destructive shell actions
- Add organization-level audit persistence if this bridge becomes a shared team service
