<?php
include 'conexion.php';

$termino = $_GET['termino'];

$stmt = $conn->prepare("SELECT definicion FROM conceptos WHERE termino LIKE :termino");
$stmt->execute(['termino' => "%$termino%"]);

$resultado = $stmt->fetch(PDO::FETCH_ASSOC);

if ($resultado) {
    echo $resultado['definicion'];
} else {
    echo "Lo siento, no tengo información sobre ese término.";
}
?>