$(document).ready(function () {
    let isBotResponding = false;

    function addMessage(message, isUser) {
        const chatBox = $("#chat-box");
        const messageClass = isUser ? "user-message" : "bot-message";
        const messageElement = `<div class="chat-message ${messageClass}"><p>${message}</p></div>`;
        chatBox.append(messageElement);
        scrollToBottom();
    }

    function typeMessage(message, isUser = false) {
        const chatBox = $("#chat-box");
        const messageClass = isUser ? "user-message" : "bot-message";
        const typingId = "typing-effect-" + Date.now();
        const typingElement = `<div class="chat-message ${messageClass}"><p id="${typingId}"></p></div>`;
        chatBox.append(typingElement);
        scrollToBottom();

        let i = 0;
        const speed = 12;
        const typingEffect = $("#" + typingId);

        function typeWriter() {
            if (i < message.length) {
                typingEffect.html(message.substring(0, i + 1).replace(/\n/g, "<br>"));
                i++;
                setTimeout(typeWriter, speed);
            } else {
                scrollToBottom();
                isBotResponding = false;
                $("#send-btn").prop("disabled", false);
            }
        }

        typeWriter();
    }

    function scrollToBottom() {
        const chatBox = $("#chat-box");
        chatBox.scrollTop(chatBox[0].scrollHeight);
    }

    function sendMessage() {
        if (isBotResponding) {
            return;
        }

        const userInput = $("#user-input").val().trim();
        if (userInput !== "") {
            isBotResponding = true;
            $("#send-btn").prop("disabled", true);
            addMessage(userInput, true);
            $("#user-input").val("");

            $.ajax({
                url: "/get_response",
                method: "POST",
                data: { message: userInput },
                success: function (response) {
                    typeMessage(response.response, false);
                },
                error: function () {
                    typeMessage("Maaf, terjadi kesalahan. Silakan coba lagi.", false);
                    isBotResponding = false;
                    $("#send-btn").prop("disabled", false);
                }
            });
        }
    }

    $("#send-btn").click(sendMessage);

    function handleKeyPress(event) {
        if (event.keyCode === 13 && !isBotResponding) {
            sendMessage();
        }
    }

    window.handleKeyPress = handleKeyPress;
});
