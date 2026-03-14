document.addEventListener('DOMContentLoaded', () => {
    // Check if we are on the dashboard
    const isDashboard = document.getElementById('task-panel');
    
    // Auth Forms Toggle
    const showRegister = document.getElementById('show-register');
    const showLogin = document.getElementById('show-login');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    
    if (showRegister) {
        showRegister.addEventListener('click', (e) => {
            e.preventDefault();
            loginForm.classList.remove('active');
            registerForm.classList.add('active');
        });
    }
    
    if (showLogin) {
        showLogin.addEventListener('click', (e) => {
            e.preventDefault();
            registerForm.classList.remove('active');
            loginForm.classList.add('active');
        });
    }

    // Auth Submit Handlers
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('login-username').value;
            const pass = document.getElementById('login-password').value;
            
            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify({username: username, password: pass})
                });
                const data = await res.json();
                if (res.ok) {
                    window.location.href = '/dashboard';
                } else {
                    showAlert(data.message || "Login failed");
                }
            } catch (err) {
                showAlert("Network error during login");
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('reg-username').value;
            const email = document.getElementById('reg-email').value;
            const pass = document.getElementById('reg-password').value;
            
            try {
                const res = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify({username, email, password: pass})
                });
                const data = await res.json();
                if (res.ok) {
                    showAlert("Registration successful. Please login.", "success");
                    showLogin.click();
                } else {
                    showAlert(data.message || "Registration failed");
                }
            } catch (err) {
                showAlert("Network error during registration");
            }
        });
    }
    
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            await fetch('/api/auth/logout', { 
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                }
            });
            window.location.href = '/';
        });
    }

    function showAlert(msg, type="error") {
        const alertBox = document.getElementById('auth-alert');
        if (!alertBox) return;
        alertBox.textContent = msg;
        alertBox.className = `alert ${type}`;
        alertBox.classList.remove('hidden');
        setTimeout(() => alertBox.classList.add('hidden'), 3000);
    }

    // --- Dashboard Logic ---
    if (isDashboard) {
        let currentTaskType = 'assignment';
        let currentResponseId = null;

        // Navigation
        const navItems = document.querySelectorAll('.nav-item');
        const panels = document.querySelectorAll('.panel');

        navItems.forEach(item => {
            item.addEventListener('click', () => {
                navItems.forEach(n => n.classList.remove('active'));
                panels.forEach(p => p.classList.remove('active', 'hidden'));
                panels.forEach(p => p.classList.add('hidden'));
                
                item.classList.add('active');
                const targetId = item.getAttribute('data-target');
                document.getElementById(targetId).classList.remove('hidden');
                document.getElementById(targetId).classList.add('active');

                if (targetId === 'history-panel') loadHistory();
                if (targetId === 'stats-panel') loadStats();
            });
        });

        // Task Tabs
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                tabBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentTaskType = btn.getAttribute('data-type');
                document.getElementById('task-prompt').placeholder = 
                    `Enter details for your ${currentTaskType}...`;
            });
        });

        // Voice Input using SpeechRecognition API
        const voiceBtn = document.getElementById('voice-btn');
        const voiceStatus = document.getElementById('voice-status');
        const promptArea = document.getElementById('task-prompt');
        let recognition = null;
        
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecog = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecog();
            recognition.continuous = false;
            recognition.interimResults = true;
            
            recognition.onstart = () => {
                voiceStatus.classList.remove('hidden');
                voiceBtn.classList.add('pulse-hover');
                voiceBtn.style.color = 'var(--error-color)';
            };
            
            recognition.onresult = (event) => {
                let interimTranscript = '';
                let finalTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }
                
                if (finalTranscript) {
                    const currentVal = promptArea.value;
                    promptArea.value = currentVal ? currentVal + ' ' + finalTranscript : finalTranscript;
                }
            };
            
            recognition.onerror = (e) => {
                console.error("Speech error", e);
                stopVoice();
            };
            
            recognition.onend = () => {
                stopVoice();
            };
        } else {
            if (voiceBtn) voiceBtn.style.display = 'none';
        }

        function stopVoice() {
            voiceStatus.classList.add('hidden');
            voiceBtn.classList.remove('pulse-hover');
            voiceBtn.style.color = 'var(--primary-color)';
        }

        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => {
                if (voiceStatus.classList.contains('hidden')) {
                    if (recognition) recognition.start();
                } else {
                    if (recognition) recognition.stop();
                }
            });
        }

        // Submit Task
        const submitBtn = document.getElementById('submit-task');
        const responseArea = document.getElementById('response-area');
        const loader = document.getElementById('loader');
        const responseContent = document.getElementById('response-content');

        submitBtn.addEventListener('click', async () => {
            const prompt = promptArea.value.trim();
            if (!prompt) return alert("Please enter a task instruction.");
            
            const personality = document.getElementById('personality').value;
            
            responseArea.classList.remove('hidden');
            responseContent.innerHTML = "";
            loader.classList.remove('hidden');
            submitBtn.disabled = true;

            try {
                const res = await fetch('/api/tasks/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify({
                        task_type: currentTaskType,
                        prompt: prompt,
                        parameters: { personality: personality }
                    })
                });
                
                const data = await res.json();
                
                loader.classList.add('hidden');
                submitBtn.disabled = false;

                if (res.ok) {
                    // Requires marked.js loaded in base.html
                    if (typeof marked !== 'undefined') {
                        responseContent.innerHTML = marked.parse(data.response);
                    } else {
                        responseContent.innerText = data.response;
                    }
                    currentResponseId = data.response_id;
                } else {
                    responseContent.innerHTML = `<p class="error">Error: ${data.message}</p>`;
                }
            } catch (err) {
                loader.classList.add('hidden');
                submitBtn.disabled = false;
                responseContent.innerHTML = `<p class="error">Network error. Is backend running?</p>`;
            }
        });

        // Export Actions
        const exportBtns = document.querySelectorAll('.export-btn');
        exportBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                if (!currentResponseId) return alert("Save a response first.");
                const format = btn.getAttribute('data-format');
                const handwritten = btn.getAttribute('data-handwritten');
                
                let url = `/api/tasks/export/${currentResponseId}?format=${format}`;
                if (handwritten) url += `&handwritten=${handwritten}`;
                
                window.open(url, '_blank');
            });
        });

        // Load History
        async function loadHistory() {
            const list = document.getElementById('history-list');
            list.innerHTML = "<p>Loading...</p>";
            try {
                const res = await fetch('/api/tasks/history');
                const data = await res.json();
                if (res.ok) {
                    list.innerHTML = "";
                    if(data.history.length === 0) {
                        list.innerHTML = "<p>No tasks yet.</p>";
                        return;
                    }
                    data.history.forEach(t => {
                        const date = new Date(t.created_at).toLocaleString();
                        list.innerHTML += `
                            <div class="history-item">
                                <div class="history-type">${t.task_type.toUpperCase()} - ${date}</div>
                                <p><strong>Prompt:</strong> ${t.prompt}</p>
                            </div>
                        `;
                    });
                }
            } catch (e) {
                list.innerHTML = "<p>Error loading history.</p>";
            }
        }
        
        // Load Stats
        async function loadStats() {
            try {
                // If the user isn't admin this will fail or return 403, we can handle gracefully
                const res = await fetch('/api/admin/stats');
                if (res.ok) {
                    const data = await res.json();
                    document.getElementById('stat-total-tasks').innerText = data.total_tasks || 0;
                }
            } catch (e) {
                console.log("Not an admin or error loading stats");
            }
        }
    }
});
