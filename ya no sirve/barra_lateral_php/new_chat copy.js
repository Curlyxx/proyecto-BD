document.addEventListener('DOMContentLoaded', function () {
    // Elementos del DOM
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const closeSidebar = document.getElementById('closeSidebar');
    const contentWrapper = document.getElementById('contentWrapper');
    const floatingAssistant = document.querySelector('.floating-assistant');
    const chatArea = document.getElementById('chat');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const stopButton = document.getElementById('stopButton');
    const readButton = document.getElementById('readButton');
    const stopSpeechButton = document.getElementById('stopSpeechButton');
    const newChatButton = document.getElementById('newChatButton');

    // Variables globales
    let currentConversationId = null;
    let isTyping = false;
    let lastAudio = null;
    let currentSpeech = null;
    const API_BASE_URL = 'http://localhost:5001'; // URL base del backend Python

    // ==============================================
    // Funciones de la barra lateral
    // ==============================================

    function setupSidebar() {
        if (!sidebar || !sidebarToggle || !closeSidebar || !contentWrapper || !floatingAssistant) {
            console.error("Error: No se encontraron todos los elementos necesarios para la barra lateral");
            return;
        }

        function toggleSidebar() {
            const isOpen = sidebar.classList.toggle('open');
            contentWrapper.classList.toggle('sidebar-open', isOpen);
            floatingAssistant.classList.toggle('shifted', isOpen);

            if (sidebarToggle.querySelector('i')) {
                sidebarToggle.querySelector('i').className = isOpen ? 'fas fa-times' : 'fas fa-folder-open';
            }
        }

        sidebarToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            toggleSidebar();
        });

        closeSidebar.addEventListener('click', function (e) {
            e.stopPropagation();
            if (sidebar.classList.contains('open')) {
                toggleSidebar();
            }
        });

        document.addEventListener('click', function (e) {
            if (sidebar.classList.contains('open') &&
                !sidebar.contains(e.target) &&
                e.target !== sidebarToggle &&
                !sidebarToggle.contains(e.target)) {
                toggleSidebar();
            }
        });

        sidebar.addEventListener('click', function (e) {
            e.stopPropagation();
        });
    }

    if (sidebar && sidebarToggle) {
        setupSidebar();
    }

    // ==============================================
    // Funciones del Chat
    // ==============================================

    function clearChatArea() {
        if (chatArea) {
            chatArea.innerHTML = '';
        }
    }

    function displayMessage(content, type, sentiment = null) {
        if (!chatArea) {
            console.error("Error: No se encontró el área de chat");
            return;
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        if (type === 'ai' && sentiment) {
            const sentimentIndicator = document.createElement('div');
            sentimentIndicator.className = `sentiment-${sentiment.toLowerCase()}`;
            sentimentIndicator.textContent = sentiment === 'POS' ? '😊 Positivo' : sentiment === 'NEG' ? '⚠️ Negativo' : '';
            messageDiv.appendChild(sentimentIndicator);
        }

        if (type === 'ai' && content.includes('imagen de')) {
            const contentDiv = document.createElement('div');
            contentDiv.textContent = content;
            messageDiv.appendChild(contentDiv);
        } else {
            const contentDiv = document.createElement('div');
            contentDiv.textContent = content;
            messageDiv.appendChild(contentDiv);
        }

        chatArea.appendChild(messageDiv);
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    function showTypingIndicator() {
        if (!chatArea) return;

        hideTypingIndicator();

        const typingDiv = document.createElement('div');
        typingDiv.id = 'typingIndicator';
        typingDiv.className = 'message ai-message typing';
        typingDiv.innerHTML = '<div class="typing-dots"><span>.</span><span>.</span><span>.</span></div>';

        chatArea.appendChild(typingDiv);
        chatArea.scrollTop = chatArea.scrollHeight;

        if (stopButton) {
            stopButton.style.display = 'inline-block';
        }

        isTyping = true;
    }

    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }

        if (stopButton) {
            stopButton.style.display = 'none';
        }

        isTyping = false;
    }

    function stopTyping() {
        hideTypingIndicator();
        displayMessage("Generación de respuesta detenida", 'system');
    }

    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        const closeBtn = document.createElement('span');
        closeBtn.innerHTML = '&times;';
        closeBtn.className = 'close-btn';
        closeBtn.onclick = function () {
            notification.remove();
        };

        notification.appendChild(closeBtn);
        document.body.appendChild(notification);

        setTimeout(() => {
            if (document.body.contains(notification)) {
                notification.remove();
            }
        }, 3000);
    }

    // ==============================================
    // Funciones para interactuar con el backend Python
    // ==============================================

    async function createNewChat() {
        try {
            const chatName = prompt('Nombre para el nuevo chat:') || `Chat ${new Date().toLocaleString()}`;

            // Limpiar el chat actual
            currentConversationId = null;
            clearChatArea();

            // Mostrar mensaje de bienvenida
            const welcomeMessage = `¡Nuevo chat "${chatName}" iniciado! ¿En qué puedo ayudarte hoy?`;
            displayMessage(welcomeMessage, 'ai');

            // Crear nueva conversación en el backend
            const response = await fetch(`${API_BASE_URL}/crear_conversacion`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ nombre_chat: chatName })
            });

            const data = await response.json();

            if (data.success) {
                currentConversationId = data.conversacion_id;
                console.log("Nueva conversación creada con ID:", currentConversationId);
                showNotification(`Chat "${chatName}" creado exitosamente`, "success");
            } else {
                throw new Error(data.error || "Error desconocido al crear chat");
            }

        } catch (error) {
            console.error('Error al crear nuevo chat:', error);
            showNotification("Error al crear nuevo chat", "error");
        }
    }

    async function sendMessageToBackend(message) {
        try {
            // Verificar si necesitamos crear una nueva conversación
            if (!currentConversationId) {
                await createNewChat();
                if (!currentConversationId) {
                    throw new Error("No se pudo crear una nueva conversación");
                }
            }

            // Mostrar mensaje del usuario
            displayMessage(message, 'user');

            // Guardar mensaje del usuario
            await fetch(`${API_BASE_URL}/guardar_mensaje`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    conversacion_id: currentConversationId,
                    contenido: message,
                    tipo: 'usuario'
                })
            });

            // Mostrar indicador de escritura
            showTypingIndicator();

            // Construir URL para obtener respuesta
            const params = new URLSearchParams();
            params.append('termino', message);

            // Ocultar indicador de escritura
            hideTypingIndicator();

            // Actualizar ID de conversación si viene en la respuesta
            if (currentConversationId) {
                params.append('conversacion_id', currentConversationId);
            }

            // Cambiar el fetch para incluir headers correctos
            const response = await fetch(`${API_BASE_URL}/obtener_info?${params.toString()}`, {
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });

            // Verificar si la respuesta es JSON válido
            let data;
            try {
                data = await response.json();
            } catch (jsonError) {
                console.error('Error parsing JSON:', jsonError);
                throw new Error('La respuesta no es JSON válido');
            }

            // Manejar diferentes tipos de respuestas
            if (data.tipo === 'imagen') {
                displayMessage(data.contenido, 'ai', data.sentimiento);

                // Agregar la imagen al mensaje
                setTimeout(() => {
                    const lastMessage = chatArea.lastElementChild;
                    const imgElement = document.createElement('img');
                    imgElement.src = `${API_BASE_URL}${data.imagen_url}`;
                    imgElement.alt = data.prompt || 'Imagen generada';
                    imgElement.className = 'response-image';
                    lastMessage.appendChild(imgElement);
                }, 100);

                // Leer automáticamente la respuesta si está configurado
                if (lastAudio === 'auto') {
                    textToSpeech(data.contenido_audio || data.contenido);
                }

            } else if (data.error) {
                displayMessage('No pude encontrar información sobre eso. ¿Puedes ser más específico?', 'ai');
            } else {
                displayMessage(data.contenido, 'ai', data.sentimiento);

                // Leer automáticamente la respuesta si está configurado
                if (lastAudio === 'auto') {
                    textToSpeech(data.contenido_audio || data.contenido);
                }
            }

        } catch (error) {
            console.error('Error al enviar mensaje:', error);
            hideTypingIndicator();
            displayMessage('Lo siento, ocurrió un error al procesar tu solicitud.', 'ai');
        }
    }

    async function textToSpeech(text, isAuto = false) {
        if (!text) return;

        try {
            // Detener cualquier audio anterior
            stopSpeech();

            // Mostrar botón de parar y ocultar botón de lectura
            if (readButton) readButton.style.display = 'none';
            if (stopSpeechButton) stopSpeechButton.style.display = 'inline-block';

            const url = `${API_BASE_URL}/hablar?texto=${encodeURIComponent(text)}&idioma=es&tld=es&rapido=false`;
            const response = await fetch(url);
            const data = await response.json();

            if (data.audioUrl) {
                const audio = new Audio(`${API_BASE_URL}${data.audioUrl}`);
                currentSpeech = audio;

                audio.onended = function () {
                    if (readButton) readButton.style.display = 'inline-block';
                    if (stopSpeechButton) stopSpeechButton.style.display = 'none';
                    currentSpeech = null;
                };

                audio.onerror = function () {
                    console.error('Error al reproducir audio');
                    if (readButton) readButton.style.display = 'inline-block';
                    if (stopSpeechButton) stopSpeechButton.style.display = 'none';
                    currentSpeech = null;
                };

                audio.play();
                lastAudio = isAuto ? 'auto' : 'manual';
            }
        } catch (error) {
            console.error('Error al convertir texto a voz:', error);
            if (readButton) readButton.style.display = 'inline-block';
            if (stopSpeechButton) stopSpeechButton.style.display = 'none';
        }
    }

    function stopSpeech() {
        if (currentSpeech) {
            currentSpeech.pause();
            currentSpeech.currentTime = 0;
            currentSpeech = null;
        }

        if (readButton) readButton.style.display = 'inline-block';
        if (stopSpeechButton) stopSpeechButton.style.display = 'none';
    }

    // ==============================================
    // Event Listeners
    // ==============================================

    if (sendButton) {
        sendButton.addEventListener('click', function () {
            const message = userInput.value.trim();
            if (message) {
                sendMessageToBackend(message);
                userInput.value = '';
            }
        });
    }

    if (userInput) {
        userInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                const message = userInput.value.trim();
                if (message) {
                    sendMessageToBackend(message);
                    userInput.value = '';
                }
            }
        });
    }

    if (stopButton) {
        stopButton.addEventListener('click', stopTyping);
    }

    if (readButton) {
        readButton.addEventListener('click', function () {
            const aiMessages = document.querySelectorAll('.ai-message');
            if (aiMessages.length > 0) {
                const lastAiMessage = aiMessages[aiMessages.length - 1];
                const text = lastAiMessage.textContent;
                textToSpeech(text);
            }
        });
    }

    if (stopSpeechButton) {
        stopSpeechButton.addEventListener('click', stopSpeech);
    }

    if (newChatButton) {
        newChatButton.addEventListener('click', createNewChat);
    }

    // Mensaje de bienvenida inicial
    window.addEventListener('load', function () {
        const welcomeMessage = "Bienvenido al asistente virtual. ¿En qué puedo ayudarte hoy?";
        displayMessage(welcomeMessage, 'ai');
    });
});

// Función global para detener la generación de respuesta
function stopTyping() {
    const stopButton = document.getElementById('stopButton');
    if (stopButton) {
        stopButton.style.display = 'none';
    }

    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }

    const chatArea = document.getElementById('chat');
    if (chatArea) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system-message';
        messageDiv.textContent = "Generación de respuesta detenida";
        chatArea.appendChild(messageDiv);
        chatArea.scrollTop = chatArea.scrollHeight;
    }
}