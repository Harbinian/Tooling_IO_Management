const fs = require("fs");
const fsp = require("fs/promises");
const path = require("path");
const { spawn } = require("child_process");
const Lark = require("@larksuiteoapi/node-sdk");

const SERVICE_ROOT = path.resolve(__dirname, "..");
const REPO_ROOT = path.resolve(SERVICE_ROOT, "..", "..");

loadDotEnv(path.join(SERVICE_ROOT, ".env"));

const config = loadConfig();
const sessionStore = new SessionStore(config.sessionStorePath);
const bridge = new FeishuClaudeBridge(config, sessionStore);

main().catch((error) => {
  log("fatal", error.stack || String(error));
  process.exitCode = 1;
});

async function main() {
  await sessionStore.initialize();

  const baseConfig = {
    appId: config.feishuAppId,
    appSecret: config.feishuAppSecret,
    loggerLevel: Lark.LoggerLevel.info,
  };

  const wsClient = new Lark.WSClient(baseConfig);
  const eventDispatcher = new Lark.EventDispatcher({}).register({
    "im.message.receive_v1": async (data) => {
      bridge.acceptEvent(data);
    },
  });

  bridge.attachClient(new Lark.Client(baseConfig));

  process.on("SIGINT", () => {
    log("info", "Received SIGINT, shutting down bridge.");
    process.exit(0);
  });

  process.on("SIGTERM", () => {
    log("info", "Received SIGTERM, shutting down bridge.");
    process.exit(0);
  });

  log(
    "info",
    `Starting Feishu long-connection bridge. workdir=${config.claudeWorkdir} defaultMode=${config.defaultExecutionMode}`
  );

  wsClient.start({ eventDispatcher });
}

function loadConfig() {
  const feishuAppId = requiredEnv("FEISHU_APP_ID");
  const feishuAppSecret = requiredEnv("FEISHU_APP_SECRET");
  const claudeWorkdir = resolvePath(
    process.env.CLAUDE_WORKDIR || REPO_ROOT,
    REPO_ROOT
  );
  const allowedWorkdirs = [claudeWorkdir];

  return {
    feishuAppId,
    feishuAppSecret,
    allowOpenIds: new Set(parseCsv(process.env.ALLOW_OPEN_IDS)),
    allowChatIds: new Set(parseCsv(process.env.ALLOW_CHAT_IDS)),
    commandPrefix: (process.env.COMMAND_PREFIX || "/cc").trim(),
    defaultExecutionMode: normalizeMode(
      process.env.DEFAULT_EXECUTION_MODE || "plan"
    ),
    sessionStorePath: resolvePath(
      process.env.SESSION_STORE_PATH || "./data/sessions.json",
      SERVICE_ROOT
    ),
    replyChunkSize: parseInteger(process.env.FEISHU_REPLY_CHUNK_SIZE, 1500),
    replyMaxChars: parseInteger(process.env.FEISHU_REPLY_MAX_CHARS, 12000),
    claudeBin: process.env.CLAUDE_BIN || "claude",
    claudeWorkdir,
    allowedWorkdirs,
    claudeSettingSources:
      process.env.CLAUDE_SETTING_SOURCES || "user,project,local",
    claudeModel: (process.env.CLAUDE_MODEL || "").trim(),
    claudeTimeoutMs: parseInteger(process.env.CLAUDE_TIMEOUT_MS, 1800000),
    claudeAllowedToolsPlan:
      (process.env.CLAUDE_ALLOWED_TOOLS_PLAN || "Read,Glob,Grep").trim(),
    claudeAllowedToolsApply:
      (
        process.env.CLAUDE_ALLOWED_TOOLS_APPLY ||
        "Read,Glob,Grep,Edit,Write"
      ).trim(),
    claudePermissionMode: (process.env.CLAUDE_PERMISSION_MODE || "").trim(),
    claudeAppendSystemPrompt: (
      process.env.CLAUDE_APPEND_SYSTEM_PROMPT || ""
    ).trim(),
  };
}

class FeishuClaudeBridge {
  constructor(config, sessionStore) {
    this.config = config;
    this.sessionStore = sessionStore;
    this.client = null;
    this.seenMessageIds = new Map();
    this.conversationQueues = new Map();
  }

  attachClient(client) {
    this.client = client;
  }

  acceptEvent(event) {
    setImmediate(() => {
      this.processEvent(event).catch((error) => {
        log("error", error.stack || String(error));
      });
    });
  }

  async processEvent(event) {
    const message = event && event.message ? event.message : {};
    const sender = event && event.sender ? event.sender : {};
    const senderId = sender.sender_id || {};
    const openId = senderId.open_id || "";
    const chatId = message.chat_id || "";
    const chatType = message.chat_type || "unknown";
    const messageId = message.message_id || event.event_id || "";
    const senderType = sender.sender_type || "user";

    if (!chatId || !messageId || senderType !== "user") {
      return;
    }

    if (this.isDuplicate(messageId)) {
      log("info", `Skip duplicate event: ${messageId}`);
      return;
    }

    if (!this.isSenderAllowed(openId, chatId)) {
      await this.safeReply(chatId, "当前账号未在远程开发白名单中。");
      return;
    }

    if (message.message_type !== "text") {
      await this.safeReply(chatId, "当前仅支持文本消息。发送 /help 查看用法。");
      return;
    }

    const rawText = parseTextMessage(message.content);
    if (!rawText) {
      return;
    }

    const parsed = parseIncomingCommand(
      rawText,
      chatType,
      this.config.commandPrefix,
      this.config.defaultExecutionMode
    );

    if (parsed.ignore) {
      return;
    }

    const conversationKey = `${chatId}:${openId || "anonymous"}`;
    await this.enqueue(conversationKey, async () => {
      await this.handleParsedCommand({
        parsed,
        chatId,
        chatType,
        openId,
        conversationKey,
      });
    });
  }

  async handleParsedCommand(context) {
    const { parsed, chatId, conversationKey } = context;

    if (parsed.action === "help") {
      await this.safeReply(chatId, buildHelpText(this.config.commandPrefix));
      return;
    }

    if (parsed.action === "status") {
      const session = await this.sessionStore.get(conversationKey);
      if (!session) {
        await this.safeReply(
          chatId,
          `当前会话: 无\n默认模式: ${this.config.defaultExecutionMode}\n工作目录: ${this.config.claudeWorkdir}`
        );
        return;
      }

      await this.safeReply(
        chatId,
        `当前会话: ${session.sessionId}\n最近模式: ${session.mode}\n工作目录: ${session.workdir}\n更新时间: ${session.updatedAt}`
      );
      return;
    }

    if (parsed.action === "reset") {
      await this.sessionStore.delete(conversationKey);
      await this.safeReply(chatId, "已清空当前聊天的 Claude 会话绑定。");
      return;
    }

    if (parsed.action === "prompt") {
      await this.runClaudeTask({
        chatId,
        conversationKey,
        prompt: parsed.prompt,
        mode: parsed.mode,
        forceNewSession: parsed.forceNewSession,
      });
      return;
    }
  }

  async runClaudeTask({ chatId, conversationKey, prompt, mode, forceNewSession }) {
    const existing = forceNewSession
      ? null
      : await this.sessionStore.get(conversationKey);

    const profile =
      mode === "apply"
        ? this.config.claudeAllowedToolsApply
        : this.config.claudeAllowedToolsPlan;

    await this.safeReply(
      chatId,
      `已接收任务。\n模式: ${mode}\n工作目录: ${this.config.claudeWorkdir}\n${
        existing ? `续接会话: ${existing.sessionId}` : "会话: 新建"
      }`
    );

    try {
      const startedAt = Date.now();
      const result = await runClaude({
        bin: this.config.claudeBin,
        workdir: this.config.claudeWorkdir,
        timeoutMs: this.config.claudeTimeoutMs,
        settingSources: this.config.claudeSettingSources,
        model: this.config.claudeModel,
        allowedTools: profile,
        permissionMode: this.config.claudePermissionMode,
        appendSystemPrompt: this.config.claudeAppendSystemPrompt,
        prompt,
        sessionId: existing ? existing.sessionId : "",
      });

      await this.sessionStore.set(conversationKey, {
        sessionId: result.sessionId || (existing ? existing.sessionId : ""),
        mode,
        workdir: this.config.claudeWorkdir,
        updatedAt: new Date().toISOString(),
        lastPrompt: shorten(prompt, 120),
      });

      const elapsedSeconds = Math.max(
        1,
        Math.round((Date.now() - startedAt) / 1000)
      );
      const resultText = result.text || "Claude 未返回文本结果。";
      const payload = [
        `任务完成`,
        `模式: ${mode}`,
        `会话: ${result.sessionId || (existing ? existing.sessionId : "未返回")}`,
        `耗时: ${elapsedSeconds}s`,
        "",
        truncate(resultText, this.config.replyMaxChars),
      ].join("\n");

      await this.safeReply(chatId, payload);
    } catch (error) {
      await this.safeReply(
        chatId,
        `任务失败\n模式: ${mode}\n原因: ${error.message || String(error)}`
      );
    }
  }

  isDuplicate(messageId) {
    const now = Date.now();
    const ttlMs = 10 * 60 * 1000;

    for (const [key, value] of this.seenMessageIds.entries()) {
      if (now - value > ttlMs) {
        this.seenMessageIds.delete(key);
      }
    }

    if (this.seenMessageIds.has(messageId)) {
      return true;
    }

    this.seenMessageIds.set(messageId, now);
    return false;
  }

  isSenderAllowed(openId, chatId) {
    const openIdRestricted = this.config.allowOpenIds.size > 0;
    const chatRestricted = this.config.allowChatIds.size > 0;

    if (openIdRestricted && !this.config.allowOpenIds.has(openId)) {
      return false;
    }

    if (chatRestricted && !this.config.allowChatIds.has(chatId)) {
      return false;
    }

    return true;
  }

  async enqueue(conversationKey, task) {
    const previous = this.conversationQueues.get(conversationKey) || Promise.resolve();
    const next = previous
      .catch(() => {})
      .then(task)
      .finally(() => {
        if (this.conversationQueues.get(conversationKey) === next) {
          this.conversationQueues.delete(conversationKey);
        }
      });

    this.conversationQueues.set(conversationKey, next);
    return next;
  }

  async safeReply(chatId, text) {
    if (!this.client) {
      throw new Error("Feishu client is not attached.");
    }

    const chunks = chunkText(text, this.config.replyChunkSize);
    for (let index = 0; index < chunks.length; index += 1) {
      const prefix = chunks.length > 1 ? `[${index + 1}/${chunks.length}]\n` : "";
      await this.client.im.v1.message.create({
        params: {
          receive_id_type: "chat_id",
        },
        data: {
          receive_id: chatId,
          msg_type: "text",
          content: JSON.stringify({ text: `${prefix}${chunks[index]}` }),
        },
      });
    }
  }
}

class SessionStore {
  constructor(filePath) {
    this.filePath = filePath;
    this.writeQueue = Promise.resolve();
  }

  async initialize() {
    await fsp.mkdir(path.dirname(this.filePath), { recursive: true });
    if (!fs.existsSync(this.filePath)) {
      await this.write({ conversations: {} });
    }
  }

  async get(conversationKey) {
    const data = await this.read();
    return data.conversations[conversationKey] || null;
  }

  async set(conversationKey, value) {
    await this.mutate((data) => {
      data.conversations[conversationKey] = value;
    });
  }

  async delete(conversationKey) {
    await this.mutate((data) => {
      delete data.conversations[conversationKey];
    });
  }

  async read() {
    const raw = await fsp.readFile(this.filePath, "utf8");
    return JSON.parse(raw);
  }

  async write(data) {
    await fsp.writeFile(this.filePath, `${JSON.stringify(data, null, 2)}\n`, "utf8");
  }

  async mutate(mutator) {
    this.writeQueue = this.writeQueue.then(async () => {
      const data = await this.read();
      await mutator(data);
      await this.write(data);
    });
    return this.writeQueue;
  }
}

async function runClaude(options) {
  ensureAllowedWorkdir(options.workdir, config.allowedWorkdirs);

  if (options.sessionId) {
    const args = ["--resume", options.sessionId, "-p", options.prompt, "--output-format", "json"];
    return executeClaude(args, options);
  }

  const args = ["-p", options.prompt, "--output-format", "json"];

  if (options.settingSources) {
    args.push("--setting-sources", options.settingSources);
  }

  if (options.model) {
    args.push("--model", options.model);
  }

  if (options.allowedTools) {
    args.push("--allowedTools", options.allowedTools);
  }

  if (options.permissionMode) {
    args.push("--permission-mode", options.permissionMode);
  }

  if (options.appendSystemPrompt) {
    args.push("--append-system-prompt", options.appendSystemPrompt);
  }

  log("info", `Running Claude CLI in ${options.workdir}`);

  return executeClaude(args, options);
}

function executeClaude(args, options) {
  if (options.sessionId && options.settingSources) {
    args.push("--setting-sources", options.settingSources);
  }

  if (options.sessionId && options.model) {
    args.push("--model", options.model);
  }

  if (options.sessionId && options.allowedTools) {
    args.push("--allowedTools", options.allowedTools);
  }

  if (options.sessionId && options.permissionMode) {
    args.push("--permission-mode", options.permissionMode);
  }

  if (options.sessionId && options.appendSystemPrompt) {
    args.push("--append-system-prompt", options.appendSystemPrompt);
  }

  return new Promise((resolve, reject) => {
    const child = spawn(options.bin, args, {
      cwd: options.workdir,
      stdio: ["ignore", "pipe", "pipe"],
      windowsHide: true,
    });

    let stdout = "";
    let stderr = "";
    let finished = false;

    const timer = setTimeout(() => {
      if (finished) {
        return;
      }
      child.kill("SIGTERM");
      reject(new Error(`Claude CLI timed out after ${options.timeoutMs} ms.`));
    }, options.timeoutMs);

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString("utf8");
    });

    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString("utf8");
    });

    child.on("error", (error) => {
      clearTimeout(timer);
      finished = true;
      reject(error);
    });

    child.on("close", (code) => {
      clearTimeout(timer);
      finished = true;

      if (code !== 0) {
        const detail = stderr.trim() || stdout.trim() || `exit code ${code}`;
        reject(new Error(`Claude CLI failed: ${detail}`));
        return;
      }

      try {
        const payload = JSON.parse(stdout);
        resolve({
          sessionId: payload.session_id || "",
          text: extractClaudeText(payload),
          raw: payload,
        });
      } catch (error) {
        reject(
          new Error(
            `Failed to parse Claude JSON output: ${error.message}\nRaw stdout:\n${stdout}`
          )
        );
      }
    });
  });
}

function extractClaudeText(payload) {
  if (typeof payload.result === "string" && payload.result.trim()) {
    return payload.result.trim();
  }

  if (Array.isArray(payload.messages)) {
    const assistantMessages = payload.messages.filter(
      (item) => item && item.role === "assistant"
    );
    const parts = [];
    for (const message of assistantMessages) {
      if (typeof message.content === "string") {
        parts.push(message.content);
        continue;
      }
      if (Array.isArray(message.content)) {
        for (const block of message.content) {
          if (block && typeof block.text === "string") {
            parts.push(block.text);
          }
        }
      }
    }
    if (parts.length > 0) {
      return parts.join("\n").trim();
    }
  }

  return "";
}

function parseIncomingCommand(text, chatType, commandPrefix, defaultMode) {
  let normalized = stripMentions(text).trim();
  if (!normalized) {
    return { ignore: true };
  }

  const isGroupChat = chatType !== "p2p";

  if (normalized.startsWith(commandPrefix)) {
    normalized = normalized.slice(commandPrefix.length).trim();
  } else if (isGroupChat && normalized.startsWith("/")) {
    // Keep built-in slash commands available in groups.
  } else if (isGroupChat) {
    return { ignore: true };
  }

  if (!normalized) {
    return { action: "help" };
  }

  const firstSpace = normalized.indexOf(" ");
  const command = (
    firstSpace === -1 ? normalized : normalized.slice(0, firstSpace)
  ).toLowerCase();
  const rest = (firstSpace === -1 ? "" : normalized.slice(firstSpace + 1)).trim();

  switch (command) {
    case "help":
    case "/help":
      return { action: "help" };
    case "status":
    case "/status":
      return { action: "status" };
    case "reset":
    case "/reset":
      return { action: "reset" };
    case "new":
    case "/new":
      return rest
        ? {
            action: "prompt",
            prompt: rest,
            mode: defaultMode,
            forceNewSession: true,
          }
        : { action: "reset" };
    case "plan":
    case "/plan":
      return rest
        ? {
            action: "prompt",
            prompt: rest,
            mode: "plan",
            forceNewSession: false,
          }
        : { action: "help" };
    case "apply":
    case "/apply":
      return rest
        ? {
            action: "prompt",
            prompt: rest,
            mode: "apply",
            forceNewSession: false,
          }
        : { action: "help" };
    default:
      return {
        action: "prompt",
        prompt: normalized,
        mode: defaultMode,
        forceNewSession: false,
      };
  }
}

function buildHelpText(commandPrefix) {
  return [
    "可用命令:",
    `${commandPrefix} <任务>  使用默认模式处理任务`,
    "/plan <任务>  只读分析，不修改代码",
    "/apply <任务>  使用 apply 工具配置执行任务",
    "/new <任务>  新开会话并立即执行任务",
    "/status  查看当前聊天绑定的 Claude 会话",
    "/reset  清空当前聊天绑定的 Claude 会话",
    "/help  查看帮助",
    "",
    "说明:",
    "1. 私聊里可直接发送任务文本。",
    `2. 群聊里请使用 ${commandPrefix} 前缀，避免误触发。`,
    "3. 是否允许改文件、跑命令，取决于本地 Claude CLI 的 allowedTools 配置。",
  ].join("\n");
}

function parseTextMessage(content) {
  try {
    const data = JSON.parse(content || "{}");
    return typeof data.text === "string" ? data.text.trim() : "";
  } catch (error) {
    return "";
  }
}

function stripMentions(text) {
  return text.replace(/<at\b[^>]*>.*?<\/at>/gi, "").trim();
}

function chunkText(text, chunkSize) {
  if (!text) {
    return [""];
  }

  const chunks = [];
  let current = text;
  while (current.length > chunkSize) {
    chunks.push(current.slice(0, chunkSize));
    current = current.slice(chunkSize);
  }
  chunks.push(current);
  return chunks;
}

function truncate(text, maxChars) {
  if (text.length <= maxChars) {
    return text;
  }
  return `${text.slice(0, maxChars)}\n\n[输出已截断，总长度超过 ${maxChars} 字符]`;
}

function shorten(text, maxChars) {
  return text.length <= maxChars ? text : `${text.slice(0, maxChars)}...`;
}

function requiredEnv(key) {
  const value = process.env[key];
  if (!value || !value.trim()) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
  return value.trim();
}

function parseCsv(value) {
  if (!value) {
    return [];
  }
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function parseInteger(value, fallback) {
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function normalizeMode(value) {
  return value === "apply" ? "apply" : "plan";
}

function resolvePath(target, baseDir) {
  if (!target) {
    return baseDir;
  }
  return path.isAbsolute(target) ? path.normalize(target) : path.resolve(baseDir, target);
}

function ensureAllowedWorkdir(workdir, allowedWorkdirs) {
  const normalized = path.resolve(workdir).toLowerCase();
  const allowed = allowedWorkdirs.some((root) =>
    normalized.startsWith(path.resolve(root).toLowerCase())
  );
  if (!allowed) {
    throw new Error(`Workdir is outside the allowed roots: ${workdir}`);
  }
}

function loadDotEnv(filePath) {
  if (!fs.existsSync(filePath)) {
    return;
  }
  const raw = fs.readFileSync(filePath, "utf8");
  for (const line of raw.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }
    const eqIndex = trimmed.indexOf("=");
    if (eqIndex === -1) {
      continue;
    }
    const key = trimmed.slice(0, eqIndex).trim();
    const value = trimmed.slice(eqIndex + 1).trim();
    if (!process.env[key]) {
      process.env[key] = stripWrappingQuotes(value);
    }
  }
}

function stripWrappingQuotes(value) {
  if (
    (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"))
  ) {
    return value.slice(1, -1);
  }
  return value;
}

function log(level, message) {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] [${level}] ${message}`);
}
