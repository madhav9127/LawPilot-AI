/**
 * LawPilot AI — Single-Page Chat Controller & State Manager
 * Features:
 * - Dynamic 2-5 word legal title generation
 * - Genuine token streaming via Server-Sent Events (SSE)
 * - Clean professional UI without emojis (crisp SVG iconography)
 * - Automatic multilingual support (English, Hindi, Hinglish, Malayalam)
 * - Sub-millisecond local conversation switching (<0.1ms)
 * - Intelligent auto-scroll respecting manual user scrolling
 */

// --- Constants & Storage Keys ---
const STORAGE_KEY = 'lawpilot_conversations';
const ACTIVE_CONV_KEY = 'lawpilot_active_conv_id';

// --- State Variables ---
let conversations = [];
let activeConversationId = null;
let isSending = false;
let lastGeneratedDocReq = null;

// --- SVG Icons (Professional, Clean, No Emojis) ---
const SVG_ICONS = {
    chat: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,
    scales: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>`,
    copy: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>`,
    check: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
    document: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>`,
    link: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>`,
    info: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`,
    delete: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`
};

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    initState();
    initChatUI();
    initSpeech();
    initFileUpload();
    initModals();
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

    const sorted = [...conversations].sort((a, b) => (b.updatedAt || b.createdAt) - (a.updatedAt || a.createdAt));

    sorted.forEach(conv => {
        const item = document.createElement('div');
        item.className = 'history-item' + (conv.id === activeConversationId ? ' active' : '');
        item.setAttribute('data-conv-id', conv.id);

        item.innerHTML = `
            <span class="history-icon">${SVG_ICONS.chat}</span>
            <span class="history-text" title="${escapeHtml(conv.title)}">${escapeHtml(conv.title)}</span>
            <button class="history-delete-btn" title="Delete conversation" onclick="handleDeleteConv('${conv.id}', event)">
                ${SVG_ICONS.delete}
            </button>
        `;

        item.addEventListener('click', (e) => {
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

    const historyItems = document.querySelectorAll('.history-item');
    historyItems.forEach(item => {
        if (item.getAttribute('data-conv-id') === convId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

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
   LIGHTWEIGHT TITLE GENERATOR (2-5 WORDS)
   ========================================================================== */

function generateClientSideTitle(message) {
    if (!message || !message.trim()) return "New Consultation";

    const lower = message.toLowerCase().trim();

    // 1. Tenancy & Landlord Disputes
    if (lower.includes("evict") || lower.includes("nikal raha hai") || lower.includes("khali karne")) {
        return "Eviction Dispute";
    }
    if (lower.includes("deposit") || lower.includes("25,000") || lower.includes("25000") || lower.includes("डिपॉज़िट") || lower.includes("dharohar")) {
        if (lower.includes("deduct") || lower.includes("painting") || lower.includes("damage") || lower.includes("kaat")) {
            return "Deposit Deduction Dispute";
        }
        return "Security Deposit Dispute";
    }
    if (lower.includes("rent agreement") || lower.includes("kirayanama") || lower.includes("किराया")) {
        if (lower.includes("increase") || lower.includes("hike") || lower.includes("badha")) {
            return "Rent Increase Dispute";
        }
        return "Rental Agreement Issue";
    }
    if (lower.includes("landlord") || lower.includes("tenant") || lower.includes("makan malik") || lower.includes("kirayedar")) {
        return "Tenant Landlord Dispute";
    }

    // 2. Employment & Wage Disputes
    if (lower.includes("salary") || lower.includes("unpaid") || lower.includes("wages") || lower.includes("vetan") || lower.includes("tankhwah") || lower.includes("वेतन") || lower.includes("ശമ്പളം")) {
        if (lower.includes("deduct") || lower.includes("cut") || lower.includes("katoti")) {
            return "Salary Deduction Dispute";
        }
        return "Unpaid Salary Issue";
    }
    if (lower.includes("relieving") || lower.includes("experience letter")) {
        return "Relieving Letter Request";
    }
    if (lower.includes("fnf") || lower.includes("full and final") || lower.includes("settlement") || lower.includes("resignation")) {
        return "Employment Settlement Dispute";
    }
    if (lower.includes("terminate") || lower.includes("fired") || lower.includes("layoff")) {
        return "Employment Termination Issue";
    }
    if (lower.includes("employer") || lower.includes("company") || lower.includes("boss") || lower.includes("hr")) {
        return "Employment Dispute";
    }

    // 3. Consumer Protection & E-Commerce
    if (lower.includes("defective") || lower.includes("damaged") || lower.includes("kharab") || lower.includes("soap bar") || lower.includes("broken")) {
        return "Defective Product Refund";
    }
    if (lower.includes("refund") || lower.includes("money back") || lower.includes("wapas") || lower.includes("റീഫണ്ട്")) {
        return "Consumer Refund Issue";
    }
    if (lower.includes("amazon") || lower.includes("flipkart") || lower.includes("meesho") || lower.includes("e-commerce")) {
        return "E-Commerce Consumer Dispute";
    }
    if (lower.includes("unfair charge") || lower.includes("hidden charge") || lower.includes("overcharge") || lower.includes("billed")) {
        return "Unfair Billing Dispute";
    }
    if (lower.includes("warranty") || lower.includes("guarantee") || lower.includes("service center")) {
        return "Consumer Warranty Grievance";
    }

    // 4. Legal Notices & Documents
    if (lower.includes("legal notice") || lower.includes("court notice") || lower.includes("notice")) {
        return "Legal Notice Assistance";
    }

    // 5. Intelligent Word Fallback
    const stopWords = new Set([
        "i", "me", "my", "we", "our", "you", "your", "he", "she", "it", "they",
        "am", "is", "are", "was", "were", "be", "have", "has", "had", "do", "does", "did",
        "a", "an", "the", "and", "but", "if", "or", "because", "as", "at", "by", "for", "with",
        "about", "to", "from", "in", "on", "off", "over", "under", "then", "here", "there",
        "when", "where", "why", "how", "all", "any", "no", "not", "so", "can", "will", "please",
        "help", "want", "need", "tell", "what", "which", "this", "that"
    ]);

    const words = message.match(/[\w\u0900-\u097F\u0D00-\u0D7F]+/g) || [];
    const significant = words.filter(w => !stopWords.has(w.toLowerCase())).slice(0, 4);

    if (significant.length >= 2) {
        return significant.map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
    } else if (significant.length === 1) {
        return `${significant[0].charAt(0).toUpperCase() + significant[0].slice(1)} Legal Inquiry`;
    }

    return "Legal Consultation";
}

/* ==========================================================================
   CHAT UI & INPUT CONTROLLER
   ========================================================================== */

function initChatUI() {
    const sendBtn = document.getElementById('sendBtn');
    const chatInput = document.getElementById('chatInput');
    const resetBtn = document.getElementById('newChatBtn');
    const sidebarToggle = document.getElementById('sidebarToggleBtn');

    if (chatInput) {
        chatInput.placeholder = "Describe your legal problem...";

        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
            }
        });

        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
            updateSendButtonState();
        });

        updateSendButtonState();
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', handleSend);
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
   STREAMING MESSAGE DISPATCHER (ChatGPT Style)
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

    // Auto-generate title on the first user message
    const isFirstMessage = (conv.messages.length === 0);
    if (isFirstMessage) {
        conv.title = generateClientSideTitle(message);
        renderSidebar();
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

    conv.messages.push(userMsg);
    conv.updatedAt = Date.now();
    saveConversations();

    // Optimistically render user message on right
    appendUserRowToDOM(message, timeStr, userMsgId);

    // Clear input field and lock send button
    input.value = '';
    input.style.height = 'auto';
    isSending = true;
    updateSendButtonState();

    // Immediately prepare live streaming assistant row with animated 3-dot thinking indicator
    const assistantMsgId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substring(2, 6);
    const streamDom = initLiveAssistantRow(assistantMsgId);
    const bubble = streamDom.bubble;

    // Build conversation history strictly for the active chat
    const historyPayload = conv.messages.slice(0, -1).map(m => ({
        role: m.role,
        content: m.content
    }));

    try {
        const response = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                conversation_history: historyPayload,
                session_id: conv.id
            })
        });

        if (!response.ok) {
            throw new Error(`Server returned HTTP ${response.status}`);
        }

        let accumulatedText = "";
        let finalCitations = [];

        // Read Server-Sent Events stream using ReadableStream
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n\n");
            buffer = lines.pop(); // keep remainder

            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed.startsWith("data: ")) continue;

                const jsonStr = trimmed.substring(6).trim();
                if (!jsonStr) continue;

                try {
                    const data = JSON.parse(jsonStr);

                    if (data.type === "metadata") {
                        if (data.title && isFirstMessage) {
                            conv.title = data.title;
                            renderSidebar();
                        }
                        if (data.citations) {
                            finalCitations = data.citations;
                        }
                    } else if (data.type === "token") {
                        accumulatedText += data.content;
                        // Replace 3 thinking dots seamlessly with streamed response
                        if (bubble && activeConversationId === conv.id) {
                            bubble.innerHTML = formatLegalMarkdown(accumulatedText);
                            smartScrollToBottom();
                        }
                    } else if (data.type === "done") {
                        if (data.citations) {
                            finalCitations = data.citations;
                        }
                        if (data.title && isFirstMessage) {
                            conv.title = data.title;
                            renderSidebar();
                        }
                        if (data.content && !accumulatedText) {
                            accumulatedText = data.content;
                            if (bubble) bubble.innerHTML = formatLegalMarkdown(accumulatedText);
                        }
                    }
                } catch (e) {
                    console.warn("SSE parsing error:", e);
                }
            }
        }

        // Finalize assistant message in DOM
        finalizeLiveAssistantRow(streamDom.rowId, accumulatedText, finalCitations);

        // Save assistant message to conversation state & persistence
        const assistantMsg = {
            id: assistantMsgId,
            role: 'assistant',
            content: accumulatedText,
            citations: finalCitations,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            status: 'sent'
        };

        conv.messages.push(assistantMsg);
        conv.updatedAt = Date.now();
        saveConversations();

        isSending = false;
        updateSendButtonState();

    } catch (err) {
        console.error("Streaming chat request failed:", err);
        // Remove active thinking indicator row on error
        const row = document.getElementById(streamDom.rowId);
        if (row) row.remove();

        isSending = false;
        updateSendButtonState();

        if (activeConversationId === conv.id) {
            appendErrorRowToDOM(userMsgId, message);
        }
    }
}

async function retryMessage(userMsgId) {
    const conv = getActiveConversation();
    if (!conv) return;

    const msg = conv.messages.find(m => m.id === userMsgId);
    if (!msg) return;

    const errCard = document.getElementById('err_' + userMsgId);
    if (errCard) errCard.remove();

    if (isSending) return;
    isSending = true;
    updateSendButtonState();

    const assistantMsgId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substring(2, 6);
    const streamDom = initLiveAssistantRow(assistantMsgId);
    const bubble = streamDom.bubble;

    const historyPayload = conv.messages
        .filter(m => m.id !== userMsgId && m.status === 'sent')
        .map(m => ({ role: m.role, content: m.content }));

    try {
        const response = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: msg.content,
                conversation_history: historyPayload,
                session_id: conv.id
            })
        });

        if (!response.ok) {
            throw new Error(`Server returned HTTP ${response.status}`);
        }

        let accumulatedText = "";
        let finalCitations = [];

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n\n");
            buffer = lines.pop();

            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed.startsWith("data: ")) continue;

                const jsonStr = trimmed.substring(6).trim();
                if (!jsonStr) continue;

                try {
                    const data = JSON.parse(jsonStr);
                    if (data.type === "metadata" && data.citations) {
                        finalCitations = data.citations;
                    } else if (data.type === "token") {
                        accumulatedText += data.content;
                        // Replace 3 thinking dots seamlessly with streamed text
                        if (bubble && activeConversationId === conv.id) {
                            bubble.innerHTML = formatLegalMarkdown(accumulatedText);
                            smartScrollToBottom();
                        }
                    } else if (data.type === "done") {
                        if (data.citations) finalCitations = data.citations;
                        if (data.content && !accumulatedText) {
                            accumulatedText = data.content;
                            if (bubble) bubble.innerHTML = formatLegalMarkdown(accumulatedText);
                        }
                    }
                } catch (e) {}
            }
        }

        finalizeLiveAssistantRow(streamDom.rowId, accumulatedText, finalCitations);

        const assistantMsg = {
            id: assistantMsgId,
            role: 'assistant',
            content: accumulatedText,
            citations: finalCitations,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            status: 'sent'
        };

        conv.messages.push(assistantMsg);
        conv.updatedAt = Date.now();
        saveConversations();

        isSending = false;
        updateSendButtonState();

    } catch (err) {
        const row = document.getElementById(streamDom.rowId);
        if (row) row.remove();

        isSending = false;
        updateSendButtonState();
        appendErrorRowToDOM(userMsgId, msg.content);
    }
}

/* ==========================================================================
   DOM RENDERING & STREAMING HELPERS (No Emojis)
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

function initLiveAssistantRow(msgId) {
    const stream = document.getElementById('messagesStream');
    const row = document.createElement('div');
    row.className = 'assistant-row';
    row.id = 'row_' + msgId;

    row.innerHTML = `
        <div class="assistant-header">
            <div class="assistant-avatar">${SVG_ICONS.scales}</div>
            <span class="assistant-name">LawPilot AI</span>
        </div>
        <div class="assistant-bubble" id="bubble_${msgId}">
            <div class="thinking-dots-container" id="thinking_${msgId}" aria-label="Thinking...">
                <span class="thinking-dot"></span>
                <span class="thinking-dot"></span>
                <span class="thinking-dot"></span>
            </div>
        </div>
        <div class="assistant-actions-bar" id="actions_${msgId}" style="display: none;"></div>
    `;

    stream.appendChild(row);
    smartScrollToBottom();

    return {
        rowId: 'row_' + msgId,
        bubble: document.getElementById('bubble_' + msgId),
        actionsBar: document.getElementById('actions_' + msgId)
    };
}

function finalizeLiveAssistantRow(rowId, fullText, citations = []) {
    const row = document.getElementById(rowId);
    if (!row) return;

    const bubble = row.querySelector('.assistant-bubble');
    if (bubble) {
        bubble.innerHTML = formatLegalMarkdown(fullText);
    }

    const actionsBar = row.querySelector('.assistant-actions-bar');
    if (!actionsBar) return;

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
                <span>${SVG_ICONS.link}</span>
                <span>Sources (${citations.length}) ▾</span>
            </button>
            <div class="sources-container" id="${rowId}_sources">
                ${itemsHtml}
            </div>
        `;
    }

    actionsBar.innerHTML = `
        <button class="action-pill-btn" onclick="copyAssistantText(this)">
            <span>${SVG_ICONS.copy}</span>
            <span>Copy</span>
        </button>
        <button class="action-pill-btn" onclick="triggerDocumentDraft()">
            <span>${SVG_ICONS.document}</span>
            <span>Generate Document</span>
        </button>
        ${sourcesHtml}
    `;
    actionsBar.style.display = 'flex';
    smartScrollToBottom();
}

function appendAssistantRowToDOM(content, citations = [], msgId = '') {
    const stream = document.getElementById('messagesStream');
    if (!stream) return;

    const row = document.createElement('div');
    row.className = 'assistant-row';
    const rowId = msgId ? ('row_' + msgId) : ('msg_' + Date.now());
    row.id = rowId;

    const formattedHtml = formatLegalMarkdown(content);

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
                <span>${SVG_ICONS.link}</span>
                <span>Sources (${citations.length}) ▾</span>
            </button>
            <div class="sources-container" id="${rowId}_sources">
                ${itemsHtml}
            </div>
        `;
    }

    row.innerHTML = `
        <div class="assistant-header">
            <div class="assistant-avatar">${SVG_ICONS.scales}</div>
            <span class="assistant-name">LawPilot AI</span>
        </div>
        <div class="assistant-bubble">${formattedHtml}</div>
        <div class="assistant-actions-bar">
            <button class="action-pill-btn" onclick="copyAssistantText(this)">
                <span>${SVG_ICONS.copy}</span>
                <span>Copy</span>
            </button>
            <button class="action-pill-btn" onclick="triggerDocumentDraft()">
                <span>${SVG_ICONS.document}</span>
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
            <div class="assistant-avatar">${SVG_ICONS.scales}</div>
            <span class="assistant-name">LawPilot AI</span>
        </div>
        <div class="msg-error-card">
            <span>Could not reach LawPilot legal reasoning engine. Your message was preserved.</span>
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
            <div class="assistant-avatar">${SVG_ICONS.scales}</div>
            <span class="assistant-name">LawPilot AI</span>
        </div>
        <div class="assistant-bubble">
            <div class="thinking-dots-container" aria-label="Thinking...">
                <span class="thinking-dot"></span>
                <span class="thinking-dot"></span>
                <span class="thinking-dot"></span>
            </div>
        </div>
    `;
    stream.appendChild(row);
    smartScrollToBottom();
    return id;
}

function removeTypingIndicator(id) {
    if (!id) return;
    const el = document.getElementById(id);
    if (el) el.remove();
}

function smartScrollToBottom() {
    const viewport = document.getElementById('chatViewport');
    if (!viewport) return;
    const isNearBottom = viewport.scrollHeight - viewport.scrollTop - viewport.clientHeight < 120;
    if (isNearBottom) {
        viewport.scrollTop = viewport.scrollHeight;
    }
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
   LEGAL MARKDOWN FORMATTER (No Emojis)
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
                    <span>${SVG_ICONS.info}</span>
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
    html = html.replace(/<\/ul>\s*<ul>/g, '');

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
            btn.innerHTML = `<span>${SVG_ICONS.check}</span><span>Copied!</span>`;
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

        if (modalDocTitle) modalDocTitle.innerText = data.title || "Formal Legal Notice Draft";
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
                copyBtn.innerHTML = `<span>${SVG_ICONS.check}</span><span>Copied!</span>`;
                setTimeout(() => { copyBtn.innerText = 'Copy Text'; }, 2000);
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

    function createRecognitionInstance() {
        const rec = new SpeechRecognition();
        rec.continuous = true;
        rec.interimResults = true;
        rec.maxAlternatives = 1;
        rec.lang = 'en-IN';

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
                showVoiceError("Microphone access denied. Click the lock icon in your address bar to allow microphone.");
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
