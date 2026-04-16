const BASE_URL = "http://192.168.1.150/v1";
const API_KEY = "app-rjhzHid326F2teOn2msQDhXS";
const ENDPOINT = `${BASE_URL}/workflows/run`;

const questionInput = document.getElementById("question");
const sendButton = document.getElementById("send");
const answerBox = document.getElementById("answer");

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

async function sendQuestion() {
  const query = questionInput.value.trim();
  if (!query) {
    answerBox.textContent = "请输入问题";
    return;
  }

  sendButton.disabled = true;
  answerBox.textContent = "请求中...";

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
    answerBox.textContent = typeof answer === "string" ? answer : JSON.stringify(answer, null, 2);
  } catch (error) {
    answerBox.textContent = `请求失败: ${error.message}`;
  } finally {
    sendButton.disabled = false;
  }
}

sendButton.addEventListener("click", sendQuestion);
questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    sendQuestion();
  }
});
