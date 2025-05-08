<?php
require_once 'db_connection.php';

header('Content-Type: application/json');

// Obtener datos del cuerpo de la solicitud
$data = json_decode(file_get_contents('php://input'), true);

try {
    $db = Database::getInstance();
    $conn = $db->getConnection();
    
    // Validar que se recibió el nombre del chat
    if (!isset($data['chat_name']) || empty(trim($data['chat_name']))) {
        throw new Exception('El nombre del chat es requerido');
    }
    
    $chatName = trim($data['chat_name']);
    
    $stmt = $conn->prepare("INSERT INTO conversaciones (nombre) VALUES (?)");
    $stmt->bind_param("s", $chatName);
    
    if ($stmt->execute()) {
        echo json_encode([
            'success' => true, 
            'chat_id' => $conn->insert_id,
            'nombre' => $chatName,
            'fecha_creacion' => date('Y-m-d H:i:s')
        ]);
    } else {
        throw new Exception("Error al crear el chat: " . $stmt->error);
    }
    
    $stmt->close();
} catch (Exception $e) {
    echo json_encode([
        'success' => false, 
        'error' => $e->getMessage()
    ]);
}
?>