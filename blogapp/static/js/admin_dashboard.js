// Admin Dashboard JavaScript

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ========================================
// FPS Monitor
// ========================================
const FPSMonitor = {
    lastTime: performance.now(),
    frames: 0,
    fps: 0,
    isRunning: false,
    fpsHistory: [],
    
    start() {
        this.isRunning = true;
        this.lastTime = performance.now();
        this.frames = 0;
        this.fpsHistory = [];
        this.update();
    },
    
    stop() {
        this.isRunning = false;
    },
    
    update() {
        if (!this.isRunning) return;
        
        this.frames++;
        const currentTime = performance.now();
        const delta = currentTime - this.lastTime;
        
        if (delta >= 1000) {
            this.fps = Math.round((this.frames * 1000) / delta);
            this.fpsHistory.push(this.fps);
            if (this.fpsHistory.length > 60) {
                this.fpsHistory.shift();
            }
            this.frames = 0;
            this.lastTime = currentTime;
        }
        
        requestAnimationFrame(() => this.update());
    },
    
    getCurrentFPS() {
        return this.fps;
    },
    
    getAverageFPS() {
        if (this.fpsHistory.length === 0) return 0;
        const sum = this.fpsHistory.reduce((a, b) => a + b, 0);
        return Math.round(sum / this.fpsHistory.length);
    },
    
    getMinFPS() {
        if (this.fpsHistory.length === 0) return 0;
        return Math.min(...this.fpsHistory);
    }
};

// ========================================
// Settings Functions
// ========================================

// Open settings modal
window.openSettings = function() {
    const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
    
    // Load saved settings
    const savedMode = localStorage.getItem('uiMode') || 'full';
    document.querySelector(`input[name="uiMode"][value="${savedMode}"]`).checked = true;
    
    const showFps = localStorage.getItem('showFps') === 'true';
    document.getElementById('showFpsToggle').checked = showFps;
    
    // Load current language
    const currentLang = localStorage.getItem('lang') || 'en';
    const langRadio = document.getElementById(currentLang === 'zh' ? 'langZh' : 'langEn');
    if (langRadio) langRadio.checked = true;
    
    modal.show();
};

// Run benchmark test
window.runBenchmark = function() {
    const btn = document.getElementById('benchmarkBtn');
    const resultDiv = document.getElementById('benchmarkResult');
    const alertDiv = document.getElementById('benchmarkAlert');
    
    btn.disabled = true;
    btn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Testing... <span id="countdown">10</span>s';
    
    resultDiv.style.display = 'none';
    
    FPSMonitor.start();
    
    let countdown = 10;
    const countdownInterval = setInterval(() => {
        countdown--;
        const countdownSpan = document.getElementById('countdown');
        if (countdownSpan) {
            countdownSpan.textContent = countdown;
        }
        
        if (countdown <= 0) {
            clearInterval(countdownInterval);
        }
    }, 1000);
    
    setTimeout(() => {
        FPSMonitor.stop();
        
        const avgFps = FPSMonitor.getAverageFPS();
        const minFps = FPSMonitor.getMinFPS();
        
        document.getElementById('avgFps').textContent = avgFps;
        document.getElementById('minFps').textContent = minFps;
        
        let recommendation = '';
        let alertClass = '';
        
        if (avgFps >= 55) {
            recommendation = 'Excellent performance! Full mode recommended.';
            alertClass = 'alert-success';
        } else if (avgFps >= 40) {
            recommendation = 'Good performance. Full mode works well.';
            alertClass = 'alert-info';
        } else if (avgFps >= 25) {
            recommendation = 'Moderate performance. Consider Lite mode.';
            alertClass = 'alert-warning';
        } else {
            recommendation = 'Low performance detected. Lite mode strongly recommended.';
            alertClass = 'alert-danger';
        }
        
        document.getElementById('recommendation').textContent = recommendation;
        alertDiv.className = 'alert ' + alertClass;
        
        resultDiv.style.display = 'block';
        
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-play-circle me-1"></i>Retest';
    }, 10000);
};

// Toggle FPS display
window.toggleFpsDisplay = function() {
    const showFps = document.getElementById('showFpsToggle').checked;
    const fpsDisplay = document.getElementById('fpsDisplay');
    
    if (showFps) {
        fpsDisplay.style.display = 'block';
        FPSMonitor.start();
        updateFpsDisplay();
    } else {
        fpsDisplay.style.display = 'none';
        FPSMonitor.stop();
    }
};

// Update FPS display
function updateFpsDisplay() {
    if (!FPSMonitor.isRunning) return;
    
    const fps = FPSMonitor.getCurrentFPS();
    document.getElementById('fpsValue').textContent = fps;
    
    setTimeout(updateFpsDisplay, 500);
}

// Save settings
window.saveSettings = function() {
    const uiMode = document.querySelector('input[name="uiMode"]:checked').value;
    const showFps = document.getElementById('showFpsToggle').checked;
    
    // Save language
    const langChoice = document.querySelector('input[name="langChoice"]:checked');
    if (langChoice) {
        I18N.setLang(langChoice.value);
    }
    
    localStorage.setItem('uiMode', uiMode);
    localStorage.setItem('showFps', showFps);
    
    applyUIMode(uiMode);
    
    const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
    modal.hide();
    
    console.log('✅ Settings saved');
};

// Apply UI mode
function applyUIMode(mode) {
    if (mode === 'lite') {
        document.body.classList.add('ui-lite');
        document.body.classList.remove('ui-full');
    } else {
        document.body.classList.add('ui-full');
        document.body.classList.remove('ui-lite');
    }
}

// ========================================
// Admin Data Loading
// ========================================

// Load admin statistics on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Admin Dashboard initializing...');
    
    loadAdminStats();
    loadUsers();
    loadFactories();
    
    // Load saved settings
    const savedMode = localStorage.getItem('uiMode') || 'full';
    applyUIMode(savedMode);
    
    const showFps = localStorage.getItem('showFps') === 'true';
    if (showFps) {
        document.getElementById('fpsDisplay').style.display = 'block';
        FPSMonitor.start();
        updateFpsDisplay();
    }
    
    console.log('✅ Admin Dashboard initialization complete');
});

// Load admin statistics
async function loadAdminStats() {
    try {
        const response = await fetch('/api/admin/stats');
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('totalUsers').textContent = data.stats.total_users;
            document.getElementById('totalFactories').textContent = data.stats.total_factories;
            document.getElementById('totalEnergy').textContent = data.stats.total_monthly_usage.toLocaleString();
            document.getElementById('totalCarbon').textContent = data.stats.total_carbon_emission.toLocaleString();
            console.log('✅ Admin stats loaded');
        } else {
            console.error('Failed to load admin stats:', data.message);
        }
    } catch (error) {
        console.error('Error loading admin stats:', error);
    }
}

// Load users list
async function loadUsers() {
    try {
        const response = await fetch('/api/admin/users');
        const data = await response.json();
        
        const tbody = document.getElementById('usersTableBody');
        
        if (data.success && data.users.length > 0) {
            tbody.innerHTML = data.users.map(user => `
                <tr style="background: transparent;">
                    <td style="padding: 0.75rem; text-align: center; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">${user.id}</td>
                    <td style="padding: 0.75rem; text-align: left; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">
                        <i class="bi bi-person-circle me-1"></i>
                        ${escapeHtml(user.username)}
                    </td>
                    <td style="padding: 0.75rem; text-align: left; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">${escapeHtml(user.email)}</td>
                    <td style="padding: 0.75rem; text-align: center; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">${user.created_at}</td>
                    <td style="padding: 0.75rem; text-align: center; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">
                        <span class="badge bg-primary">${user.factory_count}</span>
                    </td>
                    <td style="padding: 0.75rem; text-align: right; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">${user.total_usage.toLocaleString()}</td>
                    <td style="padding: 0.75rem; text-align: right; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">${user.total_carbon.toLocaleString()}</td>
                </tr>
            `).join('');
            console.log(`✅ Loaded ${data.users.length} users`);
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted">
                        <i class="bi bi-inbox me-2"></i>
                        No user data available
                    </td>
                </tr>
            `;
        }
    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('usersTableBody').innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Failed to load: ${error.message}
                </td>
            </tr>
        `;
    }
}

// Load factories list
async function loadFactories() {
    try {
        const response = await fetch('/api/admin/factories');
        const data = await response.json();
        
        const tbody = document.getElementById('factoriesTableBody');
        
        if (data.success && data.factories.length > 0) {
            tbody.innerHTML = data.factories.map(factory => `
                <tr style="background: transparent;">
                    <td style="padding: 0.75rem; text-align: center; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">${factory.id}</td>
                    <td style="padding: 0.75rem; text-align: left; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">
                        <i class="bi bi-building me-1"></i>
                        ${escapeHtml(factory.name)}
                    </td>
                    <td style="padding: 0.75rem; text-align: left; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">${factory.location ? escapeHtml(factory.location) : '-'}</td>
                    <td style="padding: 0.75rem; text-align: left; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">${factory.industry_type ? escapeHtml(factory.industry_type) : '-'}</td>
                    <td style="padding: 0.75rem; text-align: center; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">${factory.voltage_level} kV</td>
                    <td style="padding: 0.75rem; text-align: right; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">${factory.monthly_usage.toLocaleString()}</td>
                    <td style="padding: 0.75rem; text-align: right; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">${factory.carbon_emission.toLocaleString()}</td>
                    <td style="padding: 0.75rem; text-align: left; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">
                        ${factory.user ? `
                            <i class="bi bi-person-circle me-1"></i>
                            ${escapeHtml(factory.user.username)}
                        ` : '-'}
                    </td>
                </tr>
            `).join('');
            console.log(`✅ Loaded ${data.factories.length} factories`);
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted">
                        <i class="bi bi-inbox me-2"></i>
                        No factory data available
                    </td>
                </tr>
            `;
        }
    } catch (error) {
        console.error('Error loading factories:', error);
        document.getElementById('factoriesTableBody').innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Failed to load: ${error.message}
                </td>
            </tr>
        `;
    }
}
