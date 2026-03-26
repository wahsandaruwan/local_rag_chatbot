document.addEventListener("DOMContentLoaded", () => {
    checkHealth();
    setupTextarea();
    // Periodically check health
    setInterval(checkHealth, 30000);
});

let isStreaming = false;

/* Check Ollama and knowledge base health */
async function checkHealth() {
    const ollamaStatus = document.getElementById("ollama-status");
    const dbStatus = document.getElementById("db-status");
    const ollamaDot = ollamaStatus.querySelector(".health-dot");
    const dbDot = dbStatus.querySelector(".health-dot");

    try {
        const res = await fetch("/api/chat/health");
        const data = await res.json();

        // Ollama status
        if (data.ollama.ollama_running && data.ollama.model_available) {
            ollamaDot.className = "health-dot online";
            ollamaStatus.querySelector("span:last-child").textContent =
                `Ollama (${data.ollama.model_name})`;
        } else if (data.ollama.ollama_running) {
            ollamaDot.className = "health-dot offline";
            ollamaStatus.querySelector("span:last-child").textContent =
                `Ollama (model not found)`;
        } else {
            ollamaDot.className = "health-dot offline";
            ollamaStatus.querySelector("span:last-child").textContent =
                "Ollama (offline)";
        }

        // Vector store status
        dbDot.className = "health-dot online";
        document.getElementById("kb-count").textContent =
            data.vector_store.total_documents;
    } catch {
        ollamaDot.className = "health-dot offline";
        dbDot.className = "health-dot offline";
    }
}

/* Configure textarea auto-resize and keyboard shortcuts */
function setupTextarea() {
    const textarea = document.getElementById("chat-input");

    // Auto-resize
    textarea.addEventListener("input", () => {
        textarea.style.height = "auto";
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
    });

    // Enter to send, Shift+Enter for new line
    textarea.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (!isStreaming) sendMessage(e);
        }
    });
}

/* Send a chat message */
async function sendMessage(e) {
    e.preventDefault();

    const input = document.getElementById("chat-input");
    const query = input.value.trim();
    if (!query || isStreaming) return;

    // Hide welcome message
    const welcome = document.getElementById("welcome-msg");
    if (welcome) welcome.remove();

    // Add user message
    addMessage(query, "user");
    input.value = "";
    input.style.height = "auto";

    // Disable input while streaming
    isStreaming = true;
    updateSendButton(true);

    // Add assistant message placeholder with typing indicator
    const assistantBubble = addMessage("", "assistant");
    assistantBubble.innerHTML = `
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    `;

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query }),
        });

        if (!res.ok) {
            const err = await res.json();
            assistantBubble.textContent = `⚠️ Error: ${err.detail}`;
            return;
        }

        // Read SSE stream
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let fullResponse = "";
        assistantBubble.innerHTML = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split("\n");

            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const data = line.slice(6).trim();
                    if (data === "[DONE]") continue;

                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.token) {
                            fullResponse += parsed.token;
                            assistantBubble.innerHTML = formatResponse(fullResponse);
                        }
                        if (parsed.error) {
                            assistantBubble.innerHTML += `<br>⚠️ ${parsed.error}`;
                        }
                    } catch {
                        // Skip malformed lines
                    }
                }
            }

            // Auto-scroll to bottom
            scrollToBottom();
        }
    } catch (err) {
        assistantBubble.textContent = "⚠️ Failed to connect to the server.";
    } finally {
        isStreaming = false;
        updateSendButton(false);
        scrollToBottom();
    }
}

/* Add a message bubble to the chat */
function addMessage(text, role) {
    const container = document.getElementById("chat-messages");
    const icon = role === "user" ? "person-fill" : "robot";

    const msg = document.createElement("div");
    msg.className = `message ${role}`;
    msg.innerHTML = `
        <div class="message-avatar">
            <i class="bi bi-${icon}"></i>
        </div>
        <div class="message-bubble">${formatResponse(text)}</div>
    `;

    container.appendChild(msg);
    scrollToBottom();
    return msg.querySelector(".message-bubble");
}

/* Format response text to basic HTML */
function formatResponse(text) {
    if (!text) return "";

    return text
        // Bold
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        // Italic
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        // Code blocks
        .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
        // Inline code
        .replace(/`(.*?)`/g, "<code>$1</code>")
        // Line breaks
        .replace(/\n/g, "<br>");
}

/* Scroll chat to the latest message */
function scrollToBottom() {
    const container = document.getElementById("chat-messages");
    container.scrollTop = container.scrollHeight;
}

/* Toggle send button state */
function updateSendButton(disabled) {
    const btn = document.getElementById("send-btn");
    btn.disabled = disabled;
    btn.innerHTML = disabled
        ? '<span class="spinner-border spinner-border-sm"></span>'
        : '<i class="bi bi-send-fill"></i>';
}
