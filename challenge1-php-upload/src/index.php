<?php
declare(strict_types=1);
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PicDrop - Image Preview Upload</title>
    <style>
        :root {
            --bg: #eef5f9;
            --panel: #ffffff;
            --ink: #172331;
            --muted: #607085;
            --line: #d8e2ec;
            --accent: #1264a3;
            --accent-2: #0f9f8f;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            min-height: 100vh;
            background: linear-gradient(180deg, #f7fbfd 0%, var(--bg) 100%);
            color: var(--ink);
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            line-height: 1.6;
        }
        .shell { width: min(960px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 56px; }
        header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 34px; }
        .brand { font-weight: 800; font-size: 1.2rem; letter-spacing: 0; color: var(--ink); text-decoration: none; }
        .brand span { color: var(--accent); }
        .badge { border: 1px solid var(--line); background: #fff; color: var(--muted); border-radius: 999px; padding: 6px 12px; font-size: .88rem; }
        main { display: grid; grid-template-columns: 1.15fr .85fr; gap: 24px; align-items: stretch; }
        .intro, .panel {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: 0 16px 36px rgba(31, 58, 88, .08);
        }
        .intro { padding: 34px; }
        .panel { padding: 26px; }
        h1 { margin: 0 0 14px; font-size: clamp(2rem, 4vw, 3.2rem); line-height: 1.08; letter-spacing: 0; }
        h2 { margin: 0 0 14px; font-size: 1.15rem; }
        p { margin: 0 0 16px; color: var(--muted); }
        .list { display: grid; gap: 10px; margin-top: 24px; }
        .list div { border-left: 3px solid var(--accent-2); padding-left: 12px; color: #334155; }
        label { display: block; margin-bottom: 10px; font-weight: 700; }
        input[type="file"] {
            width: 100%;
            border: 1px dashed #9bb4c8;
            border-radius: 8px;
            padding: 16px;
            background: #f8fbfd;
        }
        button {
            width: 100%;
            margin-top: 18px;
            border: 0;
            border-radius: 8px;
            padding: 12px 16px;
            background: var(--accent);
            color: #fff;
            font-weight: 800;
            cursor: pointer;
        }
        button:hover { background: #0e568d; }
        .small { margin-top: 16px; font-size: .92rem; color: var(--muted); }
        @media (max-width: 760px) {
            main { grid-template-columns: 1fr; }
            header { align-items: flex-start; gap: 12px; flex-direction: column; }
        }
    </style>
</head>
<body>
<div class="shell">
    <header>
        <a class="brand" href="/">Pic<span>Drop</span></a>
        <div class="badge">Private image preview workspace</div>
    </header>
    <main>
        <section class="intro">
            <h1>Upload a quick image preview.</h1>
            <p>PicDrop prepares lightweight image previews for small team notes, drafts, and design handoffs.</p>
            <div class="list">
                <div>Common image uploads are accepted.</div>
                <div>Each file gets a short preview page.</div>
                <div>Links are local to this study environment.</div>
            </div>
        </section>
        <section class="panel">
            <h2>New preview</h2>
            <form action="/upload.php" method="post" enctype="multipart/form-data">
                <label for="file">Image file</label>
                <input id="file" name="file" type="file" required>
                <button type="submit">Upload image</button>
            </form>
            <p class="small">Supported preview types: JPEG, PNG, and GIF.</p>
        </section>
    </main>
</div>
</body>
</html>
