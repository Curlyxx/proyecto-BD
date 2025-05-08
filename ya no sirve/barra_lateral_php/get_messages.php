<?php
require_once 'db_connection.php';

header('Content-Type: application/json');

if (!isset($_GET['chat_id'])) {
    echo json_encode(['success' => false, 'error' => 'chat_id no proporcionado']);
    exit;
}

try {
    $db = Database::getInstance();
    $conn = $db->getConnection();
    
    $stmt = $conn->prepare("SELECT contenido as content, tipo as type, sentimiento as sentiment FROM mensajes WHERE conversacion_id = ? ORDER BY fecha_creacion ASC");
    $stmt->bind_param("i", $_GET['chat_id']);
    $stmt->execute();
    $result = $stmt->get_result();
    
    $messages = $result->fetch_all(MYSQLI_ASSOC);
    echo json_encode(['success' => true, 'messages' => $messages]);
} catch (Exception $e) {
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
}
?>