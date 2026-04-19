const BASE_URL = "http://192.168.1.150/v1";
const API_KEY = "app-eXeHTibIYo0PnVXGjbYZ7U7v";
const ENDPOINT = `${BASE_URL}/workflows/run`;

const questionInput = document.getElementById("question");
const sendButton = document.getElementById("send");
const clearButton = document.getElementById("clear");
const conversationBox = document.getElementById("conversation");
const emptyState = document.getElementById("empty-state");
const turnCount = document.getElementById("turn-count");
const history = [];

function pickAnswer(data) {
  return (
    data?.data?.outputs?.text ||
    data?.answer ||
    data?.output ||
    data?.result ||
    data?.message ||
    JSON.stringify(data, null, 2)
  );
}

function formatTime(date = new Date()) {
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

function syncConversationState() {
  emptyState.hidden = history.length > 0;
  turnCount.textContent = `${history.filter((item) => item.role === "user").length} 轮`;
}

function scrollConversationToBottom() {
  conversationBox.scrollTop = conversationBox.scrollHeight;
}

function createMessageElement({ role, content, state = "done", time }) {
  const message = document.createElement("article");
  const avatar = document.createElement("div");
  const bubble = document.createElement("div");
  const meta = document.createElement("div");
  const name = document.createElement("span");
  const timestamp = document.createElement("time");
  const text = document.createElement("p");

  message.className = `message message--${role}`;
  message.dataset.state = state;

  avatar.className = "message__avatar";
  avatar.textContent = role === "user" ? "你" : "AI";

  bubble.className = "message__bubble";
  meta.className = "message__meta";
  name.className = "message__name";
  name.textContent = role === "user" ? "你" : "AI 助手";

  timestamp.className = "message__time";
  timestamp.dateTime = new Date().toISOString();
  timestamp.textContent = time;

  text.className = "message__text";
  text.textContent = content;

  meta.append(name, timestamp);
  bubble.append(meta, text);
  message.append(avatar, bubble);

  return message;
}

function appendMessage(role, content, state = "done") {
  const item = {
    role,
    content,
    state,
    time: formatTime()
  };
  const element = createMessageElement(item);

  history.push(item);
  conversationBox.appendChild(element);
  syncConversationState();
  scrollConversationToBottom();

  return { item, element };
}

function updateMessage(entry, content, state = "done") {
  entry.item.content = content;
  entry.item.state = state;
  entry.element.dataset.state = state;
  entry.element.querySelector(".message__text").textContent = content;
  scrollConversationToBottom();
}

function setBusyState(isBusy) {
  sendButton.disabled = isBusy;
  clearButton.disabled = isBusy || history.length === 0;
  questionInput.disabled = isBusy;
}

function clearConversation() {
  history.length = 0;
  conversationBox.querySelectorAll(".message").forEach((node) => node.remove());
  syncConversationState();
  setBusyState(false);
  questionInput.focus();
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

  const assistantMessage = appendMessage("assistant", "正在思考...", "loading");

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
    const answer = pickAnswer(data);
    updateMessage(
      assistantMessage,
      typeof answer === "string" ? answer : JSON.stringify(answer, null, 2)
    );
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
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendQuestion();
  }
});

syncConversationState();
setBusyState(false);
