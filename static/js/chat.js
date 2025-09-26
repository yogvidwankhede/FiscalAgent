let session_id = null;
const chatEl = document.getElementById('chat');
const msgInput = document.getElementById('message');
document.getElementById('send').addEventListener('click', send);
msgInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') send(); });

function appendMessage(text, who = 'bot', image = null) {
    const div = document.createElement('div');
    div.className = 'msg';
    const span = document.createElement('span');
    span.className = who === 'user' ? 'user' : 'bot';
    span.innerText = text;
    div.appendChild(span);
    if (image) {
        const img = document.createElement('img');
        img.src = image;
        img.className = 'plot';
        div.appendChild(document.createElement('br'));
        div.appendChild(img);
    }
    chatEl.appendChild(div);
    chatEl.scrollTop = chatEl.scrollHeight;
}

async function send() {
    const text = msgInput.value.trim();
    if (!text) return;
    appendMessage(text, 'user', null);
    msgInput.value = '';
    const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: session_id })
    });
    const j = await res.json();
    session_id = j.session_id;
    appendMessage(j.reply, 'bot', j.image);
}
