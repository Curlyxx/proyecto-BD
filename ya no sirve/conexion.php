<?php
$host = 'localhost';
$dbname = 'seguridad';
$username = 'root'; // Usuario por defecto de XAMPP
$password = ''; // Contraseña por defecto de XAMPP (vacía)

try {
    $conn = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    echo "Error de conexión: " . $e->getMessage();
}
?>