import json


def render_page(led_is_on):
    state = "BẬT" if led_is_on else "TẮT"
    button_label = "Tắt đèn" if led_is_on else "Bật đèn"
    button_class = "on" if led_is_on else "off"
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Điều khiển LED</title>
    <style>
        :root {{
            color-scheme: light;
            font-family: system-ui, sans-serif;
            background: #eef2f3;
            color: #182326;
        }}
        body {{
            display: grid;
            min-height: 100vh;
            margin: 0;
            place-items: center;
        }}
        main {{
            width: min(90vw, 430px);
            padding: 2rem;
            border: 1px solid #d3dcde;
            border-radius: 12px;
            background: white;
            box-shadow: 0 12px 30px #24363b1a;
            text-align: center;
        }}
        h1 {{ margin-top: 0; }}
        .lamp {{
            width: 96px;
            height: 96px;
            margin: 1.5rem auto;
            border-radius: 50%;
            background: #b9c2c4;
            box-shadow: inset 0 0 0 8px #ffffff80;
        }}
        .lamp.on {{
            background: #ffd166;
            box-shadow: 0 0 34px #ffd166, inset 0 0 0 8px #fff8;
        }}
        .state {{ font-weight: 700; }}
        button {{
            width: 100%;
            padding: .85rem 1rem;
            border: 0;
            border-radius: 8px;
            color: white;
            background: #157a6e;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 700;
        }}
        button:hover {{ background: #0f6158; }}
        button.on {{ background: #b64b36; }}
        .error {{ color: #b64b36; min-height: 1.5em; }}
    </style>
</head>
<body>
    <main>
        <h1>Đèn LED Raspberry Pi</h1>
        <div id="lamp" class="lamp {button_class}"></div>
        <p>Trạng thái: <span id="state" class="state">{state}</span></p>
        <button id="toggle" class="{button_class}" type="button">{button_label}</button>
        <p id="error" class="error" aria-live="polite"></p>
    </main>
    <script>
        const lamp = document.querySelector('#lamp');
        const state = document.querySelector('#state');
        const toggle = document.querySelector('#toggle');
        const error = document.querySelector('#error');

        function updateView(isOn) {{
            lamp.className = `lamp ${{isOn ? 'on' : 'off'}}`;
            state.textContent = isOn ? 'BẬT' : 'TẮT';
            toggle.className = isOn ? 'on' : 'off';
            toggle.textContent = isOn ? 'Tắt đèn' : 'Bật đèn';
        }}

        toggle.addEventListener('click', async () => {{
            toggle.disabled = true;
            error.textContent = '';
            try {{
                const response = await fetch('/api/led/toggle', {{ method: 'POST' }});
                if (!response.ok) throw new Error('Không thể điều khiển đèn');
                updateView((await response.json()).on);
            }} catch (requestError) {{
                error.textContent = requestError.message;
            }} finally {{
                toggle.disabled = false;
            }}
        }});
    </script>
</body>
</html>""".encode("utf-8")


def json_response(data):
    return json.dumps(data).encode("utf-8")