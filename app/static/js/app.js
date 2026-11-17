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
    initLanguageSelector();
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

// Format markdown according to the reference image design (Supports English, Hindi, Hinglish)
function formatLegalMarkdown(text) {
    let html = escapeHtml(text);

    // Section headers: "### | Your Situation", "### | आपकी स्थिति", etc.
    html = html.replace(/###\s*\|\s*([^\n]+)/g, '<div class="section-header-bar">$1</div>');
    html = html.replace(/###\s*([^\n]+)/g, '<div class="section-header-bar">$1</div>');

    // Callout box for Information I still need from you (supports English, Hindi, Hinglish)
    html = html.replace(/(?:ℹ️\s*)?(?:Information\s*I\s*still\s*need\s*from\s*you|आपसे\s*आवश्यक\s*जानकारी|Zaroori\s*Jankari)\s*([\s\S]*?)(?=(?:<div class="section-header-bar"|$))/gi, (match, body) => {
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

/* --- Language Selector Controller --- */
function initLanguageSelector() {
    const langSelect = document.getElementById('languageSelect');
    const chatInput = document.getElementById('chatInput');
    const toast = document.getElementById('langSwitchToast');

    if (!langSelect) return;

    langSelect.addEventListener('change', () => {
        const val = langSelect.value;
        let toastMsg = "";

        if (val === 'hi') {
            chatInput.placeholder = "अपनी कानूनी समस्या यहाँ लिखें (जैसे: मकान मालिक डिपॉज़िट नहीं दे रहा)...";
            toastMsg = "🇮🇳 भाषा: हिंदी (Hindi) — LawPilot AI हिंदी में उत्तर देगा";
        } else if (val === 'hinglish') {
            chatInput.placeholder = "Apni legal problem yahan likhein (e.g. landlord deposit nahi de raha)...";
            toastMsg = "🇮🇳 Language: Hinglish — LawPilot AI Hinglish me reply karega";
        } else {
            chatInput.placeholder = "Describe your legal problem in plain English...";
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

/* --- ChatGPT Voice Mode Inside-The-Bar (Matching User Reference Image 3) --- */
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

    // Web Audio Visualizer State
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

            // Switch UI into ChatGPT Voice Waveform Mode (Image 3)
            attachBtn.style.display = 'none';
            chatInput.style.display = 'none';
            voiceBtn.style.display = 'none';

            voiceTrack.style.display = 'flex';
            stopBtn.style.display = 'flex';

            if (errorToast) errorToast.style.display = 'none';

            // Start Audio Wave Visualizer
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
                            // Centered Gaussian bell curve weighting
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

        // Restore normal ChatGPT input bar UI
        voiceTrack.style.display = 'none';
        stopBtn.style.display = 'none';

        attachBtn.style.display = 'flex';
        chatInput.style.display = 'block';
        voiceBtn.style.display = 'flex';

        // Commit transcription
        const finalRecordedText = (startingText + committedTranscript + currentInterim).trim();
        if (finalRecordedText) {
            chatInput.value = finalRecordedText;
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
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

    // Click Mic -> Start ChatGPT Waveform Mode
    voiceBtn.addEventListener('click', (e) => {
        e.preventDefault();
        startListening();
    });

    // Click White Circular Stop Button [ ■ ] -> Stop recording & show text
    stopBtn.addEventListener('click', (e) => {
        e.preventDefault();
        stopListening(false);
    });

    // Send button click while listening: Stop and Send immediately
    sendBtn.addEventListener('click', (e) => {
        if (isListening) {
            e.preventDefault();
            stopListening(true);
        }
    });
}
