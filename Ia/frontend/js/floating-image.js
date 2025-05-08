const floatingImage = document.getElementById('floatingImage');
const miniChat = document.getElementById('miniChat');

// Mensajes del asistente (ampliados)
const tipsGenerales = [
    "🔐 Mantén tus credenciales seguras y cámbialas periódicamente",
    "⚠️ Sé cauteloso al compartir información personal",
    "💡 Activa siempre las medidas de seguridad adicionales",
    "🛡️ Usa herramientas de protección confiables",
    "🔍 Verifica la autenticidad antes de interactuar",
    "📱 Mantén tu software actualizado",
    "🔒 Protege tus datos en conexiones públicas",
    "📧 Desconfía de mensajes sospechosos",
    "💾 Haz respaldos regulares de tu información",
    "🚫 Evita fuentes no oficiales",
    "👥 Administra cuidadosamente los permisos",
    "📲 Bloquea tus dispositivos cuando no los uses",
    "🔎 Usa modos seguros para operaciones importantes",
    "📛 Nunca compartas códigos de seguridad"
];
let lastTipIndex = -1; // Para controlar la última frase mostrada

// Mostrar un único mensaje aleatorio no repetido
function showRandomTip() {
    // Limpiar chat anterior
    miniChat.innerHTML = '';
    
    // Seleccionar mensaje aleatorio que no sea el último mostrado
    let randomIndex;
    do {
        randomIndex = Math.floor(Math.random() * tipsSeguridad.length);
    } while (randomIndex === lastTipIndex && tipsSeguridad.length > 1);
    
    lastTipIndex = randomIndex;
    const randomTip = tipsSeguridad[randomIndex];
    
    // Crear elemento de mensaje
    const tipElement = document.createElement('div');
    tipElement.className = 'mini-message';
    tipElement.textContent = randomTip;
    
    // Añadir al mini-chat
    miniChat.appendChild(tipElement);
    miniChat.classList.add('mini-visible');
    
    
}

// Interacción
floatingImage.addEventListener('click', (e) => {
    e.stopPropagation();
    showRandomTip();
});

// Cerrar al hacer clic fuera
document.addEventListener('click', () => {
    miniChat.classList.remove('mini-visible');
});

// Efecto hover
floatingImage.addEventListener('mouseenter', () => {
    floatingImage.style.transform = 'scale(1.1)';
});

floatingImage.addEventListener('mouseleave', () => {
    floatingImage.style.transform = 'scale(1)';
});