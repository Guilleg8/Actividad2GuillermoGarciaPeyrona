document.addEventListener('DOMContentLoaded', (event) => {
    const wsStatusEl = document.getElementById('ws-status');
    const userRoleEl = document.getElementById('user-role');
    const jwtTokenEl = document.getElementById('jwt-token');
    const log = document.getElementById('log');
    const sensorResponseEl = document.getElementById('sensor-response');
    const protectedResponseEl = document.getElementById('protected-response');

    let accessToken = localStorage.getItem('access_token') || null;

    function updateStatus(el, message, className) {
        if (!el) return;
        el.textContent = message;
        el.className = 'status-badge ' + className;
    }

    function logAlert(message, level = '') {
        const li = document.createElement('li');
        li.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        if (level) {
            li.className = level.toLowerCase();
        }
        log.prepend(li);
    }

    function updateTokenDisplay() {
        if (accessToken) {
            const parts = accessToken.split('.');
            if (parts.length === 3) {
                try {
                    const payload = JSON.parse(atob(parts[1]));
                    const role = payload.role || 'Desconocido';
                    updateStatus(userRoleEl, `Autenticado: ${role}`, 'status-ok');
                    if (jwtTokenEl) jwtTokenEl.textContent = accessToken.substring(0, 30) + '...';
                    return;
                } catch (e) {
                    console.error("Error decodificando JWT:", e);
                }
            }
        }
        updateStatus(userRoleEl, 'No Autenticado', 'status-error');
        if (jwtTokenEl) jwtTokenEl.textContent = 'No token';
        localStorage.removeItem('access_token');
        accessToken = null;
    }

    function connectWebSocket() {
        const wsUrl = `ws://${window.location.host}/ws/alerts`;
        const socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            updateStatus(wsStatusEl, "Conectado y Escuchando", 'status-ok');
            log.innerHTML = '<li>✅ Conexión WebSocket establecida.</li>';
        };

        socket.onmessage = (event) => {
            let message = event.data;
            let level = '';

            if (message.includes('"CRITICAL"')) {
                level = 'CRITICAL';
            } else if (message.includes('"WARNING"')) {
                level = 'WARNING';
            }
            logAlert(message, level);
        };

        socket.onclose = () => {
            updateStatus(wsStatusEl, "Desconectado", 'status-error');
            logAlert("❌ WebSocket Desconectado. Reconectando en 5s...", 'warning');
            setTimeout(connectWebSocket, 5000);
        };

        socket.onerror = (error) => {
            console.error("[error]", error);
            logAlert("❌ Error en la conexión WebSocket.", 'critical');
        };
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: `grant_type=password&username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}&scope=&client_id=&client_secret=`
                });

                if (response.ok) {
                    const data = await response.json();
                    accessToken = data.access_token;
                    localStorage.setItem('access_token', accessToken);
                    updateTokenDisplay();
                    alert(`¡Login exitoso! Rol: ${data.role}`);
                } else {
                    const errorData = await response.json();
                    let errorMessage = "Credenciales incorrectas o error de servidor.";
                    if (errorData && errorData.detail) {
                        errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
                    }
                    alert(`Error de Login: ${errorMessage}`);
                    updateTokenDisplay();
                }
            } catch (error) {
                alert('Error de red al intentar el login.');
                updateTokenDisplay();
            }
        });
    }

    const sensorForm = document.getElementById('sensor-form');
    if(sensorForm) {
        sensorForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const type = document.getElementById('sensor-type').value;
            const valueInput = document.getElementById('sensor-value');
            const value = valueInput ? valueInput.value : 'DEFAULT_EVENT_VALUE';


            sensorResponseEl.textContent = 'Enviando...';

            const payload = {
                sensor_type: type,
                sensor_id: `${type.toUpperCase().substring(0, 1)}-007`,
                timestamp: Date.now() / 1000,
                value: value
            };

            try {
                const response = await fetch('/sensor/event', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.status === 202) {
                    sensorResponseEl.textContent = `✅ ${data.message}`;
                    sensorResponseEl.style.color = '#00ffcc';
                } else {
                    sensorResponseEl.textContent = `❌ Error ${response.status}: ${data.detail}`;
                    sensorResponseEl.style.color = 'red';
                }

            } catch (error) {
                sensorResponseEl.textContent = '❌ Error de red al enviar el evento.';
                sensorResponseEl.style.color = 'red';
            }
        });
    }

    window.fetchProtected = async function(endpoint, method) {
        if (!protectedResponseEl) return;
        protectedResponseEl.textContent = 'Llamando a la ruta protegida...';
        protectedResponseEl.style.color = '#c9d1d9';

        if (!accessToken) {
            protectedResponseEl.textContent = '❌ ERROR: Necesitas iniciar sesión primero (Token no encontrado).';
            protectedResponseEl.style.color = 'red';
            return;
        }

        try {
            const response = await fetch(endpoint, {
                method: method,
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok) {
                protectedResponseEl.textContent = `✅ Éxito (${response.status}): ${JSON.stringify(data)}`;
                protectedResponseEl.style.color = '#00ffcc';
            } else {
                protectedResponseEl.textContent = `❌ Error ${response.status} (${data.detail}): Rol no autorizado o Token inválido.`;
                protectedResponseEl.style.color = 'red';
            }

        } catch (error) {
            protectedResponseEl.textContent = '❌ Error de red al acceder a la ruta.';
            protectedResponseEl.style.color = 'red';
        }
    }

    updateTokenDisplay();
    connectWebSocket();

});