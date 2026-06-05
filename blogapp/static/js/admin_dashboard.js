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

let lastBenchmarkResult = null;

function getBenchmarkRecommendation(avgFps) {
    if (avgFps >= 55) {
        return {
            key: 'excellent',
            alertClass: 'alert-success',
            en: 'Excellent performance! Full mode recommended.',
            zh: '性能优秀，推荐使用完整模式。'
        };
    }
    if (avgFps >= 40) {
        return {
            key: 'good',
            alertClass: 'alert-info',
            en: 'Good performance. Full mode works well.',
            zh: '性能良好，完整模式运行顺畅。'
        };
    }
    if (avgFps >= 25) {
        return {
            key: 'moderate',
            alertClass: 'alert-warning',
            en: 'Moderate performance. Consider Lite mode.',
            zh: '性能中等，可考虑使用轻量模式。'
        };
    }
    return {
        key: 'low',
        alertClass: 'alert-danger',
        en: 'Low performance detected. Lite mode strongly recommended.',
        zh: '检测到性能较低，强烈建议使用轻量模式。'
    };
}

function renderBenchmarkResult() {
    if (!lastBenchmarkResult) return;
    const { avgFps, minFps } = lastBenchmarkResult;
    const rec = getBenchmarkRecommendation(avgFps);

    document.getElementById('avgFps').textContent = avgFps;
    document.getElementById('minFps').textContent = minFps;
    document.getElementById('recommendation').textContent = tr(rec.en, rec.zh);
    document.getElementById('benchmarkAlert').className = 'alert ' + rec.alertClass;
    document.getElementById('benchmarkResult').style.display = 'block';
}

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
window.runBenchmark = async function() {
    const btn = document.getElementById('benchmarkBtn');
    const resultDiv = document.getElementById('benchmarkResult');
    
    btn.disabled = true;
    btn.innerHTML = `<i class="bi bi-hourglass-split me-1"></i>${tr('Testing...', '测试中...')} <span id="countdown">10</span>s`;
    
    resultDiv.style.display = 'none';

    const wasLiteMode = document.body.classList.contains('ui-lite');
    if (wasLiteMode) {
        document.body.classList.remove('ui-lite');
        document.body.classList.add('ui-full');
    }
    await new Promise(resolve => setTimeout(resolve, 100));
    
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
        if (wasLiteMode) {
            document.body.classList.remove('ui-full');
            document.body.classList.add('ui-lite');
        }
        
        const avgFps = FPSMonitor.getAverageFPS();
        const minFps = FPSMonitor.getMinFPS();
        
        document.getElementById('avgFps').textContent = avgFps;
        document.getElementById('minFps').textContent = minFps;
        
        lastBenchmarkResult = { avgFps, minFps };
        renderBenchmarkResult();
        
        btn.disabled = false;
        btn.innerHTML = `<i class="bi bi-play-circle me-1"></i>${tr('Retest', '重新测试')}`;
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
        const response = await fetch('/api/admin/stats', {
            credentials: 'same-origin'
        });
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
        const response = await fetch('/api/admin/users', {
            credentials: 'same-origin'
        });
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
                        <button class="btn btn-sm btn-outline-primary d-inline-flex align-items-center gap-1" data-action="view-factories" data-user-id="${user.id}" data-username="${escapeHtml(user.username)}">
                            <span class="badge bg-primary">${user.factory_count}</span>
                            <span>View</span>
                        </button>
                    </td>
                    <td style="padding: 0.75rem; text-align: right; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">${user.total_usage.toLocaleString()}</td>
                    <td style="padding: 0.75rem; text-align: right; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">${user.total_carbon.toLocaleString()}</td>
                    <td style="padding: 0.75rem; text-align: center; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">
                        ${user.is_banned 
                            ? '<span class="badge bg-danger">Banned</span>' 
                            : '<span class="badge bg-success">Active</span>'}
                    </td>
                    <td style="padding: 0.75rem; text-align: center; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">
                        ${user.is_banned 
                            ? `<button class="btn btn-sm btn-success" data-action="unban-user" data-user-id="${user.id}" data-username="${escapeHtml(user.username)}"><i class="bi bi-unlock"></i> Unban</button>`
                            : `<button class="btn btn-sm btn-warning" data-action="ban-user" data-user-id="${user.id}" data-username="${escapeHtml(user.username)}"><i class="bi bi-slash-circle"></i> Ban</button>`}
                    </td>
                </tr>
            `).join('');
            console.log(`✅ Loaded ${data.users.length} users`);
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted">
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
                <td colspan="9" class="text-center text-danger">
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
        const response = await fetch('/api/admin/factories', {
            credentials: 'same-origin'
        });
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
                    <td style="padding: 0.75rem; text-align: center; border-bottom: 1px solid rgba(226, 232, 240, 0.5);">
                        <button class="btn btn-sm btn-danger" data-action="delete-factory" data-factory-id="${factory.id}" data-factory-name="${escapeHtml(factory.name)}">
                            <i class="bi bi-trash"></i> Delete
                        </button>
                    </td>
                </tr>
            `).join('');
            console.log(`✅ Loaded ${data.factories.length} factories`);
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted">
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
                <td colspan="9" class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Failed to load: ${error.message}
                </td>
            </tr>
        `;
    }
}


// ========================================
// Admin Actions
// ========================================

function tr(en, zh) {
    return (typeof I18N !== 'undefined' && I18N.currentLang === 'zh') ? zh : en;
}

// Delete factory (admin)
window.deleteFactoryAdmin = async function(factoryId, factoryName) {
    const confirmMsg = tr(
        `Delete factory "${factoryName}"? The owner will see a notification.`,
        `确定删除工厂"${factoryName}"？工厂所属用户将收到提示。`
    );
    if (!confirm(confirmMsg)) return;
    
    try {
        const resp = await fetch(`/api/admin/factory/${factoryId}/delete`, {
            credentials: 'same-origin',
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ deleted_at_client: new Date().toISOString() })
        });
        const data = await resp.json();
        
        if (data.success) {
            alert(tr('Factory deleted successfully', '工厂删除成功'));
            await loadFactories();
            await loadAdminStats();
            await loadUsers();
        } else {
            alert(tr('Failed: ', '失败：') + (data.message || 'Unknown error'));
        }
    } catch (e) {
        alert(tr('Network error: ', '网络错误：') + e.message);
    }
};

// Ban user
window.banUser = async function(userId, username) {
    const confirmMsg = tr(
        `Ban user "${username}"? They will not be able to log in.`,
        `确定封禁用户"${username}"？该用户将无法登录。`
    );
    if (!confirm(confirmMsg)) return;
    
    try {
        const resp = await fetch(`/api/admin/user/${userId}/ban`, {
            credentials: 'same-origin',
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        const data = await resp.json();
        
        if (data.success) {
            alert(tr('User banned', '用户已封禁'));
            await loadUsers();
        } else {
            alert(tr('Failed: ', '失败：') + (data.message || 'Unknown error'));
        }
    } catch (e) {
        alert(tr('Network error: ', '网络错误：') + e.message);
    }
};

// Unban user
window.unbanUser = async function(userId, username) {
    const confirmMsg = tr(
        `Unban user "${username}"?`,
        `确定解封用户"${username}"？`
    );
    if (!confirm(confirmMsg)) return;
    
    try {
        const resp = await fetch(`/api/admin/user/${userId}/unban`, {
            credentials: 'same-origin',
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        const data = await resp.json();
        
        if (data.success) {
            alert(tr('User unbanned', '用户已解封'));
            await loadUsers();
        } else {
            alert(tr('Failed: ', '失败：') + (data.message || 'Unknown error'));
        }
    } catch (e) {
        alert(tr('Network error: ', '网络错误：') + e.message);
    }
};

// View user's factories in a modal
window.viewUserFactories = async function(userId, username) {
    try {
        const resp = await fetch(`/api/admin/users/${userId}/factories`, {
            credentials: 'same-origin'
        });
        const data = await resp.json();
        
        if (!data.success) {
            alert(tr('Failed to load: ', '加载失败：') + (data.message || ''));
            return;
        }
        
        // Build modal HTML
        let modalHtml = `
            <div class="modal fade glass-data-modal user-factories-modal" id="userFactoriesModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-person-circle me-2"></i>
                                ${tr('Factories of', '用户工厂：')} ${escapeHtml(username)}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
        `;
        
        if (data.factories.length === 0) {
            modalHtml += `<p class="text-muted text-center py-3">${tr('No factories', '暂无工厂')}</p>`;
        } else {
            modalHtml += `<div class="admin-modal-table-card"><div class="table-responsive"><table class="user-factories-table">`;
            modalHtml += `<thead><tr>`;
            modalHtml += `<th class="text-start">${tr('Name', '名称')}</th>`;
            modalHtml += `<th class="text-start">${tr('Location', '位置')}</th>`;
            modalHtml += `<th class="text-start">${tr('Industry', '行业')}</th>`;
            modalHtml += `<th class="text-end">${tr('Monthly Usage', '月用电量')}</th>`;
            modalHtml += `<th class="text-center">${tr('Actions', '操作')}</th>`;
            modalHtml += `</tr></thead><tbody>`;
            
            for (const f of data.factories) {
                modalHtml += `
                    <tr>
                        <td class="text-start">${escapeHtml(f.name)}</td>
                        <td class="text-start">${escapeHtml(f.location || '-')}</td>
                        <td class="text-start">${escapeHtml(f.industry_type || '-')}</td>
                        <td class="text-end">${f.monthly_usage.toLocaleString()} kWh</td>
                        <td class="text-center">
                            <button class="btn btn-sm btn-danger admin-table-danger-btn" data-action="delete-factory-modal" data-factory-id="${f.id}" data-factory-name="${escapeHtml(f.name)}" data-user-id="${userId}" data-username="${escapeHtml(username)}">
                                <i class="bi bi-trash"></i> ${tr('Delete', '删除')}
                            </button>
                        </td>
                    </tr>
                `;
            }
            modalHtml += '</tbody></table></div></div>';
        }
        
        modalHtml += `
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">${tr('Close', '关闭')}</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal
        const existing = document.getElementById('userFactoriesModal');
        if (existing) existing.remove();
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('userFactoriesModal'));
        modal.show();
    } catch (e) {
        alert(tr('Error: ', '错误：') + e.message);
    }
};

// Delete factory from within the user-factories modal, then refresh admin data.
window.deleteFactoryFromModal = async function(factoryId, factoryName, userId, username) {
    const confirmMsg = tr(
        `Delete factory "${factoryName}"?`,
        `确定删除工厂"${factoryName}"？`
    );
    if (!confirm(confirmMsg)) return;
    
    try {
        const resp = await fetch(`/api/admin/factory/${factoryId}/delete`, {
            credentials: 'same-origin',
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ deleted_at_client: new Date().toISOString() })
        });
        const data = await resp.json();
        
        if (data.success) {
            // Close the modal after the confirmed delete.
            const modal = bootstrap.Modal.getInstance(document.getElementById('userFactoriesModal'));
            if (modal) modal.hide();
            
            await loadAdminStats();
            await loadUsers();
            await loadFactories();
        } else {
            alert(tr('Failed: ', '失败：') + (data.message || ''));
        }
    } catch (e) {
        alert(tr('Network error: ', '网络错误：') + e.message);
    }
};

// ========================================
// Delegated event handlers (replaces inline onclick to prevent injection)
// ========================================
document.addEventListener('click', function(e) {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;
    
    const action = btn.dataset.action;
    
    if (action === 'view-factories') {
        viewUserFactories(parseInt(btn.dataset.userId), btn.dataset.username);
    } else if (action === 'ban-user') {
        banUser(parseInt(btn.dataset.userId), btn.dataset.username);
    } else if (action === 'unban-user') {
        unbanUser(parseInt(btn.dataset.userId), btn.dataset.username);
    } else if (action === 'delete-factory') {
        deleteFactoryAdmin(parseInt(btn.dataset.factoryId), btn.dataset.factoryName);
    } else if (action === 'delete-factory-modal') {
        deleteFactoryFromModal(
            parseInt(btn.dataset.factoryId),
            btn.dataset.factoryName,
            parseInt(btn.dataset.userId),
            btn.dataset.username
        );
    }
});

window.addEventListener('peakshift:languageChanged', () => {
    renderBenchmarkResult();
});
