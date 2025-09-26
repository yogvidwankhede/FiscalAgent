let session_id = null;
const chatEl = document.getElementById('chat');
const msgInput = document.getElementById('message');
const historyDiv = document.getElementById('history');

document.getElementById('send').addEventListener('click', send);
msgInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') send(); });

function toggleDark() {
    document.body.classList.toggle("dark");
    document.querySelector(".dark-toggle").textContent = document.body.classList.contains("dark") ? "☀️" : "🌙";
}

function appendMessage(text, who = 'bot', image = null) {
    const div = document.createElement('div');
    div.className = 'message ' + (who === 'user' ? 'user' : 'bot');
    div.textContent = text;
    if (image) {
        const img = document.createElement('img');
        img.src = image;
        img.style.maxWidth = '100%';
        img.style.marginTop = '8px';
        img.style.borderRadius = '6px';
        div.appendChild(document.createElement('br'));
        div.appendChild(img);
    }
    chatEl.prepend(div);
    chatEl.scrollTop = chatEl.scrollHeight;
}

function updateHistory() {
    historyDiv.innerHTML = '';
    historyData.forEach(item => {
        const hItem = document.createElement('div');
        hItem.className = 'history-item';
        hItem.textContent = item.question;
        hItem.onclick = () => {
            appendMessage(item.question, 'user');
            appendMessage(item.answer, 'bot');
        };
        historyDiv.appendChild(hItem);
    });
}

let historyData = [];

async function send() {
    const text = msgInput.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    msgInput.value = '';

    // Temporary bot loading message
    appendMessage('FiscalBuddy-AI is thinking...', 'bot');

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, session_id })
        });

        const j = await res.json();
        session_id = j.session_id;

        // Remove loading message
        const loadingMsg = chatEl.querySelector('.bot');
        if (loadingMsg) loadingMsg.remove();

        appendMessage(j.reply, 'bot', j.image);

        historyData.unshift({ question: text, answer: j.reply });
        updateHistory();

    } catch (err) {
        console.error(err);
        appendMessage('Failed to fetch response', 'bot');
    }
}
