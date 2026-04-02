/* ========================================
   PeakShift Dashboard - Single Page Application
   Version: 2.0 - 图表动画已禁用
   ======================================== */

console.log('Dashboard.js v2.0 loaded - Animation disabled');

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
                
                // 如果当前在详情页面，刷新详情页面
                if (AppState.currentView === 'factoryDetails' && AppState.currentFactory) {
                    await viewFactoryDetails(editingFactoryId);
                }
            } else {
                showError(data.message || '更新工厂失败');
            }
        } catch (error) {
            console.error('更新工厂失败:', error);
            showError('更新工厂失败');
        }
    };
    
    // 查看工厂详情
    window.viewFactoryDetails = async function(factoryId) {
        try {
            const response = await fetch(`/api/factory/${factoryId}/details`);
            const data = await response.json();
            
            if (data.success) {
                AppState.currentFactory = data;
                renderFactoryDetails(data);
                showView('factoryDetails');
            } else {
                showError(data.message || '加载工厂详情失败');
            }
        } catch (error) {
            console.error('加载工厂详情失败:', error);
            showError('加载工厂详情失败');
        }
    };
    
    // 返回工厂管理页面
    window.showFactoryManagement = function() {
        showView('factoryManagement');
        loadFactories();
    };
    
    // 编辑当前工厂
    window.editCurrentFactory = function() {
        if (AppState.currentFactory && AppState.currentFactory.factory) {
            const factoryId = AppState.currentFactory.factory.id;
            editFactory(factoryId);
        }
    };
    
    // 渲染工厂详情
    function renderFactoryDetails(data) {
        const factory = data.factory;
        const costAnalysis = data.cost_analysis;
        
        // 基本信息
        document.getElementById('detailFactoryName').textContent = factory.name;
        document.getElementById('detailFactoryLocation').textContent = factory.location || '-';
        document.getElementById('detailFactoryIndustry').textContent = factory.industry_type || '-';
        document.getElementById('detailVoltageLevel').textContent = `${factory.voltage_level} kV`;
        document.getElementById('detailTransformerCapacity').textContent = `${formatNumber(factory.transformer_capacity)} kVA`;
        document.getElementById('detailDailyUsage').textContent = `${formatNumber(factory.daily_usage)} kWh`;
        document.getElementById('detailWorkingDays').textContent = `${factory.working_days_per_month} 天`;
        
        // 核心数据统计
        document.getElementById('statTodayUsage').textContent = formatNumber(costAnalysis.daily_usage);
        document.getElementById('statMonthCost').textContent = formatNumber(costAnalysis.total_monthly_cost);
        // 使用队友写的 carbon_emission 属性
        document.getElementById('statCarbonEmission').textContent = formatNumber(costAnalysis.carbon_emission);
        
        // 节省潜力 - 等待后端实现
        // TODO: 调用后端 API /api/factory/<id>/optimization?mode=cost 或 mode=carbon
        document.getElementById('statSavingPotential').innerHTML = '<span class="text-muted small">待后端实现</span>';
        document.getElementById('statSavingUnit').textContent = '-';
        
        // 渲染图表
        renderPriceChart(costAnalysis.hourly_breakdown);
        renderEnergyPieChart(costAnalysis.hourly_breakdown);
        
        // 渲染成本报告
        renderCostReport(costAnalysis);
    }
    
    // 切换优化模式（省钱/减排）
    window.switchOptimizationMode = async function(mode) {
        if (!AppState.currentFactory || !AppState.currentFactory.factory) {
            return;
        }
        
        const factoryId = AppState.currentFactory.factory.id;
        
        // TODO: 调用后端 API 获取优化数据
        // const response = await fetch(`/api/factory/${factoryId}/optimization?mode=${mode}`);
        // const data = await response.json();
        
        // 临时占位
        const valueElement = document.getElementById('statSavingPotential');
        const unitElement = document.getElementById('statSavingUnit');
        
        if (mode === 'cost') {
            valueElement.innerHTML = '<span class="text-muted small">待后端实现</span>';
            unitElement.textContent = '元/月';
        } else {
            valueElement.innerHTML = '<span class="text-muted small">待后端实现</span>';
            unitElement.textContent = 'kg CO₂/月';
        }
    };
    
    // 渲染电价曲线图
    let priceChartInstance = null;
    function renderPriceChart(hourlyData) {
        console.log('渲染折线图 - 动画已启用');
        const ctx = document.getElementById('priceChart');
        
        // 销毁旧图表
        if (priceChartInstance) {
            priceChartInstance.destroy();
        }
        
        // 设置 Canvas 透明背景
        ctx.style.backgroundColor = 'transparent';
        
        const labels = hourlyData.map(h => `${String(h.hour).padStart(2, '0')}:00`);
        
        // 获取价格对比数据
        const priceComparison = AppState.currentFactory.cost_analysis.price_comparison;
        const agentPrices = hourlyData.map(h => priceComparison.agent_prices[h.hour]);
        const gridPrices = hourlyData.map(h => priceComparison.grid_prices[h.hour]);
        
        priceChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '代理公司价格 (含代理费)',
                    data: agentPrices,
                    borderColor: 'rgb(14, 165, 233)',
                    backgroundColor: 'rgba(14, 165, 233, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 6
                }, {
                    label: '电网价格',
                    data: gridPrices,
                    borderColor: 'rgb(245, 158, 11)',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 800,
                    easing: 'easeOutQuart'
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            font: {
                                size: 13,
                                weight: '600'
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const value = context.parsed.y;
                                return `${label}: ¥${value.toFixed(4)}/kWh`;
                            },
                            afterLabel: function(context) {
                                const index = context.dataIndex;
                                return `时段: ${hourlyData[index].period_type}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: '电价 (元/kWh)',
                            font: {
                                size: 13,
                                weight: '600'
                            }
                        },
                        ticks: {
                            callback: function(value) {
                                return '¥' + value.toFixed(2);
                            }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '时间',
                            font: {
                                size: 13,
                                weight: '600'
                            }
                        }
                    }
                }
            }
        });
    }
    
    // 渲染能源结构饼图
    let energyPieChartInstance = null;
    function renderEnergyPieChart(hourlyData) {
        console.log('渲染饼图 - 动画已启用');
        const ctx = document.getElementById('energyPieChart');
        
        // 销毁旧图表
        if (energyPieChartInstance) {
            energyPieChartInstance.destroy();
        }
        
        // 设置 Canvas 透明背景
        ctx.style.backgroundColor = 'transparent';
        
        // 计算各时段用电量
        const peakUsage = hourlyData.filter(h => h.period_type === '高峰').reduce((sum, h) => sum + h.usage, 0);
        const normalUsage = hourlyData.filter(h => h.period_type === '平时').reduce((sum, h) => sum + h.usage, 0);
        const valleyUsage = hourlyData.filter(h => h.period_type === '低谷').reduce((sum, h) => sum + h.usage, 0);
        
        energyPieChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['高峰', '平时', '低谷'],
                datasets: [{
                    data: [peakUsage, normalUsage, valleyUsage],
                    backgroundColor: [
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(16, 185, 129, 0.8)'
                    ],
                    borderColor: [
                        'rgb(239, 68, 68)',
                        'rgb(245, 158, 11)',
                        'rgb(16, 185, 129)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 800,
                    easing: 'easeOutQuart'
                },
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${formatNumber(value)} kWh (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // 渲染成本报告
    function renderCostReport(costAnalysis) {
        const container = document.getElementById('costReportContent');
        
        const hourlyData = costAnalysis.hourly_breakdown;
        const monthDays = costAnalysis.month_days;
        
        // 计算各时段汇总（hourly_breakdown 是每日数据，需要乘以工作天数）
        const peakData = hourlyData.filter(h => h.period_type === '高峰');
        const normalData = hourlyData.filter(h => h.period_type === '平时');
        const valleyData = hourlyData.filter(h => h.period_type === '低谷');
        
        const peakUsage = peakData.reduce((sum, h) => sum + h.usage, 0) * monthDays;
        const normalUsage = normalData.reduce((sum, h) => sum + h.usage, 0) * monthDays;
        const valleyUsage = valleyData.reduce((sum, h) => sum + h.usage, 0) * monthDays;
        
        const peakCost = peakData.reduce((sum, h) => sum + h.cost, 0) * monthDays;
        const normalCost = normalData.reduce((sum, h) => sum + h.cost, 0) * monthDays;
        const valleyCost = valleyData.reduce((sum, h) => sum + h.cost, 0) * monthDays;
        
        // 电能费总和（不含容量费）
        const totalEnergyCost = costAnalysis.monthly_energy_cost;
        
        // 计算总用电量
        const totalUsage = peakUsage + normalUsage + valleyUsage;
        
        const html = `
            <table style="width: 100%; border-collapse: collapse; font-size: 0.875rem;">
                <thead>
                    <tr style="background: transparent;">
                        <th style="padding: 0.75rem; text-align: center; border-bottom: 2px solid rgba(14, 165, 233, 0.2);">时段类型</th>
                        <th style="padding: 0.75rem; text-align: center; border-bottom: 2px solid rgba(14, 165, 233, 0.2);">用电量 (kWh)</th>
                        <th style="padding: 0.75rem; text-align: center; border-bottom: 2px solid rgba(14, 165, 233, 0.2);">电价 (元/kWh)</th>
                        <th style="padding: 0.75rem; text-align: center; border-bottom: 2px solid rgba(14, 165, 233, 0.2);">电费 (元)</th>
                        <th style="padding: 0.75rem; text-align: center; border-bottom: 2px solid rgba(14, 165, 233, 0.2);">占比</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 0.75rem; text-align: center; color: #dc2626; font-weight: 700; font-size: 0.9375rem;">高峰</td>
                        <td style="padding: 0.75rem; text-align: center;">${formatNumber(peakUsage)}</td>
                        <td style="padding: 0.75rem; text-align: center;">¥${peakUsage > 0 ? (peakCost / peakUsage).toFixed(4) : '0.0000'}</td>
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">¥${formatNumber(peakCost)}</td>
                        <td style="padding: 0.75rem; text-align: center;">${totalEnergyCost > 0 ? ((peakCost / totalEnergyCost) * 100).toFixed(1) : '0.0'}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.75rem; text-align: center; color: #f59e0b; font-weight: 700; font-size: 0.9375rem;">平时</td>
                        <td style="padding: 0.75rem; text-align: center;">${formatNumber(normalUsage)}</td>
                        <td style="padding: 0.75rem; text-align: center;">¥${normalUsage > 0 ? (normalCost / normalUsage).toFixed(4) : '0.0000'}</td>
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">¥${formatNumber(normalCost)}</td>
                        <td style="padding: 0.75rem; text-align: center;">${totalEnergyCost > 0 ? ((normalCost / totalEnergyCost) * 100).toFixed(1) : '0.0'}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.75rem; text-align: center; color: #10b981; font-weight: 700; font-size: 0.9375rem;">低谷</td>
                        <td style="padding: 0.75rem; text-align: center;">${formatNumber(valleyUsage)}</td>
                        <td style="padding: 0.75rem; text-align: center;">¥${valleyUsage > 0 ? (valleyCost / valleyUsage).toFixed(4) : '0.0000'}</td>
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">¥${formatNumber(valleyCost)}</td>
                        <td style="padding: 0.75rem; text-align: center;">${totalEnergyCost > 0 ? ((valleyCost / totalEnergyCost) * 100).toFixed(1) : '0.0'}%</td>
                    </tr>
                    <tr style="background: transparent;">
                        <td colspan="3" style="padding: 0.75rem; text-align: left; font-weight: bold;">容量电费</td>
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">¥${formatNumber(costAnalysis.capacity_fee)}</td>
                        <td style="padding: 0.75rem; text-align: center;">-</td>
                    </tr>
                    <tr style="background: transparent;">
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">合计</td>
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">${formatNumber(totalUsage)}</td>
                        <td style="padding: 0.75rem; text-align: center;">-</td>
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">¥${formatNumber(costAnalysis.total_monthly_cost)}</td>
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">100%</td>
                    </tr>
                </tbody>
            </table>
        `;
        
        console.log('表格 HTML:', html);
        container.innerHTML = html;
    }
    
    
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
    // 性能监测和设置
    // ========================================
    
    // FPS 监测
    const FPSMonitor = {
        frames: [],
        lastTime: performance.now(),
        rafId: null,
        isRunning: false,
        
        start() {
            if (this.isRunning) return;
            this.isRunning = true;
            this.frames = [];
            this.lastTime = performance.now();
            this.tick();
        },
        
        stop() {
            this.isRunning = false;
            if (this.rafId) {
                cancelAnimationFrame(this.rafId);
                this.rafId = null;
            }
        },
        
        tick() {
            if (!this.isRunning) return;
            
            const now = performance.now();
            const delta = now - this.lastTime;
            this.lastTime = now;
            
            // 记录 FPS（1000ms / delta）
            if (delta > 0) {
                const fps = 1000 / delta;
                this.frames.push(fps);
                
                // 基准测试时不限制帧数，实时显示时只保留最近 60 帧
                if (!this.isBenchmarking && this.frames.length > 60) {
                    this.frames.shift();
                }
            }
            
            this.rafId = requestAnimationFrame(() => this.tick());
        },
        
        getAverageFPS() {
            if (this.frames.length === 0) return 0;
            const sum = this.frames.reduce((a, b) => a + b, 0);
            return Math.round(sum / this.frames.length);
        },
        
        getMinFPS() {
            if (this.frames.length === 0) return 0;
            return Math.round(Math.min(...this.frames));
        },
        
        getCurrentFPS() {
            if (this.frames.length === 0) return 0;
            // 取最近 10 帧的平均值
            const recent = this.frames.slice(-10);
            const sum = recent.reduce((a, b) => a + b, 0);
            return Math.round(sum / recent.length);
        },
        
        reset() {
            this.frames = [];
            this.lastTime = performance.now();
        }
    };
    
    // 打开设置面板
    window.openSettings = function() {
        const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
        
        // 加载当前设置
        const currentMode = localStorage.getItem('uiMode') || 'full';
        document.getElementById('uiMode' + currentMode.charAt(0).toUpperCase() + currentMode.slice(1)).checked = true;
        
        const showFps = localStorage.getItem('showFps') === 'true';
        document.getElementById('showFpsToggle').checked = showFps;
        
        modal.show();
    };
    
    // 运行基准测试
    window.runBenchmark = async function() {
        const btn = document.getElementById('benchmarkBtn');
        const resultDiv = document.getElementById('benchmarkResult');
        const alertDiv = document.getElementById('benchmarkAlert');
        
        // 禁用按钮
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>测试中...';
        
        // 隐藏之前的结果
        resultDiv.style.display = 'none';
        
        // 保存当前 UI 模式
        const wasLiteMode = document.body.classList.contains('ui-lite');
        
        // 强制切换到满血版进行测试
        if (wasLiteMode) {
            document.body.classList.remove('ui-lite');
            document.body.classList.add('ui-full');
        }
        
        // 等待 100ms 让样式生效
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // 标记为基准测试模式
        FPSMonitor.isBenchmarking = true;
        FPSMonitor.reset();
        FPSMonitor.start();
        
        // 强制触发所有页面元素的悬停效果
        const allCards = document.querySelectorAll('.stat-card, .factory-card, .card');
        let hoverIndex = 0;
        const hoverInterval = setInterval(() => {
            // 移除所有 hover
            allCards.forEach(card => {
                card.style.transform = '';
                card.style.boxShadow = '';
            });
            
            // 强制触发当前卡片的 hover 效果
            if (allCards[hoverIndex]) {
                const card = allCards[hoverIndex];
                if (card.classList.contains('stat-card')) {
                    card.style.transform = 'translateY(-8px) scale(1.02)';
                    card.style.boxShadow = '0 20px 60px rgba(99, 102, 241, 0.3), 0 0 40px rgba(99, 102, 241, 0.2)';
                } else if (card.classList.contains('factory-card')) {
                    card.style.transform = 'translateY(-8px) scale(1.02)';
                    card.style.boxShadow = '0 20px 60px rgba(99, 102, 241, 0.25), 0 0 40px rgba(99, 102, 241, 0.15)';
                } else {
                    card.style.transform = 'translateY(-5px)';
                    card.style.boxShadow = '0 15px 40px rgba(0, 0, 0, 0.15)';
                }
            }
            hoverIndex = (hoverIndex + 1) % allCards.length;
        }, 300); // 每 0.3 秒切换一个卡片
        
        // 测试 10 秒
        await new Promise(resolve => setTimeout(resolve, 10000));
        
        // 停止监测和悬停效果
        FPSMonitor.stop();
        FPSMonitor.isBenchmarking = false;
        clearInterval(hoverInterval);
        
        // 恢复所有卡片样式
        allCards.forEach(card => {
            card.style.transform = '';
            card.style.boxShadow = '';
        });
        
        // 恢复原来的 UI 模式
        if (wasLiteMode) {
            document.body.classList.remove('ui-full');
            document.body.classList.add('ui-lite');
        }
        
        // 计算平均 FPS 和最低 FPS
        const avgFps = FPSMonitor.getAverageFPS();
        const minFps = FPSMonitor.getMinFPS();
        
        // 显示结果
        document.getElementById('avgFps').textContent = avgFps;
        document.getElementById('minFps').textContent = minFps;
        
        let recommendation = '';
        let alertClass = '';
        
        // 根据最低 FPS 来判断（最坏情况）
        if (minFps >= 50) {
            recommendation = '✅ 设备性能优秀，推荐使用满血版 UI';
            alertClass = 'alert-success';
        } else if (minFps >= 30) {
            recommendation = '⚠️ 设备性能中等，可使用满血版但可能有轻微卡顿';
            alertClass = 'alert-warning';
        } else {
            recommendation = '❌ 设备性能较低，强烈推荐使用精简版 UI';
            alertClass = 'alert-danger';
        }
        
        document.getElementById('recommendation').textContent = recommendation;
        alertDiv.className = 'alert ' + alertClass;
        
        resultDiv.style.display = 'block';
        
        // 恢复按钮
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-play-circle me-1"></i>重新测试';
    };
    
    // 切换 FPS 显示
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
    
    // 更新 FPS 显示
    function updateFpsDisplay() {
        if (!FPSMonitor.isRunning) return;
        
        const fps = FPSMonitor.getCurrentFPS();
        document.getElementById('fpsValue').textContent = fps;
        
        setTimeout(updateFpsDisplay, 500); // 每 0.5 秒更新一次
    }
    
    // 保存设置
    window.saveSettings = function() {
        const uiMode = document.querySelector('input[name="uiMode"]:checked').value;
        const showFps = document.getElementById('showFpsToggle').checked;
        
        // 保存到 localStorage
        localStorage.setItem('uiMode', uiMode);
        localStorage.setItem('showFps', showFps);
        
        // 应用 UI 模式
        applyUIMode(uiMode);
        
        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
        modal.hide();
        
        showSuccess('设置已保存');
    };
    
    // 应用 UI 模式
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
    // 初始化
    // ========================================
    function init() {
        console.log('🚀 PeakShift Dashboard 初始化...');
        
        // 显示工厂管理视图
        showView('factoryManagement');
        
        // 加载工厂列表
        loadFactories();
        
        // 加载保存的设置
        const savedMode = localStorage.getItem('uiMode') || 'full';
        applyUIMode(savedMode);
        
        const showFps = localStorage.getItem('showFps') === 'true';
        if (showFps) {
            document.getElementById('fpsDisplay').style.display = 'block';
            FPSMonitor.start();
            updateFpsDisplay();
        }
        
        console.log('✅ Dashboard 初始化完成');
    }
    
    // DOM 加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
