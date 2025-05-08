// Variables globales
let isTyping = false; // Estado para saber si la IA está escribiendo
let typingInterval; // Intervalo de la animación de escritura
let isFirstMessage = true; // Bandera para saber si es el primer mensaje
let lastAiMessage = ""; // Almacena el último mensaje de la IA
let isSpeaking = false; // Estado para saber si la IA está hablando
let lastAudio = null; // Almacena el último audio generado
let lastAiAudio = ""; // Almacena la versión resumida para audio
let currentConversationId = null; // ID de la conversación actual

// Función que se ejecuta al cargar la página
document.addEventListener('DOMContentLoaded', function () {
    // Cargar el historial de conversaciones o crear uno nuevo
    initConversation();

    // Event listeners
    document.getElementById("userInput").addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            submitComment();
        }
    });

    document.getElementById("sendButton").addEventListener("click", submitComment);
    document.getElementById("readButton").addEventListener("click", readText);
    document.getElementById("stopSpeechButton").addEventListener("click", stopSpeech);
    document.getElementById("stopButton").addEventListener("click", stopTyping);
    document.getElementById("newChatButton").addEventListener("click", crearNuevoChat);

    // Event listeners para la barra lateral
    document.getElementById("sidebarToggle").addEventListener("click", toggleSidebar);
    document.getElementById("closeSidebar").addEventListener("click", closeSidebar);
});

// Función para inicializar la conversación
function initConversation() {
    // Intentamos cargar el historial de conversaciones
    cargarHistorialConversaciones()
        .then(success => {
            if (!success) {
                // Si no hay conversaciones o hubo un error, creamos una nueva
                crearNuevoChat();
            }
        });
}

// Función para cargar el historial de conversaciones
function cargarHistorialConversaciones() {
    return fetch('http://localhost:5001/conversaciones')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Error al cargar las conversaciones:', data.error);
                return false;
            }

            const chatHistory = document.getElementById('chatHistory');
            chatHistory.innerHTML = ''; // Limpiar el historial

            if (data.conversaciones && data.conversaciones.length > 0) {
                // Clasificar las conversaciones por período de tiempo
                const hoy = new Date();
                hoy.setHours(0, 0, 0, 0);
                
                const ayer = new Date(hoy);
                ayer.setDate(ayer.getDate() - 1);
                
                const ultimos7Dias = new Date(hoy);
                ultimos7Dias.setDate(ultimos7Dias.getDate() - 7);
                
                const ultimos30Dias = new Date(hoy);
                ultimos30Dias.setDate(ultimos30Dias.getDate() - 30);
                
                // Agrupar conversaciones por período
                const conversacionesPorPeriodo = {
                    hoy: [],
                    ayer: [],
                    ultimos7Dias: [],
                    ultimos30Dias: [],
                    anteriores: []
                };
                
                data.conversaciones.forEach(conv => {
                    const fechaConv = new Date(conv.fecha_creacion);
                    
                    if (fechaConv >= hoy) {
                        conversacionesPorPeriodo.hoy.push(conv);
                    } else if (fechaConv >= ayer) {
                        conversacionesPorPeriodo.ayer.push(conv);
                    } else if (fechaConv >= ultimos7Dias) {
                        conversacionesPorPeriodo.ultimos7Dias.push(conv);
                    } else if (fechaConv >= ultimos30Dias) {
                        conversacionesPorPeriodo.ultimos30Dias.push(conv);
                    } else {
                        conversacionesPorPeriodo.anteriores.push(conv);
                    }
                });
                
                // Mostrar conversaciones agrupadas
                const periodos = [
                    { id: 'hoy', nombre: 'Hoy' },
                    { id: 'ayer', nombre: 'Ayer' },
                    { id: 'ultimos7Dias', nombre: 'Últimos 7 días' },
                    { id: 'ultimos30Dias', nombre: 'Últimos 30 días' },
                    { id: 'anteriores', nombre: 'Anteriores' }
                ];
                
                periodos.forEach(periodo => {
                    const conversaciones = conversacionesPorPeriodo[periodo.id];
                    
                    // Solo crear la sección si hay conversaciones en este período
                    if (conversaciones.length > 0) {
                        // Crear encabezado de sección
                        const seccionHeader = document.createElement('div');
                        seccionHeader.classList.add('time-section-header');
                        seccionHeader.textContent = periodo.nombre;
                        chatHistory.appendChild(seccionHeader);
                        
                        // Crear las conversaciones de esta sección
                        conversaciones.forEach(conv => {
                            const chatItem = crearElementoChat(conv);
                            chatHistory.appendChild(chatItem);
                        });
                    }
                });

                // Si no hay conversación actual pero hay conversaciones disponibles, cargamos la primera
                if (!currentConversationId && data.conversaciones.length > 0) {
                    cargarMensajesConversacion(data.conversaciones[0].id);
                }

                return true;
            } else {
                // No hay conversaciones
                chatHistory.innerHTML = '<div class="no-chats">No hay chats guardados</div>';
                return false;
            }
        })
        .catch(error => {
            console.error('Error al cargar las conversaciones:', error);
            return false;
        });
}

// Función auxiliar para crear el elemento de chat individual
function crearElementoChat(conv) {
    const chatItem = document.createElement('div');
    chatItem.classList.add('chat-item');
    chatItem.dataset.chatId = conv.id; // Guardar el ID en el dataset para referencia fácil
    
    // Si es la conversación actual, marcarla como activa
    if (currentConversationId === conv.id) {
        chatItem.classList.add('active');
    }

    // Formatear la fecha para mostrarla de manera amigable
    const fecha = new Date(conv.fecha_creacion);
    const fechaFormateada = `${fecha.getDate()}/${fecha.getMonth() + 1}/${fecha.getFullYear()} ${fecha.getHours()}:${fecha.getMinutes().toString().padStart(2, '0')}`;

    // Usar un título predeterminado si no existe
    const titulo = conv.titulo || `Chat #${conv.id}`;

    // Crear un contenedor para el título y la fecha (izquierda)
    const infoContainer = document.createElement('div');
    infoContainer.classList.add('chat-info');
    infoContainer.innerHTML = `
        <div class="chat-title">${titulo}</div>
        <div class="chat-date">${fechaFormateada}</div>
    `;
    
    // Crear el botón de eliminar (derecha)
    const deleteButton = document.createElement('button');
    deleteButton.classList.add('delete-chat-btn');
    deleteButton.innerHTML = '🗑️';
    deleteButton.title = 'Eliminar conversación';
    
    // Agregar el evento para eliminar
    deleteButton.addEventListener('click', (e) => {
        e.stopPropagation(); // Evitar que se active el chat al hacer clic en eliminar
        eliminarConversacion(conv.id);
    });

    // Agregar los elementos al chat item
    chatItem.appendChild(infoContainer);
    chatItem.appendChild(deleteButton);

    // Evento para cargar los mensajes (clic en la parte del info)
    infoContainer.addEventListener('click', () => {
        // Remover la clase active de todos los chats
        document.querySelectorAll('.chat-item').forEach(item => {
            item.classList.remove('active');
        });

        // Añadir la clase active al chat seleccionado
        chatItem.classList.add('active');

        // Cargar los mensajes de esta conversación
        cargarMensajesConversacion(conv.id);
    });

    return chatItem;
}

// Función para eliminar una conversación
function eliminarConversacion(conversacionId) {
    if (confirm(`¿Estás seguro de que deseas eliminar esta conversación?`)) {
        fetch(`http://localhost:5001/eliminar_conversacion/${conversacionId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Error al eliminar la conversación:', data.error);
                return;
            }
            
            console.log('Conversación eliminada correctamente');
            
            // Si la conversación eliminada era la actual, limpiar el chat
            if (currentConversationId === conversacionId) {
                clearChat();
                currentConversationId = null;
                localStorage.removeItem('currentConversationId');
                
                // Mostrar mensaje indicando que el chat fue eliminado
                const chat = document.getElementById("chat");
                const messageDiv = document.createElement("div");
                messageDiv.classList.add("message", "system-message");
                messageDiv.textContent = "La conversación actual ha sido eliminada.";
                chat.appendChild(messageDiv);
            }
            
            // Recargar el historial de conversaciones
            cargarHistorialConversaciones()
                .then(success => {
                    if (success && !currentConversationId && document.querySelector('.chat-item')) {
                        // Si no hay conversación activa pero hay otras disponibles, cargamos la primera
                        const primerChat = document.querySelector('.chat-item');
                        primerChat.classList.add('active');
                        const chatId = parseInt(primerChat.dataset.chatId);
                        cargarMensajesConversacion(chatId);
                    }
                });
        })
        .catch(error => {
            console.error('Error al eliminar la conversación:', error);
            alert('Ocurrió un error al eliminar la conversación.');
        });
    }
}

// Función para cargar los mensajes de una conversación
function cargarMensajesConversacion(conversacionId) {
    currentConversationId = conversacionId;
    localStorage.setItem('currentConversationId', conversacionId);

    // Limpiar el chat actual
    clearChat();

    // Mostrar el cuadro de chat
    const chat = document.getElementById("chat");
    chat.classList.add("visible");
    isFirstMessage = false;

    fetch(`http://localhost:5001/mensajes/${conversacionId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Error al cargar los mensajes:', data.error);
                return;
            }

            // Variables para controlar el último mensaje de IA con audio
            let ultimoMensajeAI = null;

            // Mostrar los mensajes en el chat
            if (data.mensajes && data.mensajes.length > 0) {
                data.mensajes.forEach(msg => {
                    let messageDiv = document.createElement("div");
                    messageDiv.classList.add("message");

                    if (msg.tipo === 'usuario') {
                        messageDiv.classList.add("user-message");
                        messageDiv.textContent = msg.contenido;
                    } else if (msg.tipo === 'ai') {
                        messageDiv.classList.add("ai-message");

                        // Verificar si hay un indicador de sentimiento
                        if (msg.sentimiento) {
                            let sentimentIndicator = document.createElement("span");
                            sentimentIndicator.classList.add("sentiment-indicator");

                            if (msg.sentimiento === "POS") {
                                sentimentIndicator.classList.add("positive");
                                sentimentIndicator.textContent = "😊 Tono positivo";
                            } else if (msg.sentimiento === "NEG") {
                                sentimentIndicator.classList.add("negative");
                                sentimentIndicator.textContent = "⚠️ Tono negativo";
                            }

                            messageDiv.appendChild(sentimentIndicator);
                        }

                        // Verificar si el mensaje tiene una imagen asociada
                        if (msg.ruta_imagen) {
                            // Crear un contenedor para la imagen
                            let imgContainer = document.createElement("div");
                            imgContainer.classList.add("image-container");

                            // Crear la imagen
                            let img = document.createElement("img");
                            img.src = msg.ruta_imagen;
                            img.alt = "Imagen generada";
                            img.classList.add("ai-generated-image");

                            // Agregar un enlace para ver la imagen completa
                            let imgLink = document.createElement("a");
                            imgLink.href = msg.ruta_imagen;
                            imgLink.target = "_blank";
                            imgLink.appendChild(img);

                            imgContainer.appendChild(imgLink);
                            messageDiv.appendChild(imgContainer);
                        }

                        // Agregar el contenido del mensaje
                        let textContent = document.createElement("div");
                        textContent.classList.add("ai-text-content");
                        textContent.innerHTML = msg.contenido;
                        messageDiv.appendChild(textContent);

                        // Almacenar el último mensaje de la IA para reproducción de audio
                        lastAiMessage = msg.contenido;
                        lastAiAudio = msg.contenido;

                        // Si este mensaje tiene una ruta de audio, guardar para cargar después
                        if (msg.ruta_audio) {
                            ultimoMensajeAI = msg;
                        }
                    }

                    chat.appendChild(messageDiv);
                });

                // Cargar el audio del último mensaje de IA si existe
                if (ultimoMensajeAI && ultimoMensajeAI.ruta_audio) {
                    console.log("Cargando audio guardado:", ultimoMensajeAI.ruta_audio);
                    
                    // Si hay un audio anterior, detenerlo
                    if (lastAudio) {
                        lastAudio.pause();
                        lastAudio.currentTime = 0;
                    }
                    
                    // Crear un nuevo objeto de audio con la URL del archivo existente
                    lastAudio = new Audio(ultimoMensajeAI.ruta_audio);
                    
                    // Agregar un parámetro de caché único para evitar problemas de caché
                    lastAudio.src = `${ultimoMensajeAI.ruta_audio}?t=${new Date().getTime()}`;
                }

                // Desplazar el chat hacia abajo
                chat.scrollTop = chat.scrollHeight;
            }
        })
        .catch(error => {
            console.error('Error al cargar los mensajes:', error);
        });
}

function crearNuevoChat() {
    // Preguntar al usuario por el nombre del chat
    const titulo = prompt("¿Cómo quieres nombrar este nuevo chat?") || "Nuevo chat";

    // Limpiar el chat actual
    clearChat();

    // Crear una nueva conversación en el backend con el título proporcionado
    fetch('http://localhost:5001/crear_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            titulo: titulo
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Error al crear nuevo chat:', data.error);
                return;
            }

            // Establecer la nueva conversación como la actual
            currentConversationId = data.conversacion_id;
            localStorage.setItem('currentConversationId', currentConversationId);

            // Actualizar el historial de conversaciones
            cargarHistorialConversaciones();

            console.log('Nuevo chat creado con ID:', currentConversationId);
        })
        .catch(error => {
            console.error('Error al crear nuevo chat:', error);
            currentConversationId = 'temp_' + Date.now();
            console.log('ID temporal creada para continuar:', currentConversationId);
        });
}


// Función para limpiar el chat
function clearChat() {
    let chat = document.getElementById("chat");
    chat.innerHTML = ""; // Elimina todos los mensajes del chat
    lastAiMessage = ""; // Limpiar el último mensaje almacenado
    if (lastAudio) {
        lastAudio.pause(); // Detener el audio si está reproduciéndose
        lastAudio = null;
    }
}

// Función para animar la escritura de un mensaje
function typeMessage(message, element, callback) {
    let text = "";
    let index = 0;
    typingInterval = setInterval(() => {
        if (index < message.length) {
            text += message.charAt(index);
            element.innerHTML = text; // Usar innerHTML para mantener el formato
            index++;
        } else {
            clearInterval(typingInterval);
            isTyping = false;
            if (callback) callback(); // Llamar al callback si está definido
        }
    }, 30); // Velocidad de escritura (30ms por letra)
}

// Función para alternar la barra lateral
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
}

// Función para cerrar la barra lateral
function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.remove('open');
}

// Función para enviar un mensaje
function submitComment() {
    let input = document.getElementById("userInput");
    let chat = document.getElementById("chat");

    if (input.value.trim() !== "" && !isTyping) {
        // Verificar si tenemos una conversación activa
        if (!currentConversationId) {
            crearNuevoChat();
            setTimeout(() => {
                submitComment(); // Reintentamos después de crear la conversación
            }, 1000);
            return;
        }

        // Mostrar el cuadro de chat si es el primer mensaje
        if (isFirstMessage) {
            chat.classList.add("visible"); // Añade la clase para mostrar el chat
            isFirstMessage = false; // Cambia la bandera para que no se repita
        }

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

        // Construir la URL para la solicitud, manejando IDs temporales
        let apiUrl = `http://localhost:5001/obtener_info?termino=${encodeURIComponent(input.value)}`;
        if (currentConversationId && !currentConversationId.toString().startsWith('temp_')) {
            apiUrl += `&conversacion_id=${currentConversationId}`;
        }

        // Hacer una solicitud al backend de Flask
        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    // Si el error es por falta de conversación, crear una nueva
                    if (data.code === "NO_CONVERSATION_ID" || data.code === "INVALID_CONVERSATION_ID") {
                        crearNuevoChat();
                        // Volver a intentar después de crear la nueva conversación
                        setTimeout(() => {
                            submitComment();
                        }, 1000);
                        return;
                    }
                    throw new Error(data.error);
                }

                // Almacenar el último mensaje de la IA
                lastAiMessage = data.contenido;

                // Generar una respuesta de la IA
                let aiMessage = document.createElement("div");
                aiMessage.classList.add("message", "ai-message");

                // Verificar si la respuesta contiene una imagen
                if (data.tipo === "imagen" && data.imagen_url) {
                    // Crear un contenedor para el texto y la imagen
                    let textContent = document.createElement("div");
                    textContent.classList.add("ai-text-content");

                    // Añadir la imagen
                    let imgContainer = document.createElement("div");
                    imgContainer.classList.add("image-container");

                    let img = document.createElement("img");
                    img.src = data.imagen_url;
                    img.alt = data.prompt || "Imagen generada";
                    img.classList.add("ai-generated-image");

                    // Añadir un enlace para ver la imagen completa
                    let imgLink = document.createElement("a");
                    imgLink.href = data.imagen_url;
                    imgLink.target = "_blank";
                    imgLink.appendChild(img);

                    imgContainer.appendChild(imgLink);
                    aiMessage.appendChild(imgContainer);

                    // Añadir el texto debajo de la imagen
                    aiMessage.appendChild(textContent);

                    // Mostrar el texto con animación de escritura
                    typeMessage(data.contenido, textContent, () => {
                        input.disabled = false;
                        document.getElementById("sendButton").style.display = "inline-block";
                        document.getElementById("stopButton").style.display = "none";
                    });
                } else {
                    // Añadir indicador de sentimiento si está disponible
                    if (data.sentimiento) {
                        let sentimentIndicator = document.createElement("span");
                        sentimentIndicator.classList.add("sentiment-indicator");

                        if (data.sentimiento === "POS") {
                            sentimentIndicator.classList.add("positive");
                            sentimentIndicator.textContent = "😊 Tono positivo";
                        } else if (data.sentimiento === "NEG") {
                            sentimentIndicator.classList.add("negative");
                            sentimentIndicator.textContent = "⚠️ Tono negativo";
                        }

                        aiMessage.appendChild(sentimentIndicator);
                    }

                    // Mostrar la respuesta con animación de escritura para mensajes normales
                    typeMessage(data.contenido, aiMessage, () => {
                        input.disabled = false;
                        document.getElementById("sendButton").style.display = "inline-block";
                        document.getElementById("stopButton").style.display = "none";
                    });
                }

                chat.appendChild(aiMessage);

                // Modifica la llamada fetch para incluir el conversacion_id
                fetch(`http://localhost:5001/hablar?texto=${encodeURIComponent(data.contenido_audio || data.contenido)}&conversacion_id=${data.conversacion_id}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`Error HTTP: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(audioData => {
                        if (audioData.error) {
                            throw new Error(audioData.error);
                        }
                        // Detener el audio anterior si está reproduciéndose
                        if (lastAudio) {
                            lastAudio.pause();
                            lastAudio.currentTime = 0;
                        }
                        // Crear un nuevo objeto de audio con la URL del archivo sobrescrito
                        lastAudio = new Audio(audioData.audioUrl);
                        // Agregar un parámetro de caché único para evitar problemas de caché
                        lastAudio.src = `${audioData.audioUrl}?t=${new Date().getTime()}`;

                        // Almacenar la versión para audio (diferente del texto mostrado)
                        lastAiAudio = data.contenido_audio || data.contenido;
                    })
                    .catch(error => {
                        console.error("Error al generar el audio:", error);
                    });
            })
            .catch(error => {
                console.error('Error:', error);
                // Mostrar un mensaje de error en caso de fallo
                let aiMessage = document.createElement("div");
                aiMessage.classList.add("message", "ai-message");
                chat.appendChild(aiMessage);

                // Mostrar el mensaje de error con animación de escritura
                typeMessage("Hubo un error al procesar tu solicitud. Inténtalo de nuevo.", aiMessage, () => {
                    input.disabled = false; // Habilitar el input cuando la IA termina de escribir
                    document.getElementById("sendButton").style.display = "inline-block";
                    document.getElementById("stopButton").style.display = "none";
                });
            });

        // Limpiar el campo de entrada
        input.value = "";

        // Desplazar el chat hacia abajo
        chat.scrollTop = chat.scrollHeight;
    }
}

// Función para leer el último mensaje de la IA
function readText() {
    if (lastAudio && lastAiAudio.trim() !== "") {
        if (!isSpeaking) {
            // Cambiar el botón "Leer" a "Parar"
            document.getElementById("readButton").style.display = "none";
            document.getElementById("stopSpeechButton").style.display = "inline-block";
            isSpeaking = true;

            // Reproducir el audio
            lastAudio.play();

            // Cuando termine de hablar, cambiar el botón de nuevo a "Leer"
            lastAudio.onended = () => {
                document.getElementById("readButton").style.display = "inline-block";
                document.getElementById("stopSpeechButton").style.display = "none";
                isSpeaking = false;
            };
        }
    } else {
        alert("No hay texto para leer o el audio no está disponible.");
    }
}

// Función para detener la reproducción de voz
function stopSpeech() {
    if (isSpeaking && lastAudio) {
        lastAudio.pause(); // Detener la reproducción
        lastAudio.currentTime = 0; // Reiniciar el audio
        document.getElementById("readButton").style.display = "inline-block";
        document.getElementById("stopSpeechButton").style.display = "none";
        isSpeaking = false;
    }
}

// Función para detener la animación de escritura
function stopTyping() {
    if (isTyping) {
        clearInterval(typingInterval); // Detener la animación de escritura
        isTyping = false;
        document.getElementById("userInput").disabled = false; // Habilitar el input
        document.getElementById("sendButton").style.display = "inline-block";
        document.getElementById("stopButton").style.display = "none";
    }
}