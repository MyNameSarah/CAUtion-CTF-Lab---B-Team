<?php
declare(strict_types=1);

function h(string $value): string {
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function clean_original_name(string $name): string {
    $name = str_replace('\\', '/', $name);
    $base = basename($name);
    $base = preg_replace('/[^A-Za-z0-9._-]/', '_', $base) ?? '';
    $base = trim($base, ". \t\n\r\0\x0B");
    return $base !== '' ? $base : 'upload.bin';
}

function last_extension(string $name): string {
    $ext = pathinfo($name, PATHINFO_EXTENSION);
    return $ext === '' ? '' : '.' . strtolower($ext);
}

$allowedTypes = [
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/gif',
];

$blockedExtensions = [
    '.php',
    '.php3',
    '.php4',
    '.php5',
    '.php7',
    '.pht',
    '.phps',
    '.phar',
    '.phpt',
    '.pgif',
    '.phtml',
    '.inc',
];

$message = '';
$previewFile = null;
$ok = false;

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    $message = 'Only POST uploads are accepted.';
} elseif (!isset($_FILES['file']) || !is_array($_FILES['file'])) {
    http_response_code(400);
    $message = 'No file was uploaded.';
} elseif ($_FILES['file']['error'] !== UPLOAD_ERR_OK) {
    http_response_code(400);
    $message = 'Upload failed. Please try another file.';
} else {
    $clientType = (string)($_FILES['file']['type'] ?? '');
    if (!in_array($clientType, $allowedTypes, true)) {
        http_response_code(400);
        $message = 'Only common image Content-Type values are accepted.';
    } else {
        $original = clean_original_name((string)$_FILES['file']['name']);
        $ext = last_extension($original);

        if (in_array($ext, $blockedExtensions, true)) {
            http_response_code(400);
            $message = 'This file extension is not allowed.';
        } else {
            $token = bin2hex(random_bytes(8));
            $storedName = $token . '_' . $original;
            $uploadDir = __DIR__ . '/uploads';
            $targetPath = $uploadDir . '/' . $storedName;

            if (!is_dir($uploadDir)) {
                mkdir($uploadDir, 0755, true);
            }

            if (!move_uploaded_file($_FILES['file']['tmp_name'], $targetPath)) {
                http_response_code(500);
                $message = 'The server could not store the upload.';
            } else {
                chmod($targetPath, 0644);
                $message = 'Upload complete. Your preview page is ready.';
                $previewFile = $storedName;
                $ok = true;
            }
        }
    }
}
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PicDrop - Upload Result</title>
    <style>
        :root { --bg:#eef5f9; --panel:#fff; --ink:#172331; --muted:#607085; --line:#d8e2ec; --accent:#1264a3; --danger:#a33a3a; --ok:#0f7b66; }
        * { box-sizing: border-box; }
        body { margin:0; min-height:100vh; background:linear-gradient(180deg,#f7fbfd 0%,var(--bg) 100%); color:var(--ink); font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; line-height:1.6; }
        .shell { width:min(760px,calc(100% - 32px)); margin:0 auto; padding:32px 0 56px; }
        header { display:flex; justify-content:space-between; align-items:center; margin-bottom:28px; }
        .brand { display:inline-flex; padding:0; border:0; background:transparent; font-weight:800; font-size:1.15rem; color:var(--ink); text-decoration:none; }
        .brand span { color:var(--accent); }
        main { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:30px; box-shadow:0 16px 36px rgba(31,58,88,.08); }
        .status { display:inline-block; border-radius:999px; padding:5px 10px; margin-bottom:14px; background:<?= $ok ? '#e7f6f1' : '#faeeee' ?>; color:<?= $ok ? 'var(--ok)' : 'var(--danger)' ?>; font-weight:800; font-size:.88rem; }
        h1 { margin:0 0 12px; font-size:2rem; letter-spacing:0; }
        p { color:var(--muted); }
        .actions { display:flex; gap:12px; flex-wrap:wrap; margin-top:22px; }
        a { display:inline-block; border-radius:8px; padding:10px 14px; text-decoration:none; font-weight:800; }
        .primary { background:var(--accent); color:#fff; }
        .secondary { border:1px solid var(--line); color:var(--ink); background:#fff; }
    </style>
</head>
<body>
<div class="shell">
    <header>
        <a class="brand" href="/">Pic<span>Drop</span></a>
    </header>
    <main>
        <div class="status"><?= $ok ? 'Stored' : 'Needs attention' ?></div>
        <h1>Upload result</h1>
        <p><?= h($message) ?></p>
        <div class="actions">
            <?php if ($previewFile !== null): ?>
                <a class="primary" href="/preview.php?file=<?= rawurlencode($previewFile) ?>">Open preview</a>
            <?php endif; ?>
            <a class="secondary" href="/">Back to uploader</a>
        </div>
    </main>
</div>
</body>
</html>
