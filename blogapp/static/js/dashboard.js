/* ========================================
   PeakShift Dashboard - Single Page Application
   ======================================== */

(function() {
    'use strict';
    
    // ========================================
    // 全局状态管理
    // ========================================
    const AppState = {
        currentView: 'factoryManagement',
        factories: [],
        currentFactory: null
    };
    
    // ========================================
    // 视图切换
    // ========================================
    function showView(viewName) {
        // 隐藏所有视图
        document.querySelectorAll('.view-container').forEach(view => {
            view.classList.remove('active');
        });
        
        // 显示目标视图
        const targetView = document.getElementById(viewName + 'View');
        if (targetView) {
            targetView.classList.add('active');
            AppState.currentView = viewName;
        }
    }
    
    // ========================================
    // 工厂管理功能
    // ========================================
    
    // 加载工厂列表
    async function loadFactories() {
        try {
            const response = await fetch('/api/factories');
            const data = await response.json();
            
            if (data.success) {
                AppState.factories = data.factories;
                renderFactories();
            } else {
                showError('加载工厂列表失败');
            }
        } catch (error) {
            console.error('加载工厂列表失败:', error);
            showError('加载工厂列表失败');
        }
    }
    
    // 渲染工厂列表
    function renderFactories() {
        const factoryList = document.getElementById('factoryList');
        const emptyState = document.getElementById('emptyState');
        
        if (AppState.factories.length === 0) {
            factoryList.innerHTML = '';
            emptyState.style.display = 'block';
            return;
        }
        
        emptyState.style.display = 'none';
        
        factoryList.innerHTML = AppState.factories.map(factory => `
            <div class="col-md-6 col-lg-4">
                <div class="factory-card">
                    <div class="factory-card-header">
                        <div>
                            <div class="factory-icon">
                                <i class="bi bi-building"></i>
                            </div>
                        </div>
                        <button class="btn btn-sm btn-link text-primary p-0" onclick="editFactory(${factory.id})" title="编辑工厂">
                            <i class="bi bi-pencil-square" style="font-size: 1.2rem;"></i>
                        </button>
                    </div>
                    
                    <h3 class="factory-name">${escapeHtml(factory.name)}</h3>
                    
                    ${factory.location ? `
                        <div class="factory-location">
                            <i class="bi bi-geo-alt"></i>
                            <span>${escapeHtml(factory.location)}</span>
                        </div>
                    ` : ''}
                    
                    ${factory.industry_type ? `
                        <div class="factory-location mt-1">
                            <i class="bi bi-briefcase"></i>
                            <span>${escapeHtml(factory.industry_type)}</span>
                        </div>
                    ` : ''}
                    
                    <div class="factory-location mt-1">
                        <i class="bi bi-lightning"></i>
                        <span>电压等级: ${factory.voltage_level} kV</span>
                    </div>
                    
                    <div class="factory-location mt-1">
                        <i class="bi bi-gear"></i>
                        <span>变压器容量: ${formatNumber(factory.transformer_capacity)} kVA</span>
                    </div>
                    
                    <div class="factory-stats">
                        <div class="stat-item">
                            <span class="stat-label">
                                <i class="bi bi-cash me-1"></i>
                                容量电费
                            </span>
                            <span class="stat-value cost">¥${formatNumber(factory.capacity_fee)}/月</span>
                        </div>
                        
                        <div class="stat-item">
                            <span class="stat-label">
                                <i class="bi bi-lightning-charge me-1"></i>
                                日用电量
                            </span>
                            <span class="stat-value usage">${formatNumber(factory.daily_usage)} kWh/天</span>
                        </div>
                        
                        <div class="stat-item">
                            <span class="stat-label">
                                <i class="bi bi-calendar-check me-1"></i>
                                月工作天数
                            </span>
                            <span class="stat-value">${factory.working_days_per_month} 天</span>
                        </div>
                        
                        <div class="stat-item">
                            <span class="stat-label">
                                <i class="bi bi-lightning-charge me-1"></i>
                                月用电量
                            </span>
                            <span class="stat-value usage">${formatNumber(factory.monthly_usage)} kWh</span>
                        </div>
                    </div>
                    
                    ${factory.work_periods ? `
                        <div class="mt-2">
                            <div class="small text-muted mb-1">
                                <i class="bi bi-clock me-1"></i>工作时间段:
                            </div>
                            <div class="d-flex flex-wrap gap-1">
                                ${JSON.parse(factory.work_periods).map(p => `
                                    <span class="badge bg-secondary">
                                        ${String(p.start).padStart(2, '0')}:00-${String(p.end).padStart(2, '0')}:00
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="factory-actions">
                        <button class="btn btn-sm btn-outline-primary" onclick="viewFactoryDetails(${factory.id})">
                            <i class="bi bi-eye me-1"></i>
                            查看详情
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteFactory(${factory.id}, '${escapeHtml(factory.name)}')">
                            <i class="bi bi-trash me-1"></i>
                            删除
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    // ========================================
    // 工作时间段管理
    // ========================================
    
    // 存储工作时间段
    let workPeriods = [];
    
    // 当前编辑的工厂 ID（null 表示创建新工厂）
    let editingFactoryId = null;
    
    // 添加工作时间段
    window.addWorkPeriod = function() {
        const startSelect = document.getElementById('periodStart');
        const endSelect = document.getElementById('periodEnd');
        
        const start = parseInt(startSelect.value);
        const end = parseInt(endSelect.value);
        
        // 验证
        if (!startSelect.value || !endSelect.value) {
            showError('请选择开始和结束时间');
            return;
        }
        
        if (start >= end) {
            showError('结束时间必须大于开始时间');
            return;
        }
        
        // 检查是否重叠
        for (const period of workPeriods) {
            if ((start >= period.start && start < period.end) || 
                (end > period.start && end <= period.end) ||
                (start <= period.start && end >= period.end)) {
                showError('时间段不能重叠');
                return;
            }
        }
        
        // 添加时间段
        workPeriods.push({ start, end });
        
        // 重置选择器
        startSelect.value = '8';
        endSelect.value = '18';
        
        // 渲染时间段列表
        renderWorkPeriods();
    };
    
    // 删除工作时间段
    window.removeWorkPeriod = function(index) {
        workPeriods.splice(index, 1);
        renderWorkPeriods();
    };
    
    // 渲染工作时间段列表
    function renderWorkPeriods() {
        const container = document.getElementById('workPeriodsList');
        
        if (workPeriods.length === 0) {
            container.innerHTML = '<div class="text-muted small">暂无工作时间段</div>';
            return;
        }
        
        container.innerHTML = workPeriods.map((period, index) => `
            <div class="d-flex align-items-center justify-content-between bg-light p-2 rounded mb-1">
                <span class="small">
                    <i class="bi bi-clock"></i>
                    ${String(period.start).padStart(2, '0')}:00 - ${String(period.end).padStart(2, '0')}:00
                </span>
                <button type="button" class="btn btn-sm btn-link text-danger p-0" onclick="removeWorkPeriod(${index})">
                    <i class="bi bi-x-circle"></i>
                </button>
            </div>
        `).join('');
    }
    
    // 显示创建工厂模态框
    window.showCreateFactoryModal = function() {
        editingFactoryId = null;
        
        const modal = new bootstrap.Modal(document.getElementById('createFactoryModal'));
        
        // 更新标题和按钮
        document.getElementById('factoryModalTitle').innerHTML = '<i class="bi bi-plus-circle me-2"></i>新建工厂';
        const submitBtn = document.getElementById('factorySubmitBtn');
        submitBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>创建';
        submitBtn.onclick = createFactory;
        
        // 重置表单
        document.getElementById('createFactoryForm').reset();
        
        // 重置工作时间段
        workPeriods = [];
        renderWorkPeriods();
        
        modal.show();
    };
    
    // 编辑工厂
    window.editFactory = function(factoryId) {
        const factory = AppState.factories.find(f => f.id === factoryId);
        if (!factory) {
            showError('工厂不存在');
            return;
        }
        
        editingFactoryId = factoryId;
        
        const modal = new bootstrap.Modal(document.getElementById('createFactoryModal'));
        
        // 更新标题和按钮
        document.getElementById('factoryModalTitle').innerHTML = '<i class="bi bi-pencil-square me-2"></i>编辑工厂';
        const submitBtn = document.getElementById('factorySubmitBtn');
        submitBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>保存';
        submitBtn.onclick = updateFactory;
        
        // 填充表单数据
        document.getElementById('factoryName').value = factory.name || '';
        document.getElementById('factoryLocation').value = factory.location || '';
        document.getElementById('industryType').value = factory.industry_type || '';
        document.getElementById('voltageLevel').value = factory.voltage_level || '';
        document.getElementById('transformerCapacity').value = factory.transformer_capacity || '';
        document.getElementById('dailyUsage').value = factory.daily_usage || '';
        document.getElementById('workingDays').value = factory.working_days_per_month || 26;
        
        // 加载工作时间段
        try {
            workPeriods = JSON.parse(factory.work_periods || '[]');
        } catch (e) {
            workPeriods = [];
        }
        renderWorkPeriods();
        
        modal.show();
    };
    
    // 创建工厂
    window.createFactory = async function() {
        const form = document.getElementById('createFactoryForm');
        
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        // 验证工作时间段
        if (workPeriods.length === 0) {
            showError('请至少添加一个工作时间段');
            return;
        }
        
        const factoryData = {
            name: document.getElementById('factoryName').value,
            location: document.getElementById('factoryLocation').value,
            industry_type: document.getElementById('industryType').value,
            voltage_level: parseInt(document.getElementById('voltageLevel').value),
            transformer_capacity: parseFloat(document.getElementById('transformerCapacity').value),
            daily_usage: parseFloat(document.getElementById('dailyUsage').value),
            working_days_per_month: parseInt(document.getElementById('workingDays').value),
            work_periods: JSON.stringify(workPeriods)
        };
        
        try {
            const response = await fetch('/api/factory/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(factoryData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('createFactoryModal'));
                modal.hide();
                
                // 显示成功消息
                showSuccess('工厂创建成功');
                
                // 重新加载工厂列表
                await loadFactories();
            } else {
                showError(data.message || '创建工厂失败');
            }
        } catch (error) {
            console.error('创建工厂失败:', error);
            showError('创建工厂失败');
        }
    };
    
    // 更新工厂
    window.updateFactory = async function() {
        const form = document.getElementById('createFactoryForm');
        
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        // 验证工作时间段
        if (workPeriods.length === 0) {
            showError('请至少添加一个工作时间段');
            return;
        }
        
        const factoryData = {
            name: document.getElementById('factoryName').value,
            location: document.getElementById('factoryLocation').value,
            industry_type: document.getElementById('industryType').value,
            voltage_level: parseInt(document.getElementById('voltageLevel').value),
            transformer_capacity: parseFloat(document.getElementById('transformerCapacity').value),
            daily_usage: parseFloat(document.getElementById('dailyUsage').value),
            working_days_per_month: parseInt(document.getElementById('workingDays').value),
            work_periods: JSON.stringify(workPeriods)
        };
        
        try {
            const response = await fetch(`/api/factory/${editingFactoryId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(factoryData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('createFactoryModal'));
                modal.hide();
                
                // 显示成功消息
                showSuccess('工厂更新成功');
                
                // 重新加载工厂列表
                await loadFactories();
            } else {
                showError(data.message || '更新工厂失败');
            }
        } catch (error) {
            console.error('更新工厂失败:', error);
            showError('更新工厂失败');
        }
    };
    
    // 查看工厂详情
    window.viewFactoryDetails = function(factoryId) {
        // TODO: 实现工厂详情页面
        console.log('查看工厂详情:', factoryId);
        showInfo('工厂详情功能开发中...');
    };
    
    // 删除工厂
    window.deleteFactory = async function(factoryId, factoryName) {
        if (!confirm(`确定要删除工厂"${factoryName}"吗？此操作不可恢复。`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/factory/${factoryId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                showSuccess('工厂删除成功');
                await loadFactories();
            } else {
                showError(data.message || '删除工厂失败');
            }
        } catch (error) {
            console.error('删除工厂失败:', error);
            showError('删除工厂失败');
        }
    };
    
    // ========================================
    // 工具函数
    // ========================================
    
    // HTML 转义
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // 格式化数字
    function formatNumber(num) {
        if (num === null || num === undefined) return '0';
        return parseFloat(num).toLocaleString('zh-CN', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        });
    }
    
    // 显示成功消息
    function showSuccess(message) {
        showToast(message, 'success');
    }
    
    // 显示错误消息
    function showError(message) {
        showToast(message, 'danger');
    }
    
    // 显示信息消息
    function showInfo(message) {
        showToast(message, 'info');
    }
    
    // 显示 Toast 消息
    function showToast(message, type = 'info') {
        // 创建 toast 容器（如果不存在）
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }
        
        // 创建 toast 元素
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${escapeHtml(message)}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 3000
        });
        
        toast.show();
        
        // 移除 toast 元素
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
    
    // ========================================
    // 初始化
    // ========================================
    function init() {
        console.log('🚀 PeakShift Dashboard 初始化...');
        
        // 显示工厂管理视图
        showView('factoryManagement');
        
        // 加载工厂列表
        loadFactories();
        
        console.log('✅ Dashboard 初始化完成');
    }
    
    // DOM 加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
