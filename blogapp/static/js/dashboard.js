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
        const ctx = document.getElementById('priceChart');
        
        // 销毁旧图表
        if (priceChartInstance) {
            priceChartInstance.destroy();
        }
        
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
                maintainAspectRatio: true,
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
        const ctx = document.getElementById('energyPieChart');
        
        // 销毁旧图表
        if (energyPieChartInstance) {
            energyPieChartInstance.destroy();
        }
        
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
                maintainAspectRatio: true,
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
        
        // 计算各时段汇总
        const peakData = hourlyData.filter(h => h.period_type === '高峰');
        const normalData = hourlyData.filter(h => h.period_type === '平时');
        const valleyData = hourlyData.filter(h => h.period_type === '低谷');
        
        const peakUsage = peakData.reduce((sum, h) => sum + h.usage, 0);
        const normalUsage = normalData.reduce((sum, h) => sum + h.usage, 0);
        const valleyUsage = valleyData.reduce((sum, h) => sum + h.usage, 0);
        
        const peakCost = peakData.reduce((sum, h) => sum + h.cost, 0);
        const normalCost = normalData.reduce((sum, h) => sum + h.cost, 0);
        const valleyCost = valleyData.reduce((sum, h) => sum + h.cost, 0);
        
        const html = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-light">
                        <tr>
                            <th>时段类型</th>
                            <th>用电量 (kWh)</th>
                            <th>电价 (元/kWh)</th>
                            <th>电费 (元)</th>
                            <th>占比</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>
                                <span class="badge bg-danger">高峰</span>
                            </td>
                            <td>${formatNumber(peakUsage)}</td>
                            <td>¥${(peakCost / peakUsage).toFixed(4)}</td>
                            <td class="fw-bold">¥${formatNumber(peakCost)}</td>
                            <td>${((peakCost / costAnalysis.total_monthly_cost) * 100).toFixed(1)}%</td>
                        </tr>
                        <tr>
                            <td>
                                <span class="badge bg-warning">平时</span>
                            </td>
                            <td>${formatNumber(normalUsage)}</td>
                            <td>¥${(normalCost / normalUsage).toFixed(4)}</td>
                            <td class="fw-bold">¥${formatNumber(normalCost)}</td>
                            <td>${((normalCost / costAnalysis.total_monthly_cost) * 100).toFixed(1)}%</td>
                        </tr>
                        <tr>
                            <td>
                                <span class="badge bg-success">低谷</span>
                            </td>
                            <td>${formatNumber(valleyUsage)}</td>
                            <td>¥${(valleyCost / valleyUsage).toFixed(4)}</td>
                            <td class="fw-bold">¥${formatNumber(valleyCost)}</td>
                            <td>${((valleyCost / costAnalysis.total_monthly_cost) * 100).toFixed(1)}%</td>
                        </tr>
                        <tr class="table-light fw-bold">
                            <td>容量电费</td>
                            <td>-</td>
                            <td>-</td>
                            <td>¥${formatNumber(costAnalysis.capacity_fee)}</td>
                            <td>${((costAnalysis.capacity_fee / costAnalysis.total_monthly_cost) * 100).toFixed(1)}%</td>
                        </tr>
                        <tr class="table-primary fw-bold">
                            <td>合计</td>
                            <td>${formatNumber(costAnalysis.monthly_usage)}</td>
                            <td>-</td>
                            <td>¥${formatNumber(costAnalysis.total_monthly_cost)}</td>
                            <td>100%</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;
        
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
