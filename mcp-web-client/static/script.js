document.addEventListener("DOMContentLoaded", () => {
    const sendBtn = document.getElementById("sendBtn");
    const messageInput = document.getElementById("messageInput");
    const messagesDiv = document.getElementById("messages");

    sendBtn.addEventListener("click", () => {
        const message = messageInput.value.trim();
        if (!message) return;

        // 显示用户消息
        const userMsg = document.createElement("div");
        userMsg.className = "message user";
        userMsg.textContent = "You: " + message;
        messagesDiv.appendChild(userMsg);

        messageInput.value = "";

        // 发送消息到后端
        fetch("/send", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        }).then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let assistantMsg = document.createElement("div");
            assistantMsg.className = "message assistant";
            assistantMsg.textContent = "Assistant: ";
            messagesDiv.appendChild(assistantMsg);

            function read() {
                reader.read().then(({ done, value }) => {
                    if (done) return;
                    const chunk = decoder.decode(value);
                    const lines = chunk.split("\n");
                    lines.forEach(line => {
                        if (line.startsWith("data: ")) {
                            assistantMsg.textContent += line.replace("data: ", "");
                        }
                    });
                    read();
                });
            }

            read();
        }).catch(error => {
            console.error("Error:", error);
        });
    });
});
