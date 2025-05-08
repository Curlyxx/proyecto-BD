<?php
// backend/wikipedia.php
$termino = $_GET['termino']; // Obtén la consulta del usuario

// URL de la API de Wikipedia en español para buscar el término
$searchUrl = "https://es.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch=" . urlencode($termino);

// Realiza la solicitud a la API para buscar el término
$searchResponse = file_get_contents($searchUrl);

// Verifica si la solicitud fue exitosa
if ($searchResponse === FALSE) {
    echo "Hubo un error al conectarse con la API de Wikipedia.";
    exit;
}

$searchData = json_decode($searchResponse, true);

// Verifica si hay resultados
if (!empty($searchData['query']['search'])) {
    $primerResultado = $searchData['query']['search'][0];
    $titulo = $primerResultado['title'];

    // URL de la API de Wikipedia para obtener el contenido completo del artículo
    $contentUrl = "https://es.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=true&explaintext=true&titles=" . urlencode($titulo);

    // Realiza la solicitud a la API para obtener el contenido
    $contentResponse = file_get_contents($contentUrl);

    // Verifica si la solicitud fue exitosa
    if ($contentResponse === FALSE) {
        echo "Hubo un error al obtener el contenido del artículo.";
        exit;
    }

    $contentData = json_decode($contentResponse, true);

    // Obtiene el contenido del artículo
    $page = current($contentData['query']['pages']); // Obtiene la primera página
    $contenido = $page['extract'];

    // Limpiar el contenido: eliminar corchetes con números [1], [2], etc.
    $contenido = preg_replace('/\[\d+\]/', '', $contenido);

    // Muestra el título y el contenido del artículo
    echo "<strong>$titulo</strong><br>";
    echo $contenido;
} else {
    echo "Lo siento, no encontré información sobre ese término, especifica solo terminos.";
}
?>