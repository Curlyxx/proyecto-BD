<?php
require_once 'db_connection.php';

header('Content-Type: application/json');

$data = json_decode(file_get_contents('php://input'), true);

if (!isset($data['chat_id'])) {
    echo json_encode(['success' => false, 'error' => 'chat_id no proporcionado']);
    exit;
}

try {
    $db = Database::getInstance();
    $conn = $db->getConnection();
    
    $stmt = $conn->prepare("DELETE FROM conversaciones WHERE id = ?");
    $stmt->bind_param("i", $data['chat_id']);
    $success = $stmt->execute();
    
    echo json_encode(['success' => $success, 'affected_rows' => $stmt->affected_rows]);
} catch (Exception $e) {
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
}
?>