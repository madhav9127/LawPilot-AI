/**
 * LawPilot AI — Single-Page Chat Controller & State Manager
 * Comprehensive client-side state management, instant switching (<10ms),
 * optimistic UI updates, conversational isolation, and resilient retry handling.
 */

// --- Constants & Storage Keys ---
const STORAGE_KEY = 'lawpilot_conversations';
const ACTIVE_CONV_KEY = 'lawpilot_active_conv_id';

// --- State Variables ---
let conversations = [];
let activeConversationId = null;
let isSending = false;
let lastGeneratedDocReq = null;

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    initState();
    initChatUI();
    initSpeech();
    initFileUpload();
    initModals();
    initLanguageSelector();
});

/* ==========================================================================
   STATE MANAGEMENT MODULE
   ========================================================================== */

function initState() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
            conversations = JSON.parse(saved);
        }
    } catch (e) {
        console.warn("Failed to load conversations from localStorage:", e);
        conversations = [];
    }

    if (!Array.isArray(conversations) || conversations.length === 0) {
        // Seed default initial empty conversation
        const initialConv = createNewConversationObject("New Consultation");
        conversations = [initialConv];
        activeConversationId = initialConv.id;
        saveConversations();
    } else {
        const savedActiveId = localStorage.getItem(ACTIVE_CONV_KEY);
        const exists = conversations.some(c => c.id === savedActiveId);
        activeConversationId = exists ? savedActiveId : conversations[0].id;
    }

    renderSidebar();
    renderActiveConversation();
}

function createNewConversationObject(title = "New Consultation") {
    return {
        id: 'conv_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7),
        title: title,
        createdAt: Date.now(),
        updatedAt: Date.now(),
        messages: []
    };
}

function saveConversations() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
        if (activeConversationId) {
            localStorage.setItem(ACTIVE_CONV_KEY, activeConversationId);
        }
    } catch (e) {
        console.warn("Failed to save conversations to localStorage:", e);
    }
}

function getActiveConversation() {
    return conversations.find(c => c.id === activeConversationId) || null;
}

function renderSidebar() {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;

    historyList.innerHTML = '';

    if (conversations.length === 0) {
        historyList.innerHTML = '<div class="empty-history-hint">No saved consultations yet.</div>';
        return;
    }

    // Sort conversations: most recently updated first
    const sorted = [...conversations].sort((a, b) => (b.updatedAt || b.createdAt) - (a.updatedAt || a.createdAt));

    sorted.forEach(conv => {
        const item = document.createElement('div');
        item.className = 'history-item' + (conv.id === activeConversationId ? ' active' : '');
        item.setAttribute('data-conv-id', conv.id);

        item.innerHTML = `
            <span class="history-icon">💬</span>
            <span class="history-text" title="${escapeHtml(conv.title)}">${escapeHtml(conv.title)}</span>
            <button class="history-delete-btn" title="Delete conversation" onclick="handleDeleteConv('${conv.id}', event)">✕</button>
        `;

        item.addEventListener('click', (e) => {
            // Prevent switching if delete button clicked
            if (e.target.closest('.history-delete-btn')) return;
            selectConversation(conv.id);
        });

        historyList.appendChild(item);
    });
}

function selectConversation(convId) {
    if (convId === activeConversationId) return;

    activeConversationId = convId;
    saveConversations();

    // Fast-path visual switch (< 5ms): Update sidebar active classes
    const historyItems = document.querySelectorAll('.history-item');
    historyItems.forEach(item => {
        if (item.getAttribute('data-conv-id') === convId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Render conversation messages without triggering any LLM calls
    renderActiveConversation();
}

function renderActiveConversation() {
    const stream = document.getElementById('messagesStream');
    const welcome = document.getElementById('welcomeScreen');
    if (!stream || !welcome) return;

    stream.innerHTML = '';

    const conv = getActiveConversation();
    if (!conv || !conv.messages || conv.messages.length === 0) {
        welcome.style.display = 'flex';
        return;
    }

    welcome.style.display = 'none';

    conv.messages.forEach(msg => {
        if (msg.role === 'user') {
            appendUserRowToDOM(msg.content, msg.timestamp || '', msg.id);
        } else if (msg.role === 'assistant') {
            appendAssistantRowToDOM(msg.content, msg.citations || [], msg.id);
        }
    });

    scrollToBottom();
}

function newChat() {
    const newConv = createNewConversationObject("New Consultation");
    conversations.unshift(newConv);
    activeConversationId = newConv.id;
    saveConversations();

    renderSidebar();
    renderActiveConversation();

    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.value = '';
        chatInput.focus();
    }
}

function handleDeleteConv(convId, event) {
    if (event) event.stopPropagation();

    const idx = conversations.findIndex(c => c.id === convId);
    if (idx === -1) return;

    conversations.splice(idx, 1);

    if (conversations.length === 0) {
        const fresh = createNewConversationObject("New Consultation");
        conversations = [fresh];
        activeConversationId = fresh.id;
    } else if (activeConversationId === convId) {
        activeConversationId = conversations[0].id;
    }

    saveConversations();
    renderSidebar();
    renderActiveConversation();
}

/* ==========================================================================
   CHAT UI & INPUT CONTROLLER
   ========================================================================== */

function initChatUI() {
    const sendBtn = document.getElementById('sendBtn');
    const chatInput = document.getElementById('chatInput');
    const resetBtn = document.getElementById('newChatBtn');
    const sidebarToggle = document.getElementById('sidebarToggleBtn');

    if (sendBtn) {
        sendBtn.addEventListener('click', handleSend);
    }

    if (chatInput) {
        // Send on Enter (unless Shift+Enter)
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
            }
        });

        // Auto-resize and update send button disabled state
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
            updateSendButtonState();
        });

        // Initialize button state
        updateSendButtonState();
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', newChat);
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            const sidebar = document.getElementById('sidebar');
            if (sidebar) sidebar.classList.toggle('open');
        });
    }
}

function updateSendButtonState() {
    const sendBtn = document.getElementById('sendBtn');
    const chatInput = document.getElementById('chatInput');
    if (!sendBtn || !chatInput) return;

    const hasText = chatInput.value.trim().length > 0;
    sendBtn.disabled = !hasText || isSending;
}

function useExamplePrompt(text) {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.value = text;
        updateSendButtonState();
        handleSend();
    }
}

function loadPrompt(text) {
    useExamplePrompt(text);
}

/* ==========================================================================
   MESSAGE DISPATCHER & OPTIMISTIC UI
   ========================================================================== */

async function handleSend() {
    const input = document.getElementById('chatInput');
    if (!input) return;

    const message = input.value.trim();
    if (!message || isSending) return;

    let conv = getActiveConversation();
    if (!conv) {
        conv = createNewConversationObject();
        conversations.unshift(conv);
        activeConversationId = conv.id;
    }

    // Auto-generate title from the first message
    if (conv.messages.length === 0) {
        conv.title = message.length > 36 ? message.substring(0, 34).trim() + '...' : message.trim();
    }

    // Hide welcome screen
    const welcome = document.getElementById('welcomeScreen');
    if (welcome) welcome.style.display = 'none';

    // Format timestamp
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Create user message object
    const userMsgId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substring(2, 6);
    const userMsg = {
        id: userMsgId,
        role: 'user',
        content: message,
        timestamp: timeStr,
        status: 'sent'
    };

    // Optimistically update conversation state & DOM
    conv.messages.push(userMsg);
    conv.updatedAt = Date.now();
    saveConversations();
    renderSidebar();

    appendUserRowToDOM(message, timeStr, userMsgId);

    // Clear input field and update button state
    input.value = '';
    input.style.height = 'auto';
    isSending = true;
    updateSendButtonState();

    // Show assistant typing indicator
    const typingId = showTypingIndicator();

    // Determine target language
    const langSelect = document.getElementById('languageSelect');
    const lang = langSelect ? langSelect.value : 'en';

    // Pass strictly active conversation history to isolate context
    const historyPayload = conv.messages.slice(0, -1).map(m => ({
        role: m.role,
        content: m.content
    }));

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                conversation_history: historyPayload,
                language: lang,
                session_id: conv.id
            })
        });

        if (!response.ok) {
            throw new Error(`Server returned HTTP ${response.status}`);
        }

        const data = await response.json();
        removeTypingIndicator(typingId);
        isSending = false;
        updateSendButtonState();

        // Save assistant message to conversation state
        const assistantMsg = {
            id: 'msg_' + Date.now() + '_' + Math.random().toString(36).substring(2, 6),
            role: 'assistant',
            content: data.content,
            citations: data.citations || [],
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            status: 'sent'
        };

        conv.messages.push(assistantMsg);
        conv.updatedAt = Date.now();
        saveConversations();

        // Render assistant row if the user is still on this conversation
        if (activeConversationId === conv.id) {
            appendAssistantRowToDOM(data.content, data.citations || [], assistantMsg.id);
        }

    } catch (err) {
        console.error("Chat request failed:", err);
        removeTypingIndicator(typingId);
        isSending = false;
        updateSendButtonState();

        // Render error card with Retry option
        if (activeConversationId === conv.id) {
            appendErrorRowToDOM(userMsgId, message);
        }
    }
}

async function retryMessage(userMsgId) {
    const conv = getActiveConversation();
    if (!conv) return;

    // Find message
    const msg = conv.messages.find(m => m.id === userMsgId);
    if (!msg) return;

    // Remove error card from DOM
    const errCard = document.getElementById('err_' + userMsgId);
    if (errCard) errCard.remove();

    if (isSending) return;
    isSending = true;
    updateSendButtonState();

    const typingId = showTypingIndicator();
    const langSelect = document.getElementById('languageSelect');
    const lang = langSelect ? langSelect.value : 'en';

    const historyPayload = conv.messages
        .filter(m => m.id !== userMsgId && m.status === 'sent')
        .map(m => ({ role: m.role, content: m.content }));

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: msg.content,
                conversation_history: historyPayload,
                language: lang,
                session_id: conv.id
            })
        });

        if (!response.ok) {
            throw new Error(`Server returned HTTP ${response.status}`);
        }

        const data = await response.json();
        removeTypingIndicator(typingId);
        isSending = false;
        updateSendButtonState();

        const assistantMsg = {
            id: 'msg_' + Date.now() + '_' + Math.random().toString(36).substring(2, 6),
            role: 'assistant',
            content: data.content,
            citations: data.citations || [],
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            status: 'sent'
        };

        conv.messages.push(assistantMsg);
        conv.updatedAt = Date.now();
        saveConversations();

        if (activeConversationId === conv.id) {
            appendAssistantRowToDOM(data.content, data.citations || [], assistantMsg.id);
        }

    } catch (err) {
        removeTypingIndicator(typingId);
        isSending = false;
        updateSendButtonState();
        appendErrorRowToDOM(userMsgId, msg.content);
    }
}

/* ==========================================================================
   DOM RENDERING HELPERS
   ========================================================================== */

function appendUserRowToDOM(text, timeStr, msgId = '') {
    const stream = document.getElementById('messagesStream');
    if (!stream) return;

    const row = document.createElement('div');
    row.className = 'user-row';
    if (msgId) row.id = 'row_' + msgId;

    row.innerHTML = `
        <div class="user-bubble">${escapeHtml(text)}</div>
        <div class="msg-timestamp">${escapeHtml(timeStr)}</div>
    `;
    stream.appendChild(row);
    scrollToBottom();
}

function appendAssistantRowToDOM(content, citations = [], msgId = '') {
    const stream = document.getElementById('messagesStream');
    if (!stream) return;

    const row = document.createElement('div');
    row.className = 'assistant-row';
    if (msgId) row.id = 'row_' + msgId;

    const formattedHtml = formatLegalMarkdown(content);
    const rowId = msgId || ('msg_' + Date.now());

    let sourcesHtml = '';
    if (citations && citations.length > 0) {
        const itemsHtml = citations.map(c => `
            <div class="source-link-item">
                <a href="${escapeHtml(c.official_url)}" target="_blank" rel="noopener noreferrer">
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

function appendErrorRowToDOM(userMsgId, originalText) {
    const stream = document.getElementById('messagesStream');
    if (!stream) return;

    const row = document.createElement('div');
    row.className = 'assistant-row';
    row.id = 'err_' + userMsgId;

    row.innerHTML = `
        <div class="assistant-header">
            <div class="assistant-avatar">⚖️</div>
            <span class="assistant-name">LawPilot AI</span>
        </div>
        <div class="msg-error-card">
            <span>⚠️ Could not reach LawPilot legal reasoning engine. Your message was preserved.</span>
            <button class="retry-btn" onclick="retryMessage('${userMsgId}')">Retry ↺</button>
        </div>
    `;

    stream.appendChild(row);
    scrollToBottom();
}

function showTypingIndicator() {
    const stream = document.getElementById('messagesStream');
    if (!stream) return null;

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
    if (!id) return;
    const el = document.getElementById(id);
    if (el) el.remove();
}

function scrollToBottom() {
    const viewport = document.getElementById('chatViewport');
    if (viewport) {
        viewport.scrollTop = viewport.scrollHeight;
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/* ==========================================================================
   LEGAL MARKDOWN FORMATTER (English, Hindi, Hinglish, Malayalam)
   ========================================================================== */

function formatLegalMarkdown(text) {
    let html = escapeHtml(text);

    // Section headers: "### | Your Situation", "### | आपकी स्थिति", etc.
    html = html.replace(/###\s*\|\s*([^\n]+)/g, '<div class="section-header-bar">$1</div>');
    html = html.replace(/###\s*([^\n]+)/g, '<div class="section-header-bar">$1</div>');

    // Callout box for Information I still need from you (supports multilingual headings)
    html = html.replace(/(?:ℹ️\s*)?(?:Information\s*I\s*still\s*need\s*from\s*you|आपसे\s*आवश्यक\s*जानकारी|Zaroori\s*Jankari|ആവശ്യമായ\s*വിവരങ്ങൾ)\s*([\s\S]*?)(?=(?:<div class="section-header-bar"|$))/gi, (match, body) => {
        return `
            <div class="info-callout-card">
                <div class="info-callout-title">
                    <span>ℹ️</span>
                    <span>Information I still need from you / आवश्यक जानकारी</span>
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

/* ==========================================================================
   DOCUMENT GENERATOR & MODAL CONTROLLER
   ========================================================================== */

async function triggerDocumentDraft() {
    const conv = getActiveConversation();
    const facts = conv ? conv.messages.map(m => m.content).join("\n") : "";

    try {
        const res = await fetch('/api/document/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                doc_type: "security_deposit_demand",
                user_name: "[Your Name]",
                counterparty_name: "[Counterparty Name]",
                facts: facts,
                disputed_amount: "₹25,000",
                demands: "Immediate refund within 15 days"
            })
        });

        const data = await res.json();
        lastGeneratedDocReq = {
            doc_type: "security_deposit_demand",
            user_name: "[Your Name]",
            counterparty_name: "[Counterparty Name]",
            facts: facts,
            disputed_amount: "₹25,000",
            demands: "Immediate refund within 15 days"
        };

        const modalDocTitle = document.getElementById('modalDocTitle');
        const modalDocContent = document.getElementById('modalDocContent');
        const docModal = document.getElementById('docModal');

        if (modalDocTitle) modalDocTitle.innerText = data.title || "📄 Formal Legal Notice Draft";
        if (modalDocContent) modalDocContent.innerText = data.content_text;
        if (docModal) docModal.style.display = 'flex';

    } catch (e) {
        alert("Unable to generate document draft at this moment.");
    }
}

function closeDocModal() {
    const docModal = document.getElementById('docModal');
    if (docModal) docModal.style.display = 'none';
}

function initModals() {
    const settingsBtn = document.getElementById('settingsBtn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', () => {
            const settingsModal = document.getElementById('settingsModal');
            if (settingsModal) settingsModal.style.display = 'flex';
        });
    }

    const aboutBtn = document.getElementById('aboutBtn');
    if (aboutBtn) {
        aboutBtn.addEventListener('click', () => {
            alert("LawPilot AI is an intelligent legal assistant for India, grounding civil disputes (Tenancy, Consumer, Employment) in official Indian statutes.");
        });
    }

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

/* ==========================================================================
   FILE UPLOAD HANDLER
   ========================================================================== */

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
                if (input) {
                    input.value = `I have attached my ${data.document_type || 'document'} (${file.name}). Extracted facts: ${data.summary || 'Document details parsed'}. Please advise on my rights.`;
                    input.style.height = 'auto';
                    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
                    input.focus();
                    updateSendButtonState();
                }
            } catch (err) {
                alert("File upload error: " + err.message);
            }
        });
    }
}

/* ==========================================================================
   LANGUAGE SELECTOR CONTROLLER
   ========================================================================== */

function initLanguageSelector() {
    const langSelect = document.getElementById('languageSelect');
    const chatInput = document.getElementById('chatInput');
    const toast = document.getElementById('langSwitchToast');

    if (!langSelect) return;

    langSelect.addEventListener('change', () => {
        const val = langSelect.value;
        let toastMsg = "";

        if (val === 'hi') {
            if (chatInput) chatInput.placeholder = "अपनी कानूनी समस्या यहाँ लिखें (जैसे: मकान मालिक डिपॉज़िट नहीं दे रहा)...";
            toastMsg = "🇮🇳 भाषा: हिंदी (Hindi) — LawPilot AI हिंदी में उत्तर देगा";
        } else if (val === 'hinglish') {
            if (chatInput) chatInput.placeholder = "Apni legal problem yahan likhein (e.g. landlord deposit nahi de raha)...";
            toastMsg = "🇮🇳 Language: Hinglish — LawPilot AI Hinglish me reply karega";
        } else {
            if (chatInput) chatInput.placeholder = "Describe your legal problem in plain English...";
            toastMsg = "🌐 Language: English — LawPilot AI will respond in English";
        }

        if (toast) {
            toast.innerText = toastMsg;
            toast.style.display = 'flex';
            setTimeout(() => {
                if (toast) toast.style.display = 'none';
            }, 3000);
        }
    });
}

/* ==========================================================================
   CHATGPT VOICE MODE (Inside-The-Bar Visualizer)
   ========================================================================== */

function initSpeech() {
    const voiceBtn = document.getElementById('voiceBtn');
    const chatInput = document.getElementById('chatInput');
    const attachBtn = document.getElementById('attachBtn');
    const voiceTrack = document.getElementById('chatgptVoiceTrack');
    const stopBtn = document.getElementById('chatgptStopBtn');
    const sendBtn = document.getElementById('sendBtn');
    const waveformBars = document.getElementById('waveformBars');
    const errorToast = document.getElementById('voiceErrorToast');

    if (!voiceBtn || !chatInput || !voiceTrack || !stopBtn) return;

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        voiceBtn.title = 'Speech recognition not supported in this browser';
        voiceBtn.style.opacity = '0.4';
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isListening = false;
    let startingText = '';
    let committedTranscript = '';
    let currentInterim = '';

    let audioStream = null;
    let audioCtx = null;
    let analyserNode = null;
    let visualizerAnimationId = null;

    function getSelectedLang() {
        const langSelect = document.getElementById('languageSelect');
        const langVal = langSelect ? langSelect.value : 'en';
        if (langVal === 'hi') return 'hi-IN';
        if (langVal === 'hinglish') return 'hi-IN';
        return 'en-IN';
    }

    function createRecognitionInstance() {
        const rec = new SpeechRecognition();
        rec.continuous = true;
        rec.interimResults = true;
        rec.maxAlternatives = 1;
        rec.lang = getSelectedLang();

        rec.onstart = () => {
            isListening = true;
            startingText = chatInput.value ? (chatInput.value.trim() + ' ') : '';
            committedTranscript = '';
            currentInterim = '';

            attachBtn.style.display = 'none';
            chatInput.style.display = 'none';
            voiceBtn.style.display = 'none';

            voiceTrack.style.display = 'flex';
            stopBtn.style.display = 'flex';

            if (errorToast) errorToast.style.display = 'none';

            startAudioWave();
        };

        rec.onresult = (event) => {
            let interim = '';
            let newFinal = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                const text = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    newFinal += text + ' ';
                } else {
                    interim += text;
                }
            }

            if (newFinal) {
                committedTranscript += newFinal;
            }
            currentInterim = interim;
        };

        rec.onerror = (event) => {
            console.warn("Speech recognition error:", event.error);
            if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
                showVoiceError("⚠️ Microphone access denied. Click the lock/camera icon in your address bar to allow microphone.");
            }
            stopListening(false);
        };

        rec.onend = () => {
            if (isListening) {
                stopListening(false);
            }
        };

        return rec;
    }

    function showVoiceError(msg) {
        if (!errorToast) return;
        errorToast.innerHTML = `<span>${msg}</span><button onclick="document.getElementById('voiceErrorToast').style.display='none'">✕</button>`;
        errorToast.style.display = 'flex';
        setTimeout(() => {
            if (errorToast) errorToast.style.display = 'none';
        }, 8000);
    }

    async function startAudioWave() {
        if (waveformBars) {
            waveformBars.classList.add('idle');
        }

        try {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                if (AudioContext) {
                    audioCtx = new AudioContext();
                    analyserNode = audioCtx.createAnalyser();
                    analyserNode.fftSize = 64;
                    const source = audioCtx.createMediaStreamSource(audioStream);
                    source.connect(analyserNode);

                    const dataArray = new Uint8Array(analyserNode.frequencyBinCount);
                    const bars = waveformBars ? waveformBars.querySelectorAll('.wave-bar') : [];
                    const mid = bars.length / 2;

                    function animateBars() {
                        if (!isListening) return;
                        analyserNode.getByteFrequencyData(dataArray);

                        let sum = 0;
                        for (let i = 0; i < dataArray.length; i++) {
                            sum += dataArray[i];
                        }
                        const avg = sum / dataArray.length;

                        bars.forEach((bar, index) => {
                            const distFromCenter = Math.abs(index - mid);
                            const bellWeight = Math.max(0.25, 1 - (distFromCenter / mid) * 0.75);
                            const freqVal = (dataArray[index] || avg) * bellWeight;
                            const scale = Math.max(0.6, Math.min(3.8, freqVal / 22));
                            bar.style.transform = `scaleY(${scale})`;
                            if (scale > 1.4) {
                                bar.style.backgroundColor = '#3b82f6';
                            } else {
                                bar.style.backgroundColor = '#64748b';
                            }
                        });

                        visualizerAnimationId = requestAnimationFrame(animateBars);
                    }
                    animateBars();
                }
            }
        } catch (e) {
            console.log("Audio visualizer running in CSS mode");
        }
    }

    function stopAudioWave() {
        if (visualizerAnimationId) {
            cancelAnimationFrame(visualizerAnimationId);
            visualizerAnimationId = null;
        }
        if (audioStream) {
            audioStream.getTracks().forEach(track => track.stop());
            audioStream = null;
        }
        if (audioCtx && audioCtx.state !== 'closed') {
            audioCtx.close();
            audioCtx = null;
        }
        if (waveformBars) {
            const bars = waveformBars.querySelectorAll('.wave-bar');
            bars.forEach(bar => {
                bar.style.transform = '';
                bar.style.backgroundColor = '';
            });
            waveformBars.classList.remove('idle');
        }
    }

    function stopListening(autoSend = false) {
        isListening = false;
        if (recognition) {
            try {
                recognition.stop();
            } catch (e) {}
            recognition = null;
        }

        stopAudioWave();

        voiceTrack.style.display = 'none';
        stopBtn.style.display = 'none';

        attachBtn.style.display = 'flex';
        chatInput.style.display = 'block';
        voiceBtn.style.display = 'flex';

        const finalRecordedText = (startingText + committedTranscript + currentInterim).trim();
        if (finalRecordedText) {
            chatInput.value = finalRecordedText;
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
            updateSendButtonState();
        }

        if (autoSend && chatInput.value.trim()) {
            handleSend();
        } else {
            chatInput.focus();
        }
    }

    function startListening() {
        if (isListening) return;
        try {
            recognition = createRecognitionInstance();
            recognition.start();
        } catch (e) {
            console.error("Could not start speech recognition:", e);
            stopListening(false);
        }
    }

    voiceBtn.addEventListener('click', (e) => {
        e.preventDefault();
        startListening();
    });

    stopBtn.addEventListener('click', (e) => {
        e.preventDefault();
        stopListening(false);
    });

    sendBtn.addEventListener('click', (e) => {
        if (isListening) {
            e.preventDefault();
            stopListening(true);
        }
    });
}
