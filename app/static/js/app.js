/**
 * LawPilot AI — Clean, Single-Page Chatbot Controller
 */

let conversationHistory = [];
let isSending = false;
let voiceAssistant = null;

document.addEventListener('DOMContentLoaded', () => {
    initChat();
    initSpeech();
    initFileUpload();
});

function initChat() {
    const sendBtn = document.getElementById('sendBtn');
    const chatInput = document.getElementById('chatInput');
    const resetBtn = document.getElementById('newChatBtn');

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

    resetBtn.addEventListener('click', () => {
        if (conversationHistory.length > 0 && confirm("Start a new conversation?")) {
            resetChat();
        }
    });
}

function resetChat() {
    conversationHistory = [];
    document.getElementById('messagesStream').innerHTML = '';
    document.getElementById('welcomeScreen').style.display = 'flex';
    document.getElementById('chatInput').value = '';
    fetch('/api/session/reset', { method: 'POST' }).catch(() => {});
}

function useExamplePrompt(text) {
    document.getElementById('chatInput').value = text;
    handleSend();
}

async function handleSend() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message || isSending) return;

    // Hide welcome screen
    document.getElementById('welcomeScreen').style.display = 'none';

    // Append user message
    appendMessageRow('user', message);
    input.value = '';
    input.style.height = 'auto';
    conversationHistory.push({ role: 'user', content: message });

    // Show typing state
    isSending = true;
    const typingId = showTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                conversation_history: conversationHistory,
                language: 'en'
            })
        });

        const data = await response.json();
        removeTypingIndicator(typingId);
        isSending = false;

        appendMessageRow('assistant', data.content, data.citations);
        conversationHistory.push({ role: 'assistant', content: data.content });

    } catch (err) {
        removeTypingIndicator(typingId);
        isSending = false;
        appendMessageRow('assistant', "⚠️ Connection issue: Unable to reach legal reasoning service. Please check your network.");
    }
}

function appendMessageRow(role, content, citations = []) {
    const stream = document.getElementById('messagesStream');
    const row = document.createElement('div');
    row.className = `message-row ${role}`;

    const bubble = document.createElement('div');
    bubble.className = `bubble ${role}`;

    const mdContent = document.createElement('div');
    mdContent.className = 'markdown-content';
    mdContent.innerHTML = renderMarkdown(content);
    bubble.appendChild(mdContent);

    // Citations
    if (citations && citations.length > 0) {
        const citeBox = document.createElement('div');
        citeBox.className = 'citation-container';
        citeBox.innerHTML = '<span style="font-size: 0.725rem; font-weight: 600; color: var(--text-muted); margin-right: 0.3rem;">Verified Sources:</span>';
        
        citations.forEach(c => {
            const badge = document.createElement('a');
            badge.className = 'citation-badge';
            badge.href = c.official_url;
            badge.target = '_blank';
            badge.rel = 'noopener noreferrer';
            badge.innerHTML = `📖 ${escapeHtml(c.act_name)} (${escapeHtml(c.section)}) ↗`;
            citeBox.appendChild(badge);
        });
        bubble.appendChild(citeBox);
    }

    // In-Chat Action Bar for Assistant
    if (role === 'assistant') {
        const actions = document.createElement('div');
        actions.className = 'bubble-actions';

        // 1. Copy
        const copyBtn = document.createElement('button');
        copyBtn.className = 'action-pill';
        copyBtn.innerHTML = '📋 Copy';
        copyBtn.onclick = () => {
            navigator.clipboard.writeText(content).then(() => {
                copyBtn.innerHTML = '✅ Copied!';
                setTimeout(() => { copyBtn.innerHTML = '📋 Copy'; }, 2000);
            });
        };
        actions.appendChild(copyBtn);

        // 2. Generate Notice Draft
        const draftBtn = document.createElement('button');
        draftBtn.className = 'action-pill teal';
        draftBtn.innerHTML = '📄 Generate Legal Notice Draft';
        draftBtn.onclick = () => {
            requestDocumentDraft();
        };
        actions.appendChild(draftBtn);

        // 3. Case Summary
        const summaryBtn = document.createElement('button');
        summaryBtn.className = 'action-pill';
        summaryBtn.innerHTML = '📊 Case Summary';
        summaryBtn.onclick = () => {
            document.getElementById('chatInput').value = "Summarize my case and tell me what information is missing.";
            handleSend();
        };
        actions.appendChild(summaryBtn);

        bubble.appendChild(actions);
    }

    row.appendChild(bubble);
    stream.appendChild(row);
    scrollToBottom();
}

function showTypingIndicator() {
    const stream = document.getElementById('messagesStream');
    const row = document.createElement('div');
    row.className = 'message-row assistant';
    const id = 'typing-' + Date.now();
    row.id = id;

    const bubble = document.createElement('div');
    bubble.className = 'bubble assistant';
    bubble.innerHTML = '<span style="color: var(--text-muted); font-size: 0.85rem;">⚖️ Analyzing verified Indian statutes...</span>';
    row.appendChild(bubble);
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

function requestDocumentDraft() {
    document.getElementById('chatInput').value = "Draft a formal legal notice based on our conversation.";
    handleSend();
}

// Voice Input
function initSpeech() {
    const voiceBtn = document.getElementById('voiceBtn');
    if (!voiceBtn) return;

    voiceAssistant = new VoiceAssistant(
        (transcript, isFinal) => {
            const input = document.getElementById('chatInput');
            input.value = transcript;
            input.style.height = 'auto';
            input.style.height = Math.min(input.scrollHeight, 120) + 'px';
        },
        (isRecording) => {
            if (isRecording) {
                voiceBtn.classList.add('recording');
                voiceBtn.title = 'Listening... Click to stop';
            } else {
                voiceBtn.classList.remove('recording');
                voiceBtn.title = 'Speak in English or Hindi';
            }
        }
    );

    voiceBtn.addEventListener('click', () => {
        if (voiceAssistant) voiceAssistant.toggle();
    });
}

// File Attachment
function initFileUpload() {
    const attachBtn = document.getElementById('attachBtn');
    const fileInput = document.getElementById('fileAttachment');

    if (!attachBtn || !fileInput) return;

    attachBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        document.getElementById('welcomeScreen').style.display = 'none';
        appendMessageRow('user', `📎 Uploaded Document: ${file.name}`);

        const formData = new FormData();
        formData.append('file', file);

        const typingId = showTypingIndicator();

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            removeTypingIndicator(typingId);

            if (!result.success) {
                appendMessageRow('assistant', `⚠️ **Security Alert:** ${result.error}`);
                return;
            }

            let msg = `📄 **Document Analyzed: ${result.filename}**\n\n`;
            if (result.extracted_amounts.formatted_primary) {
                msg += `- **Identified Amount:** ${result.extracted_amounts.formatted_primary}\n`;
            }
            if (result.detected_clauses.length > 0) {
                msg += `- **Key Clauses Identified:** ${result.detected_clauses.join(', ')}\n`;
            }
            msg += `\n**Summary:** ${result.summary_snippet}\n\n*${result.confirmation_prompt}*`;

            appendMessageRow('assistant', msg);
            conversationHistory.push({ role: 'assistant', content: msg });

        } catch (err) {
            removeTypingIndicator(typingId);
            appendMessageRow('assistant', "⚠️ Could not read uploaded file. Please ensure it is a valid PDF, DOCX, or text file.");
        }
    });
}

// Markdown helper
function renderMarkdown(text) {
    if (!text) return '';
    return text
        .replace(/### (.*?)\n/g, '<h3>$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
        .replace(/\*(.*?)\*/g, '<i>$1</i>')
        .replace(/\n\n/g, '<p></p>')
        .replace(/\n- /g, '<br/>• ')
        .replace(/```text\n([\s\S]*?)\n```/g, '<pre><code>$1</code></pre>')
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color: var(--accent-teal); text-decoration: underline;">$1</a>');
}

function escapeHtml(string) {
    if (!string) return '';
    return String(string).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
