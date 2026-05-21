<?php
declare(strict_types=1);

function h(string $value): string {
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function clean_preview_name(string $name): string {
    $name = str_replace('\\', '/', $name);
    $base = basename($name);
    $base = preg_replace('/[^A-Za-z0-9._-]/', '_', $base) ?? '';
    return trim($base, ". \t\n\r\0\x0B");
}

$file = clean_preview_name((string)($_GET['file'] ?? ''));
$exists = $file !== '' && is_file(__DIR__ . '/uploads/' . $file);
$src = $exists ? '/uploads/' . rawurlencode($file) : '';
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PicDrop - Preview</title>
    <style>
        :root { --bg:#eef5f9; --panel:#fff; --ink:#172331; --muted:#607085; --line:#d8e2ec; --accent:#1264a3; }
        * { box-sizing:border-box; }
        body { margin:0; min-height:100vh; background:linear-gradient(180deg,#f7fbfd 0%,var(--bg) 100%); color:var(--ink); font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; line-height:1.6; }
        .shell { width:min(960px,calc(100% - 32px)); margin:0 auto; padding:32px 0 56px; }
        header { display:flex; justify-content:space-between; align-items:center; margin-bottom:26px; }
        .brand { display:inline-flex; padding:0; border:0; background:transparent; font-weight:800; font-size:1.15rem; color:var(--ink); text-decoration:none; }
        .brand span { color:var(--accent); }
        main { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:24px; box-shadow:0 16px 36px rgba(31,58,88,.08); }
        .meta { color:var(--muted); margin:0 0 18px; overflow-wrap:anywhere; }
        h1 { margin:0 0 6px; font-size:2rem; letter-spacing:0; }
        .viewer { min-height:260px; display:grid; place-items:center; border:1px solid var(--line); border-radius:8px; background:#f8fbfd; overflow:hidden; }
        img { display:block; max-width:100%; max-height:520px; }
        .missing { color:var(--muted); padding:40px 16px; text-align:center; }
        a { display:inline-block; margin-top:18px; border:1px solid var(--line); border-radius:8px; padding:10px 14px; color:var(--ink); text-decoration:none; font-weight:800; background:#fff; }
    </style>
</head>
<body>
<div class="shell">
    <header>
        <a class="brand" href="/">Pic<span>Drop</span></a>
    </header>
    <main>
        <h1>Preview</h1>
        <?php if ($exists): ?>
            <p class="meta"><?= h($file) ?></p>
            <div class="viewer">
                <img src="<?= h($src) ?>" alt="uploaded preview">
            </div>
        <?php else: ?>
            <div class="viewer">
                <p class="missing">Preview file was not found.</p>
            </div>
        <?php endif; ?>
        <a href="/">Back to uploader</a>
    </main>
</div>
</body>
</html>
