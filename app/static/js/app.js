/**
 * LawPilot AI — Single-Page Chat Controller
 * Refined layout matching the official legal tech design.
 */

let conversationHistory = [];
let isSending = false;
let currentSessionId = 'session_' + Math.random().toString(36).substring(2, 9) + '_' + Date.now();
let lastGeneratedDocReq = null;

document.addEventListener('DOMContentLoaded', () => {
    initChat();
    initSpeech();
    initFileUpload();
    initModals();
});

function initChat() {
    const sendBtn = document.getElementById('sendBtn');
    const chatInput = document.getElementById('chatInput');
    const resetBtn = document.getElementById('newChatBtn');
    const sidebarToggle = document.getElementById('sidebarToggleBtn');

    sendBtn.addEventListener('click', handleSend);

    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });

    // Auto-resize textarea
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });

    resetBtn.addEventListener('click', resetChat);

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('open');
        });
    }
}

function resetChat() {
    conversationHistory = [];
    document.getElementById('messagesStream').innerHTML = '';
    document.getElementById('welcomeScreen').style.display = 'flex';
    document.getElementById('chatInput').value = '';
    fetch('/api/session/reset?session_id=' + encodeURIComponent(currentSessionId), { method: 'POST' }).catch(() => {});
    currentSessionId = 'session_' + Math.random().toString(36).substring(2, 9) + '_' + Date.now();
}

function useExamplePrompt(text) {
    document.getElementById('chatInput').value = text;
    handleSend();
}

function loadPrompt(text) {
    document.getElementById('chatInput').value = text;
    handleSend();
}

async function handleSend() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message || isSending) return;

    // Hide welcome screen
    document.getElementById('welcomeScreen').style.display = 'none';

    // Format current time
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Append user message
    appendUserRow(message, timeStr);
    input.value = '';
    input.style.height = 'auto';
    conversationHistory.push({ role: 'user', content: message });

    // Show typing state
    isSending = true;
    const typingId = showTypingIndicator();

    const lang = document.getElementById('languageSelect') ? document.getElementById('languageSelect').value : 'en';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                conversation_history: conversationHistory,
                language: lang,
                session_id: currentSessionId
            })
        });

        const data = await response.json();
        removeTypingIndicator(typingId);
        isSending = false;

        appendAssistantRow(data.content, data.citations || []);
        conversationHistory.push({ role: 'assistant', content: data.content });

    } catch (err) {
        removeTypingIndicator(typingId);
        isSending = false;
        appendAssistantRow("⚠️ Connection issue: Unable to reach legal reasoning service. Please check your network.", []);
    }
}

function appendUserRow(text, timeStr) {
    const stream = document.getElementById('messagesStream');
    const row = document.createElement('div');
    row.className = 'user-row';
    row.innerHTML = `
        <div class="user-bubble">${escapeHtml(text)}</div>
        <div class="msg-timestamp">${timeStr}</div>
    `;
    stream.appendChild(row);
    scrollToBottom();
}

function appendAssistantRow(content, citations = []) {
    const stream = document.getElementById('messagesStream');
    const row = document.createElement('div');
    row.className = 'assistant-row';

    const formattedHtml = formatLegalMarkdown(content);
    const rowId = 'msg_' + Date.now();

    let sourcesHtml = '';
    if (citations && citations.length > 0) {
        let itemsHtml = citations.map(c => `
            <div class="source-link-item">
                <a href="${c.official_url}" target="_blank" rel="noopener noreferrer">
                    [${escapeHtml(c.act_name)} — ${escapeHtml(c.section)}]
                </a>: <em>${escapeHtml(c.title)}</em>
            </div>
        `).join('');

        sourcesHtml = `
            <button class="action-pill-btn" onclick="toggleSources('${rowId}_sources')">
                <span>🔗</span>
                <span>Sources (${citations.length}) ▾</span>
            </button>
            <div class="sources-container" id="${rowId}_sources">
                ${itemsHtml}
            </div>
        `;
    }

    row.innerHTML = `
        <div class="assistant-header">
            <div class="assistant-avatar">⚖️</div>
            <span class="assistant-name">LawPilot AI</span>
        </div>
        <div class="assistant-bubble">${formattedHtml}</div>
        <div class="assistant-actions-bar">
            <button class="action-pill-btn" onclick="copyAssistantText(this)">
                <span>📋</span>
                <span>Copy</span>
            </button>
            <button class="action-pill-btn" onclick="triggerDocumentDraft()">
                <span>📄</span>
                <span>Generate Document</span>
            </button>
            ${sourcesHtml}
        </div>
    `;

    stream.appendChild(row);
    scrollToBottom();
}

function toggleSources(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.classList.toggle('open');
    }
}

function copyAssistantText(btn) {
    const bubble = btn.closest('.assistant-row').querySelector('.assistant-bubble');
    if (bubble) {
        navigator.clipboard.writeText(bubble.innerText).then(() => {
            const originalText = btn.innerHTML;
            btn.innerHTML = '<span>✅</span><span>Copied!</span>';
            setTimeout(() => { btn.innerHTML = originalText; }, 2000);
        });
    }
}

// Format markdown according to the reference image design
function formatLegalMarkdown(text) {
    let html = escapeHtml(text);

    // Section headers: "### | Your Situation", "### | Your Legal Position", "### | Practical Next Steps"
    html = html.replace(/###\s*\|\s*([^\n]+)/g, '<div class="section-header-bar">$1</div>');
    html = html.replace(/###\s*([^\n]+)/g, '<div class="section-header-bar">$1</div>');

    // Callout box for Information I still need from you
    html = html.replace(/ℹ️\s*Information\s*I\s*still\s*need\s*from\s*you\s*([\s\S]*?)(?=(?:<div class="section-header-bar"|$))/gi, (match, body) => {
        return `
            <div class="info-callout-card">
                <div class="info-callout-title">
                    <span>ℹ️</span>
                    <span>Information I still need from you</span>
                </div>
                <div class="info-callout-body">${body.trim()}</div>
            </div>
        `;
    });

    // Bold text: **text**
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Numbered steps with circle badge (e.g., "1. Gather evidence")
    html = html.replace(/(?:^|\n)\s*(\d+)\.\s+([^\n]+)/g, (match, num, stepText) => {
        return `<div class="step-item"><span class="step-num">${num}</span><span>${stepText}</span></div>`;
    });

    // Bullet points: "* text" or "- text"
    html = html.replace(/(?:^|\n)\s*[\*\-]\s+([^\n]+)/g, '<li>$1</li>');
    html = html.replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>');
    html = html.replace(/<\/ul>\s*<ul>/g, ''); // combine consecutive uls

    // Paragraph breaks
    html = html.replace(/\n\n/g, '<p></p>');

    return html;
}

function showTypingIndicator() {
    const stream = document.getElementById('messagesStream');
    const id = 'typing_' + Date.now();
    const row = document.createElement('div');
    row.className = 'assistant-row';
    row.id = id;
    row.innerHTML = `
        <div class="assistant-header">
            <div class="assistant-avatar">⚖️</div>
            <span class="assistant-name">LawPilot AI</span>
        </div>
        <div class="typing-dots">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
    `;
    stream.appendChild(row);
    scrollToBottom();
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function scrollToBottom() {
    const viewport = document.getElementById('chatViewport');
    viewport.scrollTop = viewport.scrollHeight;
}

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/* --- Document Generator Modal --- */
async function triggerDocumentDraft() {
    // Generate draft legal notice based on current conversation
    try {
        const res = await fetch('/api/document/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                doc_type: "security_deposit_demand",
                user_name: "[Your Name]",
                counterparty_name: "[Counterparty Name]",
                facts: conversationHistory.map(m => m.content).join("\n"),
                disputed_amount: "₹25,000",
                demands: "Immediate refund within 15 days"
            })
        });

        const data = await res.json();
        lastGeneratedDocReq = {
            doc_type: "security_deposit_demand",
            user_name: "[Your Name]",
            counterparty_name: "[Counterparty Name]",
            facts: conversationHistory.map(m => m.content).join("\n"),
            disputed_amount: "₹25,000",
            demands: "Immediate refund within 15 days"
        };

        document.getElementById('modalDocTitle').innerText = data.title || "📄 Formal Legal Notice Draft";
        document.getElementById('modalDocContent').innerText = data.content_text;
        document.getElementById('docModal').style.display = 'flex';

    } catch (e) {
        alert("Unable to generate document draft at this moment.");
    }
}

function closeDocModal() {
    document.getElementById('docModal').style.display = 'none';
}

function initModals() {
    // Settings modal
    const settingsBtn = document.getElementById('settingsBtn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', () => {
            document.getElementById('settingsModal').style.display = 'flex';
        });
    }

    // About modal
    const aboutBtn = document.getElementById('aboutBtn');
    if (aboutBtn) {
        aboutBtn.addEventListener('click', () => {
            alert("LawPilot AI is an intelligent legal assistant for India, grounding everyday civil challenges (Tenancy, Consumer, Employment) in official India Code statutes.");
        });
    }

    // Modal download PDF
    const downloadPdf = document.getElementById('modalDownloadPdf');
    if (downloadPdf) {
        downloadPdf.addEventListener('click', async () => {
            if (!lastGeneratedDocReq) return;
            const res = await fetch('/api/document/download/pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(lastGeneratedDocReq)
            });
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'LawPilot_Notice.pdf';
            a.click();
        });
    }

    // Modal download DOCX
    const downloadDocx = document.getElementById('modalDownloadDocx');
    if (downloadDocx) {
        downloadDocx.addEventListener('click', async () => {
            if (!lastGeneratedDocReq) return;
            const res = await fetch('/api/document/download/docx', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(lastGeneratedDocReq)
            });
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'LawPilot_Notice.docx';
            a.click();
        });
    }

    // Modal copy text
    const copyBtn = document.getElementById('modalCopyBtn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const text = document.getElementById('modalDocContent').innerText;
            navigator.clipboard.writeText(text).then(() => {
                copyBtn.innerText = '✅ Copied!';
                setTimeout(() => { copyBtn.innerText = '📋 Copy Text'; }, 2000);
            });
        });
    }
}

/* --- File Upload Handling --- */
function initFileUpload() {
    const attachBtn = document.getElementById('attachBtn');
    const fileInput = document.getElementById('fileAttachment');

    if (attachBtn && fileInput) {
        attachBtn.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            try {
                const res = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                
                const input = document.getElementById('chatInput');
                input.value = `I have attached my ${data.document_type || 'document'} (${file.name}). Extracted facts: ${data.summary || 'Document details parsed'}. Please advise on my rights.`;
                input.style.height = 'auto';
                input.style.height = Math.min(input.scrollHeight, 120) + 'px';
                input.focus();
            } catch (err) {
                alert("File upload error: " + err.message);
            }
        });
    }
}

/* --- Web Speech API (Microphone) --- */
function initSpeech() {
    const voiceBtn = document.getElementById('voiceBtn');
    if (!voiceBtn) return;

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        voiceBtn.style.display = 'none';
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-IN';

    let isListening = false;

    voiceBtn.addEventListener('click', () => {
        if (!isListening) {
            recognition.start();
            voiceBtn.style.color = '#dc2626';
            isListening = true;
        } else {
            recognition.stop();
            voiceBtn.style.color = '';
            isListening = false;
        }
    });

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const input = document.getElementById('chatInput');
        input.value = input.value ? (input.value + ' ' + transcript) : transcript;
        input.focus();
        voiceBtn.style.color = '';
        isListening = false;
    };

    recognition.onerror = () => {
        voiceBtn.style.color = '';
        isListening = false;
    };

    recognition.onend = () => {
        voiceBtn.style.color = '';
        isListening = false;
    };
}
