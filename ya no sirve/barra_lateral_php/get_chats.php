<?php
require_once 'db_connection.php';

header('Content-Type: application/json');

try {
    $db = Database::getInstance();
    $conn = $db->getConnection();
    
    $stmt = $conn->query("SELECT id, nombre, fecha_creacion FROM conversaciones ORDER BY fecha_creacion DESC");
    $chats = $stmt->fetch_all(MYSQLI_ASSOC);
    
    echo json_encode(['success' => true, 'chats' => $chats]);
} catch (Exception $e) {
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
}
?>