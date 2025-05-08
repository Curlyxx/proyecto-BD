let isTyping = false; // Estado para saber si la IA está escribiendo
let typingInterval; // Intervalo de la animación de escritura

// Función para limpiar el chat
function clearChat() {
    let chat = document.getElementById("chat");
    chat.innerHTML = ""; // Elimina todos los mensajes del chat
}

// Asignar la función clearChat al botón "Nuevo Chat"
document.getElementById("newChatButton").addEventListener("click", clearChat);

function submitComment() {
    let input = document.getElementById("userInput");
    let chat = document.getElementById("chat");

    if (input.value.trim() !== "" && !isTyping) {
        // Mostrar el mensaje del usuario
        let userMessage = document.createElement("div");
        userMessage.classList.add("message", "user-message");
        userMessage.textContent = input.value;
        chat.appendChild(userMessage);

        // Deshabilitar el input y cambiar el botón a "Parar"
        input.disabled = true;
        document.getElementById("sendButton").style.display = "none";
        document.getElementById("stopButton").style.display = "inline-block";
        isTyping = true;

        // Hacer una solicitud al backend de Wikipedia
        fetch(`http://localhost/Ia/backend/wikipedia.php?termino=${encodeURIComponent(input.value)}`)
            .then(response => response.text())
            .then(data => {
                // Generar una respuesta de la IA
                let aiResponse = data;
                let aiMessage = document.createElement("div");
                aiMessage.classList.add("message", "ai-message");

                // Animación de escritura
                let text = "";
                let index = 0;
                typingInterval = setInterval(() => {
                    if (index < aiResponse.length) {
                        text += aiResponse.charAt(index);
                        aiMessage.innerHTML = text; // Usar innerHTML para mantener el formato
                        index++;
                    } else {
                        clearInterval(typingInterval);
                        isTyping = false;
                        input.disabled = false; // Habilitar el input cuando la IA termina de escribir
                        document.getElementById("sendButton").style.display = "inline-block";
                        document.getElementById("stopButton").style.display = "none";
                    }
                }, 30); // Velocidad de escritura (30ms por letra)

                chat.appendChild(aiMessage);
            })
            .catch(error => {
                console.error('Error:', error);
                // Mostrar un mensaje de error en caso de fallo
                let aiMessage = document.createElement("div");
                aiMessage.classList.add("message", "ai-message");
                aiMessage.textContent = "Hubo un error al procesar tu solicitud. Inténtalo de nuevo.";
                chat.appendChild(aiMessage);

                // Restablecer el estado
                clearInterval(typingInterval);
                isTyping = false;
                input.disabled = false;
                document.getElementById("sendButton").style.display = "inline-block";
                document.getElementById("stopButton").style.display = "none";
            });

        // Limpiar el campo de entrada
        input.value = "";

        // Desplazar el chat hacia abajo
        chat.scrollTop = chat.scrollHeight;
    }
}

function stopTyping() {
    if (isTyping) {
        clearInterval(typingInterval); // Detener la animación de escritura
        isTyping = false;
        document.getElementById("userInput").disabled = false; // Habilitar el input
        document.getElementById("sendButton").style.display = "inline-block";
        document.getElementById("stopButton").style.display = "none";
    }
}

// Generar figuras animadas
function createShape() {
    const shape = document.createElement("div");
    shape.classList.add("shape");
    document.querySelector(".background-animations").appendChild(shape);

    const size = Math.random() * 20 + 10 + "px";
    shape.style.width = size;
    shape.style.height = size;
    shape.style.left = Math.random() * 100 + "vw";
    shape.style.animationDuration = Math.random() * 3 + 2 + "s";

    setTimeout(() => {
        shape.remove();
    }, 5000);
}

setInterval(createShape, 500);