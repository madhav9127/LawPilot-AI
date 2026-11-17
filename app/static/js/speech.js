/**
 * LawPilot AI - Browser Speech Recognition Module
 * Supports English (en-IN) and Hindi (hi-IN) voice input via Web Speech API.
 */

class VoiceAssistant {
    constructor(onTranscriptCallback, onStateChangeCallback) {
        this.onTranscript = onTranscriptCallback;
        this.onStateChange = onStateChangeCallback;
        this.recognition = null;
        this.isRecording = false;
        this.currentLang = 'en-IN'; // Default Indian English
        this.initSpeech();
    }

    initSpeech() {
        window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!window.SpeechRecognition) {
            console.warn("Web Speech API not supported in this browser.");
            return;
        }

        try {
            this.recognition = new window.SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = true;
            this.recognition.lang = this.currentLang;

            this.recognition.onstart = () => {
                this.isRecording = true;
                if (this.onStateChange) this.onStateChange(true);
            };

            this.recognition.onresult = (event) => {
                let interimTranscript = '';
                let finalTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }

                const transcript = finalTranscript || interimTranscript;
                if (this.onTranscript) this.onTranscript(transcript, !!finalTranscript);
            };

            this.recognition.onerror = (event) => {
                console.error("Speech recognition error:", event.error);
                this.stop();
            };

            this.recognition.onend = () => {
                this.isRecording = false;
                if (this.onStateChange) this.onStateChange(false);
            };
        } catch (e) {
            console.error("Speech init failure:", e);
        }
    }

    setLanguage(langCode) {
        if (langCode === 'hi') {
            this.currentLang = 'hi-IN';
        } else {
            this.currentLang = 'en-IN';
        }
        if (this.recognition) {
            this.recognition.lang = this.currentLang;
        }
    }

    toggle() {
        if (!this.recognition) {
            alert("Speech recognition is not supported in your browser or microphone access is restricted. Please type your query in the input box.");
            return;
        }

        if (this.isRecording) {
            this.stop();
        } else {
            this.start();
        }
    }

    start() {
        if (this.recognition && !this.isRecording) {
            try {
                this.recognition.start();
            } catch (e) {
                console.error("Recognition start error:", e);
            }
        }
    }

    stop() {
        if (this.recognition && this.isRecording) {
            try {
                this.recognition.stop();
            } catch (e) {
                console.error("Recognition stop error:", e);
            }
            this.isRecording = false;
            if (this.onStateChange) this.onStateChange(false);
        }
    }
}
