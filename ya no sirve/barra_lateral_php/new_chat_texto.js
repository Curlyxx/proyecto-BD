// Función para crear nuevo chat
async function createNewChat() {
    try {
        // Pedir nombre del chat solo una vez
        const chatName = prompt('Nombre para el nuevo chat:');
        if (!chatName || chatName.trim() === '') return;

        const response = await fetch('http://localhost/ia2/Ia/backend/barra_lateral_php/create_chat.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ chat_name: chatName })
        });

        const data = await response.json();

        if (data.success) {
            // Formatear la fecha correctamente para mostrarla
            const formattedDate = formatDate(data.fecha_creacion);
            addChatToSidebar(data.chat_id, chatName, formattedDate); // Usamos chatName directamente
            clearChatArea();
            currentChatId = data.chat_id;

            // Mostrar alerta verde con botón de cierre
            const successAlert = document.createElement('div');
            successAlert.textContent = '✅ Nuevo chat creado correctamente';
            successAlert.style.position = 'fixed';
            successAlert.style.top = '20px';
            successAlert.style.right = '20px';
            successAlert.style.padding = '10px 15px 10px 15px';
            successAlert.style.backgroundColor = '#d4edda';
            successAlert.style.color = '#155724';
            successAlert.style.border = '1px solid #c3e6cb';
            successAlert.style.borderRadius = '5px';
            successAlert.style.zIndex = '9999';
            successAlert.style.boxShadow = '0 2px 6px rgba(0,0,0,0.1)';
            successAlert.style.display = 'flex';
            successAlert.style.alignItems = 'center';
            successAlert.style.justifyContent = 'space-between';
            successAlert.style.minWidth = '260px';
            successAlert.style.gap = '10px';

            // Botón de cierre (X)
            const closeBtn = document.createElement('span');
            closeBtn.textContent = '✖';
            closeBtn.style.cursor = 'pointer';
            closeBtn.style.marginLeft = 'auto';
            closeBtn.style.fontWeight = 'bold';
            closeBtn.addEventListener('click', () => successAlert.remove());

            successAlert.appendChild(closeBtn);
            document.body.appendChild(successAlert);

            // Eliminar automáticamente después de 3 segundos si no se cierra manualmente
            setTimeout(() => {
                if (document.body.contains(successAlert)) {
                    successAlert.remove();
                }
            }, 3000);
        } else {
            throw new Error(data.error || 'Error al crear chat');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al crear chat: ' + error.message);
        return false;
    }
}

// Función para formatear la fecha
function formatDate(dateString) {
    const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    };
    return new Date(dateString).toLocaleString('es-ES', options);
}