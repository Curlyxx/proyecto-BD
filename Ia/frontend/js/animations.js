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

// Crear figuras animadas cada 500ms
setInterval(createShape, 500);


// Agrega este código JavaScript a tu archivo JS o en una etiqueta <script> al final de tu HTML

// Función para desplazarse al fondo del chat
function scrollToBottom() {
    // Opción 1: Desplazarse al fondo de la ventana
    window.scrollTo(0, document.body.scrollHeight);
    
    // Opción 2: Si tienes un contenedor específico para el chat
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Opción 3: Si usas un div con id="chat"
    const chat = document.getElementById('chat');
    if (chat) {
        chat.scrollTop = chat.scrollHeight;
    }
}

// Ejecutar cuando la página se carga completamente
window.addEventListener('load', scrollToBottom);

// Ejecutar también cuando se agrega un nuevo mensaje (si tienes esa funcionalidad)
function scrollAfterNewMessage() {
    setTimeout(scrollToBottom, 100); // Pequeño retraso para asegurar que el contenido se ha renderizado
}

// Ejemplo: si tienes un botón de enviar con id="sendButton"
// document.getElementById('sendButton').addEventListener('click', scrollAfterNewMessage);