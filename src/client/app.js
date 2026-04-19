const BASE_URL = "http://192.168.1.150/v1";
const API_KEY = "app-d1nktiKrJQpYpvIs0LhX4jNj";
const ENDPOINT = `${BASE_URL}/workflows/run`;

const questionInput = document.getElementById("question");
const sendButton = document.getElementById("send");
const clearButton = document.getElementById("clear");
const conversationBox = document.getElementById("conversation");
const emptyState = document.getElementById("empty-state");
const turnCount = document.getElementById("turn-count");
const history = [];

function formatTime(date = new Date()) {
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

function syncConversationState() {
  const turnTotal = history.filter((item) => item.role === "user").length;

  emptyState.hidden = history.length > 0;
  conversationBox.dataset.hasMessages = history.length > 0 ? "true" : "false";
  turnCount.textContent = `${turnTotal} 轮`;
  clearButton.disabled = sendButton.disabled || history.length === 0;
}

function scrollConversationToBottom(behavior = "auto") {
  const top = conversationBox.scrollHeight;

  if (typeof conversationBox.scrollTo === "function") {
    conversationBox.scrollTo({ top, behavior });
    return;
  }

  conversationBox.scrollTop = top;
}

function createMessageElement({ role, content, state = "done", time, isoTime }) {
  const message = document.createElement("article");
  const avatar = document.createElement("div");
  const bubble = document.createElement("div");
  const meta = document.createElement("div");
  const name = document.createElement("span");
  const timestamp = document.createElement("time");
  const text = document.createElement("p");
  const cursor = document.createElement("span");

  message.className = `message message--${role}`;
  message.dataset.state = state;

  avatar.className = "message__avatar";
  avatar.textContent = role === "user" ? "你" : "AI";

  bubble.className = "message__bubble";
  meta.className = "message__meta";
  name.className = "message__name";
  name.textContent = role === "user" ? "你" : "AI 助手";

  timestamp.className = "message__time";
  timestamp.dateTime = isoTime;
  timestamp.textContent = time;

  text.className = "message__text";
  text.textContent = content;

  cursor.className = "message__cursor";
  cursor.setAttribute("aria-hidden", "true");

  meta.append(name, timestamp);
  bubble.append(meta, text, cursor);
  message.append(avatar, bubble);

  return message;
}

function appendMessage(role, content, state = "done") {
  const now = new Date();
  const item = {
    role,
    content,
    state,
    time: formatTime(now),
    isoTime: now.toISOString()
  };
  const element = createMessageElement(item);

  history.push(item);
  conversationBox.appendChild(element);
  syncConversationState();
  scrollConversationToBottom("smooth");

  return { item, element };
}

function updateMessage(entry, content, state = "done") {
  entry.item.content = content;
  entry.item.state = state;
  entry.element.dataset.state = state;
  entry.element.querySelector(".message__text").textContent = content;
  scrollConversationToBottom("auto");
}

function setBusyState(isBusy) {
  sendButton.disabled = isBusy;
  clearButton.disabled = isBusy || history.length === 0;
  questionInput.readOnly = isBusy;
  questionInput.setAttribute("aria-busy", String(isBusy));
  document.body.dataset.busy = isBusy ? "true" : "false";
}

function clearConversation() {
  history.length = 0;
  conversationBox.querySelectorAll(".message").forEach((node) => node.remove());
  syncConversationState();
  setBusyState(false);
  questionInput.focus();
}

function cleanExtractedText(text) {
  if (!text || typeof text !== "string") {
    return "";
  }

  // 匹配并移除所有 UUID + 可选的 true/false
  const uuidPattern = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(true|false)?/gi;
  let cleaned = text.replace(uuidPattern, "");

  // 提取【答复】后面的内容
  if (cleaned.includes("【答复】")) {
    cleaned = cleaned.split("【答复】").pop();
  }

  // 清理多余的空格
  cleaned = cleaned.replace(/\s+/g, " ").trim();

  return cleaned;
}

function readPath(source, path) {
  return path.reduce(
    (current, key) => (current && typeof current === "object" ? current[key] : undefined),
    source
  );
}

function extractAnswer(data) {
  // 尝试从常见路径提取答案文本
  const candidatePaths = [
    ["data", "outputs", "text"],
    ["outputs", "text"],
    ["data", "outputs", "answer"],
    ["outputs", "answer"],
    ["data", "text"],
    ["text"],
    ["data", "answer"],
    ["answer"],
    ["data", "output"],
    ["output"],
    ["result"]
  ];

  for (const path of candidatePaths) {
    const value = readPath(data, path);
    if (typeof value === "string" && value.length > 0) {
      return cleanExtractedText(value);
    }
  }

  // 检查 outputs 对象
  const outputs = readPath(data, ["data", "outputs"]) ?? readPath(data, ["outputs"]);
  if (outputs && typeof outputs === "object") {
    for (const key of Object.keys(outputs)) {
      const value = outputs[key];
      if (typeof value === "string" && value.length > 0) {
        return cleanExtractedText(value);
      }
    }
  }

  return "未获取到有效回复";
}

async function sendQuestion() {
  const query = questionInput.value.trim();
  if (!query) {
    questionInput.focus();
    return;
  }

  appendMessage("user", query);
  questionInput.value = "";
  setBusyState(true);

  const assistantMessage = appendMessage("assistant", "思考中...", "loading");

  try {
    const response = await fetch(ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${API_KEY}`
      },
      body: JSON.stringify({
        inputs: { query },
        response_mode: "blocking",
        user: "web-user-001"
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    const answer = extractAnswer(data);
    updateMessage(assistantMessage, answer, "done");
  } catch (error) {
    updateMessage(assistantMessage, `请求失败: ${error.message}`, "error");
  } finally {
    setBusyState(false);
    questionInput.focus();
  }
}

sendButton.addEventListener("click", sendQuestion);
clearButton.addEventListener("click", clearConversation);

questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    sendQuestion();
  }
});

syncConversationState();
setBusyState(false);
