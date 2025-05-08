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


// Desplazamiento del minichatbot para que se vea al frente:
