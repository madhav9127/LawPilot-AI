/**
 * LawPilot AI - Core Application Frontend State & API Controller
 */

// Global State
const appState = {
    currentTab: 'home',
    currentLanguage: 'en',
    currentState: 'All India (Central)',
    conversationHistory: [],
    currentCase: {
        category: 'general',
        user_role: 'Aggrieved Party',
        counterparty_name: 'Opposing Party',
        financial_amounts: { primary_amount: null, formatted_primary: 'Not specified' },
        agreements: 'Not specified',
        timeline: [],
        available_evidence: [],
        missing_information: []
    },
    evidenceList: [],
    isTyping: false
};

// Initialize Speech
let voiceAssistant = null;

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initSpeechAssistant();
    initChatHandlers();
    initDocumentGenerator();
    initFileUpload();
    loadEvidenceChecklist('general');
});

// --- NAVIGATION ---
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabTarget = item.getAttribute('data-tab');
            switchTab(tabTarget);
        });
    });
}

function switchTab(tabId) {
    appState.currentTab = tabId;
    
    // Update nav links
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.getAttribute('data-tab') === tabId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Update tab sections
    document.querySelectorAll('.tab-content').forEach(section => {
        if (section.id === `tab-${tabId}`) {
            section.classList.add('active');
        } else {
            section.classList.remove('active');
        }
    });

    // If switching to My Cases, re-render dashboard
    if (tabId === 'cases') {
        renderCaseDashboard();
    }
    // If switching to Doc Generator, prefill from current case
    if (tabId === 'docs') {
        prefillDocGenerator();
    }
}

// --- CATEGORY & EXAMPLE CLICK-THROUGHS ---
function startScenario(queryText, category = null) {
    switchTab('assistant');
    const input = document.getElementById('chatInput');
    input.value = queryText;
    sendMessage();
}

// --- VOICE ASSISTANT ---
function initSpeechAssistant() {
    const micBtn = document.getElementById('micBtn');
    if (!micBtn) return;

    voiceAssistant = new VoiceAssistant(
        (transcript, isFinal) => {
            const input = document.getElementById('chatInput');
            input.value = transcript;
            if (isFinal) {
                // Flash input
                input.style.borderColor = 'var(--accent-teal)';
            }
        },
        (isRecording) => {
            if (isRecording) {
                micBtn.style.color = '#ef4444';
                micBtn.title = "Listening... Click to stop";
            } else {
                micBtn.style.color = 'var(--text-muted)';
                micBtn.title = "Speak in English or Hindi";
            }
        }
    );

    micBtn.addEventListener('click', () => {
        const langSelector = document.getElementById('languageSelect');
        if (langSelector && voiceAssistant) {
            voiceAssistant.setLanguage(langSelector.value);
        }
        if (voiceAssistant) voiceAssistant.toggle();
    });
}

// --- CHAT CONTROLLER ---
function initChatHandlers() {
    const sendBtn = document.getElementById('sendBtn');
    const chatInput = document.getElementById('chatInput');
    const clearBtn = document.getElementById('clearChatBtn');
    const langSelect = document.getElementById('languageSelect');
    const stateSelect = document.getElementById('stateSelect');

    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', async () => {
            if (confirm("Reset conversation and clear session?")) {
                const container = document.getElementById('chatMessages');
                container.innerHTML = `
                    <div class="msg-bubble msg-ai">
                        <div class="status-badge status-verified">Session Ready</div>
                        <p>Welcome to <b>LawPilot AI</b>. Explain your legal problem in plain English, Hindi, or Hinglish.</p>
                    </div>
                `;
                appState.conversationHistory = [];
                await fetch('/api/session/reset', { method: 'POST' });
            }
        });
    }

    if (langSelect) {
        langSelect.addEventListener('change', (e) => {
            appState.currentLanguage = e.target.value;
            if (voiceAssistant) voiceAssistant.setLanguage(e.target.value);
        });
    }

    if (stateSelect) {
        stateSelect.addEventListener('change', (e) => {
            appState.currentState = e.target.value;
        });
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message || appState.isTyping) return;

    // Append user message
    appendMessage('user', message);
    input.value = '';
    appState.conversationHistory.push({ role: 'user', content: message });

    // Show typing indicator
    showTypingIndicator();
    appState.isTyping = true;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                conversation_history: appState.conversationHistory,
                language: appState.currentLanguage,
                state_jurisdiction: appState.currentState
            })
        });

        const data = await response.json();
        hideTypingIndicator();
        appState.isTyping = false;

        appendMessage('assistant', data.content, data.citations, data.verification_status, data.follow_up_questions, data.escalation_detected);
        appState.conversationHistory.push({ role: 'assistant', content: data.content });

        // Update Case Background Extraction
        updateCaseFacts(message);

    } catch (err) {
        hideTypingIndicator();
        appState.isTyping = false;
        appendMessage('assistant', "⚠️ Connection error: Unable to contact legal assistant service. Please check your connection.");
    }
}

function appendMessage(role, content, citations = [], status = null, followUps = [], isEscalated = false) {
    const container = document.getElementById('chatMessages');
    const bubble = document.createElement('div');
    bubble.className = `msg-bubble msg-${role}`;

    let html = '';

    if (role === 'assistant') {
        if (status) {
            let statusClass = 'status-verified';
            if (status.includes('recommended')) statusClass = 'status-recommended';
            if (status.includes('Insufficient')) statusClass = 'status-insufficient';
            html += `<div class="status-badge ${statusClass}">${escapeHtml(status)}</div>`;
        }

        if (isEscalated) {
            html += `
                <div class="escalation-banner">
                    <div class="escalation-title">⚠️ URGENT LEGAL ESCALATION REQUIRED</div>
                    <div class="escalation-text">This matter involves imminent deadlines, physical eviction threats, or potential court summons. Please contact emergency services or a qualified advocate immediately.</div>
                </div>
            `;
        }
    }

    // Convert markdown to clean HTML
    html += `<div class="markdown-body">${formatMarkdown(content)}</div>`;

    // Add Citations
    if (citations && citations.length > 0) {
        html += '<div style="margin-top: 0.8rem; border-top: 1px dashed var(--border-slate); padding-top: 0.5rem;">';
        html += '<div style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); margin-bottom: 0.3rem;">VERIFIED STATUTORY CITATIONS:</div>';
        citations.forEach(c => {
            html += `<a href="${c.official_url}" target="_blank" rel="noopener noreferrer" class="citation-chip" title="${escapeHtml(c.title)}">📖 ${escapeHtml(c.act_name)} - ${escapeHtml(c.section)} ↗</a>`;
        });
        html += '</div>';
    }

    // Add Follow-up Chips
    if (followUps && followUps.length > 0) {
        html += '<div style="margin-top: 0.8rem; display: flex; flex-wrap: wrap; gap: 0.4rem;">';
        followUps.forEach(q => {
            html += `<button class="example-item" style="border: 1px solid var(--border-slate); cursor: pointer;" onclick="followUpClicked('${escapeHtml(q)}')">💬 ${escapeHtml(q)}</button>`;
        });
        html += '</div>';
    }

    // Copy Button for AI messages
    if (role === 'assistant') {
        html += `
            <div style="display: flex; justify-content: flex-end; margin-top: 0.5rem;">
                <button class="btn-icon" style="font-size: 0.75rem;" onclick="copyText(this)" title="Copy response">📋 Copy</button>
            </div>
        `;
    }

    bubble.innerHTML = html;
    container.appendChild(bubble);
    container.scrollTop = container.scrollHeight;
}

function followUpClicked(questionText) {
    const input = document.getElementById('chatInput');
    input.value = questionText;
    sendMessage();
}

function copyText(btn) {
    const bubble = btn.closest('.msg-bubble');
    const md = bubble.querySelector('.markdown-body');
    if (md) {
        navigator.clipboard.writeText(md.innerText).then(() => {
            const original = btn.innerHTML;
            btn.innerHTML = '✅ Copied!';
            setTimeout(() => { btn.innerHTML = original; }, 2000);
        });
    }
}

function showTypingIndicator() {
    const container = document.getElementById('chatMessages');
    const indicator = document.createElement('div');
    indicator.id = 'typingIndicator';
    indicator.className = 'msg-bubble msg-ai';
    indicator.innerHTML = '<span style="color: var(--text-muted); font-size: 0.85rem;">⚖️ Analyzing verified legal statutes...</span>';
    container.appendChild(indicator);
    container.scrollTop = container.scrollHeight;
}

function hideTypingIndicator() {
    const ind = document.getElementById('typingIndicator');
    if (ind) ind.remove();
}

// --- CASE EXTRACTION & DASHBOARD ---
async function updateCaseFacts(userText) {
    try {
        const response = await fetch('/api/case/extract', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: userText,
                state_jurisdiction: appState.currentState
            })
        });
        const caseData = await response.json();
        appState.currentCase = caseData;

        // Update sidebar widgets
        updateSidebarDisplay(caseData);
        // Load appropriate evidence checklist
        loadEvidenceChecklist(caseData.category);

    } catch (e) {
        console.error("Case extraction error:", e);
    }
}

function updateSidebarDisplay(c) {
    const catElem = document.getElementById('sideCategory');
    const amtElem = document.getElementById('sideAmount');
    const partyElem = document.getElementById('sideParties');
    const evidenceElem = document.getElementById('sideEvidence');

    if (catElem) catElem.innerText = c.category.toUpperCase().replace('_', ' ');
    if (amtElem) amtElem.innerText = c.financial_amounts.formatted_primary || 'Not specified';
    if (partyElem) partyElem.innerText = `${c.user_role} vs ${c.counterparty_name}`;
    if (evidenceElem) evidenceElem.innerText = c.available_evidence.length > 0 ? c.available_evidence.join(', ') : 'Pending verification';
}

function renderCaseDashboard() {
    const c = appState.currentCase;
    const catInput = document.getElementById('caseFieldCategory');
    const userRoleInput = document.getElementById('caseFieldUserRole');
    const oppPartyInput = document.getElementById('caseFieldOpponent');
    const amtInput = document.getElementById('caseFieldAmount');
    const incidentDesc = document.getElementById('caseFieldIncident');
    const agreementsInput = document.getElementById('caseFieldAgreement');
    const missingList = document.getElementById('caseMissingList');

    if (catInput) catInput.value = c.category;
    if (userRoleInput) userRoleInput.value = c.user_role || '';
    if (oppPartyInput) oppPartyInput.value = c.counterparty_name || '';
    if (amtInput) amtInput.value = c.financial_amounts.formatted_primary || '';
    if (incidentDesc) incidentDesc.value = c.incident_description || '';
    if (agreementsInput) agreementsInput.value = c.agreements || '';

    if (missingList) {
        if (c.missing_information && c.missing_information.length > 0) {
            missingList.innerHTML = c.missing_information.map(m => `<li style="color: #b45309; margin-bottom: 0.3rem;">⚠️ ${escapeHtml(m)}</li>`).join('');
        } else {
            missingList.innerHTML = '<li style="color: #15803d;">✅ All primary facts and jurisdiction recorded.</li>';
        }
    }
}

// --- EVIDENCE CHECKLIST ---
async function loadEvidenceChecklist(category) {
    try {
        const response = await fetch(`/api/evidence/${category}`);
        const items = await response.json();
        appState.evidenceList = items;
        renderEvidenceChecklist(items);
    } catch (e) {
        console.error("Evidence fetch failed:", e);
    }
}

function renderEvidenceChecklist(items) {
    const container = document.getElementById('evidenceContainer');
    if (!container) return;

    container.innerHTML = '';
    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'cat-card';
        card.style.marginBottom = '1rem';
        card.style.padding = '1rem';

        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                <h4 style="font-size: 0.95rem; font-weight: 700;">${escapeHtml(item.name)}</h4>
                <div style="display: flex; gap: 0.3rem;">
                    <button class="btn-icon status-btn ${item.status === 'available' ? 'active-avail' : ''}" onclick="setEvidenceStatus('${item.id}', 'available', this)">✅ Have it</button>
                    <button class="btn-icon status-btn ${item.status === 'unavailable' ? 'active-unavail' : ''}" onclick="setEvidenceStatus('${item.id}', 'unavailable', this)">❌ Don't have</button>
                </div>
            </div>
            <p style="font-size: 0.825rem; color: var(--text-muted); margin-bottom: 0.4rem;">${escapeHtml(item.description)}</p>
            <div style="font-size: 0.775rem; background: var(--bg-slate); padding: 0.4rem 0.6rem; border-radius: 6px; border-left: 3px solid var(--accent-teal);">
                <b>Legal Importance:</b> ${escapeHtml(item.legal_importance)}
            </div>
        `;
        container.appendChild(card);
    });
}

function setEvidenceStatus(itemId, status, btn) {
    const parent = btn.parentElement;
    parent.querySelectorAll('button').forEach(b => b.style.opacity = '0.5');
    btn.style.opacity = '1.0';
    btn.style.fontWeight = 'bold';
}

// --- DOCUMENT GENERATOR ---
function initDocumentGenerator() {
    const genBtn = document.getElementById('generateDocBtn');
    const pdfBtn = document.getElementById('downloadPdfBtn');
    const docxBtn = document.getElementById('downloadDocxBtn');

    if (genBtn) genBtn.addEventListener('click', generateDocumentDraft);
    if (pdfBtn) pdfBtn.addEventListener('click', downloadPdf);
    if (docxBtn) docxBtn.addEventListener('click', downloadDocx);
}

function prefillDocGenerator() {
    const c = appState.currentCase;
    const oppInput = document.getElementById('docOpponentName');
    const amtInput = document.getElementById('docAmount');
    const factsInput = document.getElementById('docFacts');
    const typeSelect = document.getElementById('docTypeSelect');

    if (oppInput && c.counterparty_name) oppInput.value = c.counterparty_name;
    if (amtInput && c.financial_amounts.formatted_primary) amtInput.value = c.financial_amounts.formatted_primary;
    if (factsInput && c.incident_description) factsInput.value = c.incident_description;

    if (typeSelect) {
        if (c.category === 'tenant') typeSelect.value = 'security_deposit_demand';
        else if (c.category === 'consumer') typeSelect.value = 'consumer_complaint_draft';
        else if (c.category === 'employment') typeSelect.value = 'unpaid_salary_demand';
    }
}

async function generateDocumentDraft() {
    const payload = getDocPayload();
    const preview = document.getElementById('docPreviewBox');
    if (preview) preview.value = "Drafting formal document under statutory guidelines...";

    try {
        const response = await fetch('/api/document/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (preview) preview.value = data.content_text;
    } catch (e) {
        if (preview) preview.value = "Error generating draft: " + e.toString();
    }
}

async function downloadPdf() {
    const payload = getDocPayload();
    const response = await fetch('/api/document/download/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `LawPilot_${payload.doc_type}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
}

async function downloadDocx() {
    const payload = getDocPayload();
    const response = await fetch('/api/document/download/docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `LawPilot_${payload.doc_type}.docx`;
    document.body.appendChild(a);
    a.click();
    a.remove();
}

function getDocPayload() {
    return {
        doc_type: document.getElementById('docTypeSelect')?.value || 'security_deposit_demand',
        user_name: document.getElementById('docUserName')?.value || 'Complainant / Claimant',
        user_address: document.getElementById('docUserAddress')?.value || 'Address not specified',
        counterparty_name: document.getElementById('docOpponentName')?.value || 'Opposite Party',
        counterparty_address: document.getElementById('docOpponentAddress')?.value || 'Address not specified',
        facts: document.getElementById('docFacts')?.value || 'Facts of the dispute',
        disputed_amount: document.getElementById('docAmount')?.value || 'Unspecified',
        incident_date: document.getElementById('docDate')?.value || 'Recent',
        demands: document.getElementById('docDemands')?.value || 'Immediate refund / release of outstanding dues',
        deadline_days: parseInt(document.getElementById('docDays')?.value || '15'),
        state: appState.currentState
    };
}

// --- FILE UPLOAD ---
function initFileUpload() {
    const fileInput = document.getElementById('fileUploadInput');
    const uploadBtn = document.getElementById('uploadFileBtn');

    if (uploadBtn && fileInput) {
        uploadBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            appendMessage('user', `📎 Uploaded Document: ${file.name}`);
            showTypingIndicator();

            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                hideTypingIndicator();

                if (!result.success) {
                    appendMessage('assistant', `⚠️ **Document Parsing Alert**: ${result.error}`);
                    return;
                }

                let reply = `📄 **Document Analyzed: ${result.filename}**\n\n`;
                reply += `**Detected Category:** ${result.category.toUpperCase()}\n`;
                if (result.extracted_amounts.formatted_primary) {
                    reply += `**Extracted Amount:** ${result.extracted_amounts.formatted_primary}\n`;
                }
                if (result.detected_clauses.length > 0) {
                    reply += `**Key Clauses Found:**\n${result.detected_clauses.map(c => `- ${c}`).join('\n')}\n\n`;
                }
                reply += `**Summary:** ${result.summary_snippet}\n\n`;
                reply += `*${result.confirmation_prompt}*`;

                appendMessage('assistant', reply);
                updateCaseFacts(result.summary_snippet);

            } catch (err) {
                hideTypingIndicator();
                appendMessage('assistant', "⚠️ Failed to process uploaded document. Please check the file format.");
            }
        });
    }
}

// --- UTILITIES ---
function formatMarkdown(text) {
    if (!text) return '';
    return text
        .replace(/### (.*?)\n/g, '<h3 style="margin-top: 0.6rem; margin-bottom: 0.3rem; font-size: 1.05rem; font-weight: 700;">$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
        .replace(/\*(.*?)\*/g, '<i>$1</i>')
        .replace(/\n\n/g, '<p style="margin-bottom: 0.6rem;"></p>')
        .replace(/\n- /g, '<br/>• ')
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color: var(--accent-teal); text-decoration: underline;">$1</a>');
}

function escapeHtml(string) {
    if (!string) return '';
    return String(string).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
