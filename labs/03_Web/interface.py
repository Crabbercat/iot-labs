import json


def render_page(led_states, weather=None):
    weather = weather or {}
    initial_weather = json.dumps(weather, ensure_ascii=False)
    initial_leds = json.dumps(led_states)
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Raspberry Pi IoT Controller</title>
    <style>
        :root {{
            color-scheme: light;
            font-family: system-ui, sans-serif;
            background: #eef2f3;
            color: #182326;
        }}
        body {{ margin: 0; padding: 2rem 1rem; }}
        main {{ max-width: 760px; margin: auto; }}
        h1 {{ margin-top: 0; }}
        .grid {{ display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
        section {{ padding: 1.25rem; border: 1px solid #d3dcde; border-radius: 12px; background: white; box-shadow: 0 12px 30px #24363b1a; }}
        dl {{ display: grid; grid-template-columns: 1fr 1fr; gap: .6rem; margin: 0; }}
        dt {{ color: #5b696c; }}
        dd {{ margin: 0; font-weight: 700; text-align: right; }}
        .led {{ display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: .8rem 0; border-bottom: 1px solid #e5eaeb; }}
        .led:last-of-type {{ border-bottom: 0; }}
        .status {{ font-weight: 700; }}
        button {{ padding: .65rem .9rem; border: 0; border-radius: 8px; color: white; background: #157a6e; cursor: pointer; font-weight: 700; }}
        button.off {{ background: #b64b36; }}
        button:disabled {{ cursor: wait; opacity: .65; }}
        .error {{ min-height: 1.4em; color: #b64b36; }}
    </style>
</head>
<body>
    <main>
        <h1>Raspberry Pi IoT Controller</h1>
        <div class="grid">
            <section>
                <h2>Thời tiết</h2>
                <dl>
                    <dt>Địa điểm</dt><dd id="location">--</dd>
                    <dt>Nhiệt độ</dt><dd id="temperature">--</dd>
                    <dt>Mưa</dt><dd id="rain">--</dd>
                    <dt>Lượng mưa</dt><dd id="precipitation">--</dd>
                    <dt>Gió</dt><dd id="wind">--</dd>
                    <dt>Trạng thái</dt><dd id="weather">--</dd>
                    <dt>Cập nhật</dt><dd id="time">--</dd>
                </dl>
                <p id="weather-error" class="error" aria-live="polite"></p>
                <button id="refresh-weather" type="button">Cập nhật thời tiết</button>
            </section>
            <section>
                <h2>Điều khiển LED</h2>
                <div id="led-list"></div>
                <button id="all-off" type="button">Tắt tất cả</button>
                <p id="led-error" class="error" aria-live="polite"></p>
            </section>
        </div>
    </main>
    <script>
        const initialLeds = {initial_leds};
        const initialWeather = {initial_weather};
        const ledList = document.querySelector('#led-list');
        const ledError = document.querySelector('#led-error');
        const weatherError = document.querySelector('#weather-error');

        function renderLeds(leds) {{
            ledList.innerHTML = Object.entries(leds).map(([pin, isOn]) => `
                <div class="led">
                    <span>LED GPIO ${{pin}}</span>
                    <span><span class="status">${{isOn ? 'BẬT' : 'TẮT'}}</span>
                    <button class="${{isOn ? 'off' : ''}}" data-pin="${{pin}}" data-on="${{isOn}}">
                        ${{isOn ? 'Tắt' : 'Bật'}}
                    </button></span>
                </div>`).join('');
        }}

        function renderWeather(weather) {{
            document.querySelector('#location').textContent = weather.location || '--';
            document.querySelector('#temperature').textContent = weather.temperature == null ? '--' : `${{weather.temperature}} °C`;
            document.querySelector('#rain').textContent = weather.rain == null ? '--' : `${{weather.rain}} mm`;
            document.querySelector('#precipitation').textContent = weather.precipitation == null ? '--' : `${{weather.precipitation}} mm`;
            document.querySelector('#wind').textContent = weather.wind_speed == null ? '--' : `${{weather.wind_speed}} km/h`;
            document.querySelector('#weather').textContent = weather.weather || '--';
            document.querySelector('#time').textContent = weather.time || '--';
        }}

        async function request(url, options) {{
            const response = await fetch(url, options);
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Yêu cầu thất bại');
            return data;
        }}

        ledList.addEventListener('click', async (event) => {{
            const button = event.target.closest('button[data-pin]');
            if (!button) return;
            button.disabled = true;
            ledError.textContent = '';
            const action = button.dataset.on === 'true' ? 'off' : 'on';
            try {{ renderLeds((await request(`/api/led/${{button.dataset.pin}}/${{action}}`, {{ method: 'POST' }})).leds); }}
            catch (error) {{ ledError.textContent = error.message; }}
        }});

        document.querySelector('#all-off').addEventListener('click', async () => {{
            ledError.textContent = '';
            try {{ renderLeds((await request('/api/led/all-off', {{ method: 'POST' }})).leds); }}
            catch (error) {{ ledError.textContent = error.message; }}
        }});

        document.querySelector('#refresh-weather').addEventListener('click', async () => {{
            weatherError.textContent = '';
            try {{ renderWeather(await request('/api/weather')); }}
            catch (error) {{ weatherError.textContent = error.message; }}
        }});

        renderLeds(initialLeds);
        renderWeather(initialWeather);
    </script>
</body>
</html>""".encode("utf-8")


def json_response(data):
    return json.dumps(data, ensure_ascii=False).encode("utf-8")
