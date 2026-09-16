import json


def render_page(is_on):
    state = "BẬT" if is_on else "TẮT"
    action = "Tắt đèn" if is_on else "Bật đèn"
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LED Control</title>
    <style>
        :root {{ font-family: system-ui, sans-serif; color: #182326; background: #eef2f3; }}
        body {{ display: grid; min-height: 100vh; margin: 0; place-items: center; }}
        main {{ width: min(90vw, 360px); padding: 2rem; border: 1px solid #d3dcde; border-radius: 12px; background: white; text-align: center; box-shadow: 0 12px 30px #24363b1a; }}
        .lamp {{ width: 110px; height: 110px; margin: 1.5rem auto; border-radius: 50%; background: #b9c2c4; }}
        .lamp.on {{ background: #ffd166; box-shadow: 0 0 36px #ffd166; }}
        .state {{ font-weight: 700; }}
        button {{ width: 100%; padding: .8rem; border: 0; border-radius: 8px; color: white; background: #157a6e; cursor: pointer; font: inherit; font-weight: 700; }}
        button.on {{ background: #b64b36; }}
        button:disabled {{ cursor: wait; opacity: .65; }}
        .error {{ min-height: 1.4em; color: #b64b36; }}
    </style>
</head>
<body>
    <main>
        <h1>LED Control</h1>
        <div id="lamp" class="lamp {"on" if is_on else "off"}"></div>
        <p>Trạng thái: <span id="state" class="state">{state}</span></p>
        <button id="toggle" class="{"on" if is_on else ""}" type="button">{action}</button>
        <p id="error" class="error" aria-live="polite"></p>
    </main>
    <script>
        const lamp = document.querySelector('#lamp');
        const state = document.querySelector('#state');
        const button = document.querySelector('#toggle');
        const error = document.querySelector('#error');

        function updateView(isOn) {{
            lamp.className = `lamp ${{isOn ? 'on' : 'off'}}`;
            state.textContent = isOn ? 'BẬT' : 'TẮT';
            button.className = isOn ? 'on' : '';
            button.textContent = isOn ? 'Tắt đèn' : 'Bật đèn';
        }}

        button.addEventListener('click', async () => {{
            button.disabled = true;
            error.textContent = '';
            try {{
                const response = await fetch('/api/simple-led/toggle', {{ method: 'POST' }});
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Không thể điều khiển đèn');
                updateView(data.on);
            }} catch (requestError) {{
                error.textContent = requestError.message;
            }} finally {{
                button.disabled = false;
            }}
        }});
    </script>
</body>
</html>""".encode("utf-8")


def json_response(data):
    return json.dumps(data, ensure_ascii=False).encode("utf-8")
