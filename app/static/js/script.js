// /static/js/script.js

$(document).ready(function () {
    // --- Konfigurasi Global ---
    const BOT_AVATAR = '<img src="/static/images/logo-stikom.png" alt="Logo STIKOM">';
    const USER_AVATAR = '<img src="/static/images/profil.png" alt="User">';
    const TYPING_SPEED = 10; // milidetik

    let isBotResponding = false;
    const chatBox = $("#chat-box");
    const userInput = $("#user-input");
    const sendBtn = $("#send-btn");

    // Konfigurasi Marked.js (sudah baik, bisa disederhanakan)
    marked.setOptions({
        breaks: true,
        gfm: true,
        renderer: new marked.Renderer()
    });

    // --- Fungsi Utilitas ---

    const getCurrentTime = () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const scrollToBottom = () => {
        chatBox.scrollTop(chatBox[0].scrollHeight);
    };

    const toggleInputState = (disabled) => {
        isBotResponding = disabled;
        userInput.prop("disabled", disabled);
        sendBtn.prop("disabled", disabled);
        if (!disabled) {
            userInput.focus();
        }
    };

    // --- Fungsi Utama Chat ---

    function addMessage(message, isUser) {
        const senderClass = isUser ? "user-message" : "bot-message";
        const avatar = isUser ? USER_AVATAR : BOT_AVATAR;
        
        // Menggunakan Marked.js untuk mem-parse markdown
        const htmlMessage = marked.parse(message.trim());

        const messageElement = `
            <div class="chat-message ${senderClass}">
                <div class="message-avatar">${avatar}</div>
                <div class="message-content">
                    ${htmlMessage}
                    <span class="message-time">${getCurrentTime()}</span>
                </div>
            </div>`;
        
        chatBox.append(messageElement);
        scrollToBottom();
    }
    
    function typeBotMessage(message) {
        const typingId = `typing-effect-${Date.now()}`;
        const messageElement = `
            <div class="chat-message bot-message">
                <div class="message-avatar">${BOT_AVATAR}</div>
                <div class="message-content">
                    <div id="${typingId}" class="typing-effect"></div>
                    <span class="message-time">${getCurrentTime()}</span>
                </div>
            </div>`;

        chatBox.append(messageElement);
        scrollToBottom();
        
        const typingEffect = $(`#${typingId}`);
        const htmlMessage = marked.parse(message.trim());
        
        let i = 0;
        function typeWriter() {
            if (i < htmlMessage.length) {
                typingEffect.html(htmlMessage.substring(0, i + 1));
                i++;
                setTimeout(typeWriter, TYPING_SPEED);
            } else {
                typingEffect.removeClass('typing-effect');
                scrollToBottom();
                toggleInputState(false);
            }
        }
        typeWriter();
    }

    function sendMessage() {
        const message = userInput.val().trim();
        if (message === "" || isBotResponding) return;

        toggleInputState(true);
        addMessage(message, true);
        userInput.val("");

        $.ajax({
            url: "/get_response",
            method: "POST",
            data: { message: message },
            timeout: 30000,
            success: (response) => {
                if (response && response.response) {
                    typeBotMessage(response.response);
                } else {
                    typeBotMessage("Maaf, terjadi kesalahan pada format respons dari server.");
                }
            },
            error: (xhr) => {
                let errorMessage = "Maaf, terjadi kesalahan. Silakan coba lagi.";
                if (xhr.status === 0) {
                    errorMessage = "Tidak dapat terhubung ke server.";
                } else if (xhr.status >= 500) {
                    errorMessage = "Terjadi kesalahan internal pada server.";
                }
                typeBotMessage(errorMessage);
            },
            complete: () => {
                // Penanganan state sudah dilakukan di dalam `typeBotMessage`
            }
        });
    }

    // --- Event Handlers ---
    sendBtn.on("click", (e) => {
        e.preventDefault();
        sendMessage();
    });

    userInput.on("keypress", (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // --- Inisialisasi ---
    userInput.focus();
});