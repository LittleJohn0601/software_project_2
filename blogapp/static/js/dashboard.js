/* ========================================
   PeakShift Dashboard - Single Page Application
   Version: 2.0 - Chart animations disabled
   ======================================== */

console.log('Dashboard.js v2.0 loaded - Animation disabled');

(function() {
    'use strict';
    
    // ========================================
    // Global state management
    // ========================================
    const AppState = {
        currentView: 'factoryManagement',
        factories: [],
        currentFactory: null
    };
    
    // ========================================
    // View switching
    // ========================================
    function showView(viewName) {
        // Hide all views
        document.querySelectorAll('.view-container').forEach(view => {
            view.classList.remove('active');
        });
        
        // Show target view
        const targetView = document.getElementById(viewName + 'View');
        if (targetView) {
            targetView.classList.add('active');
            AppState.currentView = viewName;
        }
    }
    
    // ========================================
    // Factory management features
    // ========================================
    
    // Load factory list
    async function loadFactories() {
        try {
            // Add timestamp to prevent caching
            const response = await fetch(`/api/factories?t=${Date.now()}`, {
                credentials: 'same-origin'
            });
            const data = await response.json();
            
            if (data.success) {
                AppState.factories = data.factories;
                renderFactories();
            } else {
                showError('Failed to load factory list');
            }
        } catch (error) {
            console.error('Failed to load factory list:', error);
            showError('Failed to load factory list');
        }
    }
    
    // Render factory list
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
            <div class="col-xl-4 col-lg-6 col-md-12">
                <div class="factory-card">
                    <div class="factory-card-header">
                        <div>
                            <div class="factory-icon">
                                <i class="bi bi-building"></i>
                            </div>
                        </div>
                        <button class="btn btn-sm btn-link text-primary p-0" onclick="editFactory(${factory.id})" title="Edit factory">
                            <i class="bi bi-pencil-square" style="font-size: 1.1rem;"></i>
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
                        <span>Voltage: ${factory.voltage_level} kV</span>
                    </div>
                    
                    <div class="factory-location mt-1">
                        <i class="bi bi-gear"></i>
                        <span>Capacity: ${formatNumber(factory.transformer_capacity)} kVA</span>
                    </div>
                    
                    <div class="factory-stats">
                        <div class="stat-item">
                            <span class="stat-label">
                                <i class="bi bi-cash"></i>
                                Capacity fee
                            </span>
                            <span class="stat-value cost">¥${formatNumber(factory.capacity_fee)}/mo</span>
                        </div>
                        
                        <div class="stat-item">
                            <span class="stat-label">
                                <i class="bi bi-lightning-charge"></i>
                                Daily usage
                            </span>
                            <span class="stat-value usage">${formatNumber(factory.daily_usage)} kWh</span>
                        </div>
                        
                        <div class="stat-item">
                            <span class="stat-label">
                                <i class="bi bi-calendar-check"></i>
                                Working days
                            </span>
                            <span class="stat-value">${factory.working_days_per_month} days</span>
                        </div>
                        
                        <div class="stat-item">
                            <span class="stat-label">
                                <i class="bi bi-lightning-charge"></i>
                                Monthly usage
                            </span>
                            <span class="stat-value usage">${formatNumber(factory.monthly_usage)} kWh</span>
                        </div>
                    </div>
                    
                    ${factory.work_periods ? `
                        <div class="mt-2" style="margin-top: 0.375rem !important;">
                            <div class="text-muted mb-1" style="font-size: 0.6875rem; margin-bottom: 0.25rem !important;">
                                <i class="bi bi-clock"></i> Work periods:
                            </div>
                            <div class="d-flex flex-wrap gap-1">
                                ${JSON.parse(factory.work_periods).map(p => `
                                    <span class="badge bg-secondary" style="font-size: 0.625rem; padding: 0.125rem 0.375rem;">
                                        ${String(p.start).padStart(2, '0')}:00-${String(p.end).padStart(2, '0')}:00
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="factory-actions">
                        <button class="btn btn-sm btn-outline-primary" onclick="viewFactoryDetails(${factory.id})">
                            <i class="bi bi-eye me-1"></i>
                            View details
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteFactory(${factory.id}, '${escapeHtml(factory.name)}')">
                            <i class="bi bi-trash me-1"></i>
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    // ========================================
    // Work period management
    // ========================================
    
    // Store work periods
    let workPeriods = [];
    
    // Current edited factory ID (null means creating a new factory)
    let editingFactoryId = null;
    
    // Add work period
    window.addWorkPeriod = function() {
        const startSelect = document.getElementById('periodStart');
        const endSelect = document.getElementById('periodEnd');
        
        const start = parseInt(startSelect.value);
        const end = parseInt(endSelect.value);
        
        // Validation
        if (!startSelect.value || !endSelect.value) {
            showError('Please select a start and end time');
            return;
        }
        
        if (start >= end) {
            showError('End time must be later than start time');
            return;
        }
        
        // Check for overlap
        for (const period of workPeriods) {
            if ((start >= period.start && start < period.end) || 
                (end > period.start && end <= period.end) ||
                (start <= period.start && end >= period.end)) {
                showError('Time periods cannot overlap');
                return;
            }
        }
        
        // Add time period
        workPeriods.push({ start, end });
        
        // Reset selectors
        startSelect.value = '8';
        endSelect.value = '18';
        
        // Render period list
        renderWorkPeriods();
    };
    
    // Remove work period
    window.removeWorkPeriod = function(index) {
        workPeriods.splice(index, 1);
        renderWorkPeriods();
    };
    
    // Render work period list
    function renderWorkPeriods() {
        const container = document.getElementById('workPeriodsList');
        
        if (workPeriods.length === 0) {
            container.innerHTML = '<div class="text-muted small">No work periods added yet</div>';
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
    
    // Show create factory modal
    window.showCreateFactoryModal = function() {
        editingFactoryId = null;
        
        const modal = new bootstrap.Modal(document.getElementById('createFactoryModal'));
        
        // Update title and button
        document.getElementById('factoryModalTitle').innerHTML = '<i class="bi bi-plus-circle me-2"></i>New Factory';
        const submitBtn = document.getElementById('factorySubmitBtn');
        submitBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Create';
        submitBtn.onclick = createFactory;
        
        // Reset form
        document.getElementById('createFactoryForm').reset();
        
        // Reset work periods
        workPeriods = [];
        renderWorkPeriods();
        
        modal.show();
    };
    
    // Edit factory
    window.editFactory = function(factoryId) {
        const factory = AppState.factories.find(f => f.id === factoryId);
        if (!factory) {
            showError('Factory not found');
            return;
        }
        
        editingFactoryId = factoryId;
        
        const modal = new bootstrap.Modal(document.getElementById('createFactoryModal'));
        
        // Update title and button
        document.getElementById('factoryModalTitle').innerHTML = '<i class="bi bi-pencil-square me-2"></i>Edit Factory';
        const submitBtn = document.getElementById('factorySubmitBtn');
        submitBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Save';
        submitBtn.onclick = updateFactory;
        
        // Fill form data
        document.getElementById('factoryName').value = factory.name || '';
        document.getElementById('factoryLocation').value = factory.location || '';
        document.getElementById('industryType').value = factory.industry_type || '';
        document.getElementById('voltageLevel').value = factory.voltage_level || '';
        document.getElementById('transformerCapacity').value = factory.transformer_capacity || '';
        document.getElementById('dailyUsage').value = factory.daily_usage || '';
        document.getElementById('workingDays').value = factory.working_days_per_month || 26;
        
        // Load work periods
        try {
            workPeriods = JSON.parse(factory.work_periods || '[]');
        } catch (e) {
            workPeriods = [];
        }
        renderWorkPeriods();
        
        modal.show();
    };
    
    // Create factory
    window.createFactory = async function() {
        const form = document.getElementById('createFactoryForm');
        
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        // Validate work periods
        if (workPeriods.length === 0) {
            showError('Please add at least one work period');
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
                credentials: 'same-origin',
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(factoryData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('createFactoryModal'));
                modal.hide();
                
                // Show success message
                showSuccess('Factory created successfully');
                
                // Reload factory list
                await loadFactories();
            } else {
                showError(data.message || 'Failed to create factory');
            }
        } catch (error) {
            console.error('Failed to create factory:', error);
            showError('Failed to create factory');
        }
    };
    
    // Update factory
    window.updateFactory = async function() {
        const form = document.getElementById('createFactoryForm');
        
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        // Validate work periods
        if (workPeriods.length === 0) {
            showError('Please add at least one work period');
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
                credentials: 'same-origin',
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(factoryData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('createFactoryModal'));
                modal.hide();
                
                // Show success message
                showSuccess('Factory updated successfully');
                
                // Always reload factory list
                await loadFactories();
                
                // If currently on the details page, refresh details (regardless of whether the edited factory is the current one)
                if (AppState.currentView === 'factoryDetails') {
                    // If the edited factory is currently being viewed, refresh its details
                    if (AppState.currentFactory && AppState.currentFactory.factory.id === editingFactoryId) {
                        await viewFactoryDetails(editingFactoryId);
                    }
                    // If a different factory was edited, update the list data for consistency
                }
            } else {
                showError(data.message || 'Failed to update factory');
            }
        } catch (error) {
            console.error('Failed to update factory:', error);
            showError('Failed to update factory');
        }
    };
    
    // View factory details
    window.viewFactoryDetails = async function(factoryId) {
        try {
            // Add timestamp to prevent caching
            const response = await fetch(`/api/factory/${factoryId}/details?t=${Date.now()}`, {
                credentials: 'same-origin'
            });
            const data = await response.json();
            
            if (data.success) {
                AppState.currentFactory = data;
                renderFactoryDetails(data);
                showView('factoryDetails');
                document.getElementById('currentFactoryId').value = factoryId;
            } else {
                showError(data.message || 'Failed to load factory details');
            }
        } catch (error) {
            console.error('Failed to load factory details:', error);
            showError('Failed to load factory details');
        }
    };
    
    // Return to factory management page
    window.showFactoryManagement = function() {
        showView('factoryManagement');
        loadFactories();
    };
    
    // Edit current factory
    window.editCurrentFactory = function() {
        if (AppState.currentFactory && AppState.currentFactory.factory) {
            const factoryId = AppState.currentFactory.factory.id;
            editFactory(factoryId);
        }
    };
    
    // Render factory details
    function renderFactoryDetails(data) {
        const factory = data.factory;
        const costAnalysis = data.cost_analysis;
        
        // Basic information
        document.getElementById('detailFactoryName').textContent = factory.name;
        document.getElementById('detailFactoryLocation').textContent = factory.location || '-';
        document.getElementById('detailFactoryIndustry').textContent = factory.industry_type || '-';
        document.getElementById('detailVoltageLevel').textContent = `${factory.voltage_level} kV`;
        document.getElementById('detailTransformerCapacity').textContent = `${formatNumber(factory.transformer_capacity)} kVA`;
        document.getElementById('detailDailyUsage').textContent = `${formatNumber(factory.daily_usage)} kWh`;
        document.getElementById('detailWorkingDays').textContent = `${factory.working_days_per_month} days`;
        
        // Key metrics
        document.getElementById('statTodayUsage').textContent = formatNumber(costAnalysis.daily_usage);
        document.getElementById('statMonthCost').textContent = formatNumber(costAnalysis.total_monthly_cost);
        // Using teammate's carbon_emission property
        document.getElementById('statCarbonEmission').textContent = formatNumber(costAnalysis.carbon_emission);
        
        // Saving potential - call backend API (default cost-saving mode)
        switchOptimizationMode('cost');
        
        // Load optimization suggestions
        loadOptimizationSuggestions(factory.id);

        loadEfficiencyBenchmark(factory.id);
        // Load green power guide\
        loadGreenPowerGuide(factory.id);

        loadEquipmentRecommendations(factory.id);
        
        // Render charts
        renderPriceChart(costAnalysis.hourly_breakdown);
        renderEnergyPieChart(costAnalysis.hourly_breakdown);
        
        // Render cost report
        renderCostReport(costAnalysis);
    }
    
    // Load optimization suggestions
    async function loadOptimizationSuggestions(factoryId) {
        const container = document.getElementById('optimizationContent');
        
        try {
            const response = await fetch(`/api/factory/${factoryId}/suggestions?t=${Date.now()}`, {
                credentials: 'same-origin'
            });
            const data = await response.json();
            
            if (data.success && data.suggestions && data.suggestions.length > 0) {
                let html = '';
                
                // Add photovoltaic comparison summary if available
                if (data.summary && data.summary.photovoltaic_comparison) {
                    const pv = data.summary.photovoltaic_comparison;
                    html += `
                        <div class="mb-3 p-3" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%); border-radius: 12px; border: 2px solid rgba(16, 185, 129, 0.3);">
                            <div class="d-flex align-items-center mb-2">
                                <i class="bi bi-sun-fill me-2" style="font-size: 1.25rem; color: #f59e0b;"></i>
                                <h6 class="mb-0" style="font-size: 1rem; font-weight: 600;">Photovoltaic Power Comparison</h6>
                            </div>
                            <div class="row g-3">
                                <div class="col-md-4">
                                    <div class="text-center p-2" style="background: rgba(255, 255, 255, 0.6); border-radius: 8px;">
                                        <div class="small text-muted mb-1">Current Grid Carbon</div>
                                        <div style="font-size: 1.125rem; font-weight: 600; color: #ef4444;">
                                            ${formatNumber(pv.current_carbon)} kg CO₂
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="text-center p-2" style="background: rgba(255, 255, 255, 0.6); border-radius: 8px;">
                                        <div class="small text-muted mb-1">With Photovoltaic</div>
                                        <div style="font-size: 1.125rem; font-weight: 600; color: #10b981;">
                                            ${formatNumber(pv.pv_carbon)} kg CO₂
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="text-center p-2" style="background: rgba(255, 255, 255, 0.6); border-radius: 8px;">
                                        <div class="small text-muted mb-1">Reduction Potential</div>
                                        <div style="font-size: 1.125rem; font-weight: 600; color: #3b82f6;">
                                            ${formatNumber(pv.carbon_reduction)} kg CO₂
                                            <span class="small" style="color: #10b981;">(${pv.reduction_percentage}%)</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }
                
                // Render suggestion list
                html += data.suggestions.map((suggestion, index) => `
                    <div class="suggestion-item mb-3 p-3" style="background: rgba(255, 255, 255, 0.5); border-radius: 12px; border-left: 4px solid ${
                        suggestion.impact === 'high' ? '#ef4444' : 
                        suggestion.impact === 'medium' ? '#f59e0b' : '#10b981'
                    };">
                        <div class="d-flex align-items-start justify-content-between mb-2">
                            <h6 class="mb-0" style="font-size: 0.9375rem; font-weight: 600;">
                                <i class="bi bi-lightbulb-fill me-2" style="color: ${
                                    suggestion.impact === 'high' ? '#ef4444' : 
                                    suggestion.impact === 'medium' ? '#f59e0b' : '#10b981'
                                };"></i>
                                ${suggestion.title}
                            </h6>
                            <span class="badge" style="background: ${
                                suggestion.impact === 'high' ? '#ef4444' : 
                                suggestion.impact === 'medium' ? '#f59e0b' : '#10b981'
                            }; font-size: 0.75rem;">
                                ${suggestion.impact === 'high' ? 'High impact' : 
                                  suggestion.impact === 'medium' ? 'Medium impact' : 'Low impact'}
                            </span>
                        </div>
                        <p class="text-muted mb-2" style="font-size: 0.875rem;">${suggestion.description}</p>
                        ${suggestion.action_items && suggestion.action_items.length > 0 ? `
                            <div class="mt-2">
                                <div class="small text-muted mb-1">Action recommendations:</div>
                                <ul class="small mb-0" style="padding-left: 1.25rem;">
                                    ${suggestion.action_items.map(item => `<li>${item}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                `).join('');
                
                container.innerHTML = html;
            } else {
                // No suggestions
                container.innerHTML = `
                    <div class="text-center py-4 text-muted">
                        <i class="bi bi-check-circle" style="font-size: 2.5rem; color: #10b981;"></i>
                        <p class="mt-2 mb-0" style="font-size: 0.9375rem;">The current power plan is already well optimized!</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Failed to load optimization suggestions:', error);
            container.innerHTML = `
                <div class="alert alert-warning" role="alert" style="font-size: 0.875rem;">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Failed to load optimization suggestions. Please try again later.
                </div>
            `;
        }
    }
    
    // Switch optimization mode (cost/emissions)
    window.switchOptimizationMode = async function(mode) {
        if (!AppState.currentFactory || !AppState.currentFactory.factory) {
            return;
        }
        
        const factoryId = AppState.currentFactory.factory.id;
        
        try {
            // Call backend API to get optimization data
            const response = await fetch(`/api/factory/${factoryId}/optimization?mode=${mode}&t=${Date.now()}`, {
                credentials: 'same-origin'
            });
            const data = await response.json();
            
            const valueElement = document.getElementById('statSavingPotential');
            const unitElement = document.getElementById('statSavingUnit');
            
            if (data.success && data.saving_potential) {
                // Show saving potential
                valueElement.textContent = formatNumber(data.saving_potential.value);
                unitElement.textContent = data.saving_potential.unit;
            } else {
                // Show error or no data
                valueElement.innerHTML = '<span class="text-muted small">No data available</span>';
                unitElement.textContent = mode === 'cost' ? 'CNY/month' : 'kg CO₂/month';
            }
        } catch (error) {
            console.error('Failed to get optimization data:', error);
            const valueElement = document.getElementById('statSavingPotential');
            const unitElement = document.getElementById('statSavingUnit');
            valueElement.innerHTML = '<span class="text-muted small">Loading failed</span>';
            unitElement.textContent = mode === 'cost' ? 'CNY/month' : 'kg CO₂/month';
        }
    };
    
    // Render price line chart
    let priceChartInstance = null;
    function renderPriceChart(hourlyData) {
        console.log('Rendering line chart - animation enabled');
        const ctx = document.getElementById('priceChart');
        
        // Destroy old chart
        if (priceChartInstance) {
            priceChartInstance.destroy();
        }
        
        // Set canvas transparent background
        ctx.style.backgroundColor = 'transparent';
        
        const labels = hourlyData.map(h => `${String(h.hour).padStart(2, '0')}:00`);
        
        // Get price comparison data
        const priceComparison = AppState.currentFactory.cost_analysis.price_comparison;
        const agentPrices = hourlyData.map(h => priceComparison.agent_prices[h.hour]);
        const gridPrices = hourlyData.map(h => priceComparison.grid_prices[h.hour]);
        
        priceChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: typeof I18N !== 'undefined' && I18N.currentLang === 'zh' ? '售电公司电价（含服务费）' : 'Agent company price (incl. fees)',
                    data: agentPrices,
                    borderColor: 'rgb(14, 165, 233)',
                    backgroundColor: 'rgba(14, 165, 233, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 6
                }, {
                    label: typeof I18N !== 'undefined' && I18N.currentLang === 'zh' ? '电网电价' : 'Grid price',
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
                                const datasetIndex = context.datasetIndex;
                                
                                // For grid price, use the period_type from hourlyData
                                if (datasetIndex === 1) {
                                    return `Period: ${hourlyData[index].period_type}`;
                                }
                                
                                // For agent company price, determine period based on price level
                                const agentPrice = agentPrices[index];
                                const allAgentPrices = agentPrices.slice();
                                allAgentPrices.sort((a, b) => a - b);
                                
                                const lowThreshold = allAgentPrices[Math.floor(allAgentPrices.length * 0.33)];
                                const highThreshold = allAgentPrices[Math.floor(allAgentPrices.length * 0.67)];
                                
                                let agentPeriod;
                                if (agentPrice <= lowThreshold) {
                                    agentPeriod = 'Valley';
                                } else if (agentPrice >= highThreshold) {
                                    agentPeriod = 'Peak';
                                } else {
                                    agentPeriod = 'Normal';
                                }
                                
                                return `Period: ${agentPeriod}`;
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
                            text: typeof I18N !== 'undefined' && I18N.currentLang === 'zh' ? '电价（元/kWh）' : 'Price (CNY/kWh)',
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
                            text: typeof I18N !== 'undefined' && I18N.currentLang === 'zh' ? '时间' : 'Time',
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
    
    // Render energy mix doughnut chart
    let energyPieChartInstance = null;
    function renderEnergyPieChart(hourlyData) {
        console.log('Rendering pie chart - animation enabled');
        const ctx = document.getElementById('energyPieChart');
        
        // Destroy old chart
        if (energyPieChartInstance) {
            energyPieChartInstance.destroy();
        }
        
        // Set canvas transparent background
        ctx.style.backgroundColor = 'transparent';
        
        // Calculate usage by period
        const peakUsage = hourlyData.filter(h => h.period_type === 'Peak').reduce((sum, h) => sum + h.usage, 0);
        const normalUsage = hourlyData.filter(h => h.period_type === 'Normal').reduce((sum, h) => sum + h.usage, 0);
        const valleyUsage = hourlyData.filter(h => h.period_type === 'Valley').reduce((sum, h) => sum + h.usage, 0);
        
        const isZh = typeof I18N !== 'undefined' && I18N.currentLang === 'zh';
        energyPieChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: isZh ? ['高峰', '平时', '低谷'] : ['Peak', 'Normal', 'Valley'],
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
    
    // Render cost report
    function renderCostReport(costAnalysis) {
        const container = document.getElementById('costReportContent');
        
        const hourlyData = costAnalysis.hourly_breakdown;
        const monthDays = costAnalysis.month_days;
        
        // Calculate period totals (hourly_breakdown is daily data, multiply by working days)
        const peakData = hourlyData.filter(h => h.period_type === 'Peak');
        const normalData = hourlyData.filter(h => h.period_type === 'Normal');
        const valleyData = hourlyData.filter(h => h.period_type === 'Valley');
        
        const peakUsage = peakData.reduce((sum, h) => sum + h.usage, 0) * monthDays;
        const normalUsage = normalData.reduce((sum, h) => sum + h.usage, 0) * monthDays;
        const valleyUsage = valleyData.reduce((sum, h) => sum + h.usage, 0) * monthDays;
        
        const peakCost = peakData.reduce((sum, h) => sum + h.cost, 0) * monthDays;
        const normalCost = normalData.reduce((sum, h) => sum + h.cost, 0) * monthDays;
        const valleyCost = valleyData.reduce((sum, h) => sum + h.cost, 0) * monthDays;
        
        // Total energy cost (excluding capacity fee)
        const totalEnergyCost = costAnalysis.monthly_energy_cost;
        
        // Calculate total usage
        const totalUsage = peakUsage + normalUsage + valleyUsage;
        
        const html = `
            <table style="width: 100%; border-collapse: collapse; font-size: 0.875rem;">
                <thead>
                    <tr style="background: transparent;">
                        <th style="padding: 0.75rem; text-align: center; border-bottom: 2px solid rgba(14, 165, 233, 0.2);">Period type</th>
                        <th style="padding: 0.75rem; text-align: center; border-bottom: 2px solid rgba(14, 165, 233, 0.2);">Usage (kWh)</th>
                        <th style="padding: 0.75rem; text-align: center; border-bottom: 2px solid rgba(14, 165, 233, 0.2);">Price (CNY/kWh)</th>
                        <th style="padding: 0.75rem; text-align: center; border-bottom: 2px solid rgba(14, 165, 233, 0.2);">Cost (CNY)</th>
                        <th style="padding: 0.75rem; text-align: center; border-bottom: 2px solid rgba(14, 165, 233, 0.2);">Share</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 0.75rem; text-align: center; color: #dc2626; font-weight: 700; font-size: 0.9375rem;">Peak</td>
                        <td style="padding: 0.75rem; text-align: center;">${formatNumber(peakUsage)}</td>
                        <td style="padding: 0.75rem; text-align: center;">¥${peakUsage > 0 ? (peakCost / peakUsage).toFixed(4) : '0.0000'}</td>
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">¥${formatNumber(peakCost)}</td>
                        <td style="padding: 0.75rem; text-align: center;">${totalEnergyCost > 0 ? ((peakCost / totalEnergyCost) * 100).toFixed(1) : '0.0'}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.75rem; text-align: center; color: #f59e0b; font-weight: 700; font-size: 0.9375rem;">Normal</td>
                        <td style="padding: 0.75rem; text-align: center;">${formatNumber(normalUsage)}</td>
                        <td style="padding: 0.75rem; text-align: center;">¥${normalUsage > 0 ? (normalCost / normalUsage).toFixed(4) : '0.0000'}</td>
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">¥${formatNumber(normalCost)}</td>
                        <td style="padding: 0.75rem; text-align: center;">${totalEnergyCost > 0 ? ((normalCost / totalEnergyCost) * 100).toFixed(1) : '0.0'}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.75rem; text-align: center; color: #10b981; font-weight: 700; font-size: 0.9375rem;">Valley</td>
                        <td style="padding: 0.75rem; text-align: center;">${formatNumber(valleyUsage)}</td>
                        <td style="padding: 0.75rem; text-align: center;">¥${valleyUsage > 0 ? (valleyCost / valleyUsage).toFixed(4) : '0.0000'}</td>
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">¥${formatNumber(valleyCost)}</td>
                        <td style="padding: 0.75rem; text-align: center;">${totalEnergyCost > 0 ? ((valleyCost / totalEnergyCost) * 100).toFixed(1) : '0.0'}%</td>
                    </tr>
                    <tr style="background: transparent;">
                        <td colspan="3" style="padding: 0.75rem; text-align: left; font-weight: bold;">Capacity fee</td>
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">¥${formatNumber(costAnalysis.capacity_fee)}</td>
                        <td style="padding: 0.75rem; text-align: center;">-</td>
                    </tr>
                    <tr style="background: transparent;">
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">Total</td>
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">${formatNumber(totalUsage)}</td>
                        <td style="padding: 0.75rem; text-align: center;">-</td>
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">¥${formatNumber(costAnalysis.total_monthly_cost)}</td>
                        <td style="padding: 0.75rem; text-align: center; font-weight: bold;">100%</td>
                    </tr>
                </tbody>
            </table>
        `;
        
        console.log('Table HTML:', html);
        container.innerHTML = html;
    }
    
    // Load efficiency benchmark
    function loadEfficiencyBenchmark(factoryId) {
        const card = document.getElementById('efficiencyBenchmarkCard');
    
        fetch(`/api/factory/${factoryId}/efficiency-benchmark`, {
            credentials: 'same-origin'
        })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.data) {
                    card.style.display = 'block';
                    const b = data.data;
                    
                    let bgColor = '';
                    if (b.level === 'excellent') bgColor = 'rgba(16, 185, 129, 0.1)';
                    else if (b.level === 'good') bgColor = 'rgba(59, 130, 246, 0.1)';
                    else if (b.level === 'average') bgColor = 'rgba(245, 158, 11, 0.1)';
                    else bgColor = 'rgba(239, 68, 68, 0.1)';
                
                    document.getElementById('benchmarkContent').innerHTML = `
                        <div class="row align-items-center" style="background: ${bgColor}; border-radius: 12px; padding: 12px;">
                            <div class="col-md-3 text-center">
                                <div style="font-size: 2.5rem;">${b.level_icon}</div>
                                <span class="badge bg-${b.level_color} mt-1">${b.level_text}</span>
                            </div>
                            <div class="col-md-5">
                                <div class="small text-muted">${b.industry}</div>
                                <div class="mb-2">
                                    <span class="fw-bold">${b.energy_intensity}</span>
                                    <span class="text-muted"> kWh/ten thousand yuan</span>
                                </div>
                                <div class="progress mb-2" style="height: 6px;">
                                    <div class="progress-bar bg-${b.level_color}" style="width: ${Math.min(100, (b.energy_intensity / b.benchmark_poor) * 100)}%"></div>
                                </div>
                                <div class="d-flex justify-content-between small text-muted">
                                    <span><span>Excellent</span> ${b.benchmark_excellent}</span>
                                    <span><span>Average</span> ${b.benchmark_avg}</span>
                                    <span><span>Poor</span> ${b.benchmark_poor}</span>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="small text-muted">📊 <span>Monthly Electricity Consumption</span></div>
                                <div class="fw-bold">${b.monthly_usage.toLocaleString()} kWh</div>
                                <div class="small text-muted mt-2">💰 <span>Estimated Monthly Output</span></div>
                                <div class="fw-bold">${b.estimated_output*10} <span>thousand yuan</span></div>
                                <div class="small text-${b.level_color} mt-2">${b.tip}</div>
                            </div>
                        </div>
                    `;
                }
            })
            .catch(err => {
                console.error('Efficiency benchmark loading failed:', err);
                card.style.display = 'none';
            });
    }
    
    // Load green power procurement guide
    function loadGreenPowerGuide(factoryId) {
        const card = document.getElementById('greenPowerCard');
        if (!card) return;
    
        fetch(`/api/factory/${factoryId}/green-power-guide?project_type=existing`, {
            credentials: 'same-origin'
        })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.data) {
                    card.style.display = 'block';
                    const g = data.data;
                
                    // Generate platform buttons
                    let platformButtons = '';
                    g.platforms.forEach(platform => {
                        platformButtons += `<a href="${platform.url}" target="_blank" class="btn btn-sm btn-outline-success me-2 mb-2">${platform.name}</a>`;
                    });
                
                    document.getElementById('greenPowerContent').innerHTML = `
                        <div class="row align-items-center">
                            <div class="col-md-3 text-center">
                                <div style="font-size: 2rem;">🌱</div>
                                <span class="badge bg-success mt-1">${g.tier_name}</span>
                            </div>
                            <div class="col-md-5">
                                <div class="small text-muted">Recommended plan</div>
                                <div class="fw-bold mb-1">${g.description}</div>
                                <div class="small text-muted"><span>Monthly electricity consumption:</span> ${g.monthly_usage.toLocaleString()} kWh</div>
                                <div class="small text-success"><span>Estimated monthly cost:</span> ¥${g.estimated_cost_per_month.toLocaleString()}</div>
                                <div class="small text-info"><span>Carbon reduction:</span> ${g.carbon_reduction_per_month.toLocaleString()} <span>tons/month</span></div>
                                <div class="small text-primary mt-1">💰 ${g.price_info}</div>
                            </div>
                            <div class="col-md-4">
                                <div class="small text-muted"><span>Official Purchase Platforms</span></div>
                                <div class="mt-1">${platformButtons}</div>
                                ${g.certificates_needed ? `<div class="small text-muted mt-2"><span>Recommended to purchase:</span> ${g.certificates_needed} <span>green certificates/month</span></div>` : ''}
                            </div>
                        </div>
                        <div class="mt-2 p-2 bg-light rounded">
                            <div class="small fw-bold">📋 <span>Implementation Steps</span></div>
                            <div class="small">${g.steps.join(' → ')}</div>
                            <div class="small text-muted mt-1">📌 ${g.policy_note}</div>
                        </div>
                    </div>
                `;
            } else {
                card.style.display = 'none';
            }
        })
        .catch(err => {
            console.error('Green power guide loading failed:', err);
            card.style.display = 'none';
        });
    }

    // Load equipment recommendations
    function loadEquipmentRecommendations(factoryId) {
        const card = document.getElementById('equipmentCard');
        if (!card) return;
    
        fetch(`/api/factory/${factoryId}/equipment-recommendations`, {
            credentials: 'same-origin'
        })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.data && data.data.length > 0) {
                    card.style.display = 'block';
                
                    // Horizontal layout: three cards in a row
                    let html = '<div class="row">';
                    data.data.forEach(rec => {
                        html += `
                            <div class="col-md-4">
                                <div class="card h-100 text-center p-3" style="background: rgba(255,255,255,0.5);">
                                    <div style="font-size: 2.5rem;">${rec.icon}</div>
                                    <h6 class="mt-2 fw-bold">${rec.category}</h6>
                                    <div class="small fw-bold">${rec.recommended_device || rec.description}</div>
                                    <hr class="my-2">
                                    <div class="small text-muted">💰 Investment: ${rec.investment_formatted}</div>
                                    <div class="small text-success">💵 Annual Saving: ${rec.annual_saving_formatted}</div>
                                    <div class="small text-info">⏱️ Payback: ${rec.payback_years} years</div>
                                </div>
                            </div>
                        `;
                    });
                    html += '</div>';
                    document.getElementById('equipmentContent').innerHTML = html;
                } else {
                    card.style.display = 'none';
                }
            })
            .catch(err => {
                console.error('Equipment recommendations failed:', err);
                card.style.display = 'none';
            });
    }


    // Delete factory
    window.deleteFactory = async function(factoryId, factoryName) {
        if (!confirm(`Are you sure you want to delete factory "${factoryName}"? This action cannot be undone.`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/factory/${factoryId}`, {
                credentials: 'same-origin',
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                showSuccess('Factory deleted successfully');
                await loadFactories();
            } else {
                showError(data.message || 'Failed to delete factory');
            }
        } catch (error) {
            console.error('Failed to delete factory:', error);
            showError('Failed to delete factory');
        }
    };
    
    // ========================================
    // Utility functions
    // ========================================
    
    // HTML escaping
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Format numbers
    function formatNumber(num) {
        if (num === null || num === undefined) return '0';
        return parseFloat(num).toLocaleString('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        });
    }
    
    // Show success message
    function showSuccess(message) {
        showToast(message, 'success');
    }
    
    // Show error message
    function showError(message) {
        showToast(message, 'danger');
    }
    
    // Show info message
    function showInfo(message) {
        showToast(message, 'info');
    }
    
    // Show toast message
    function showToast(message, type = 'info') {
        // Create toast container (if missing)
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
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
        
        // Remove toast element
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
    
    // ========================================
    // Performance monitoring and settings
    // ========================================
    
    // FPS monitor
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
            
            // Record FPS (1000ms / delta)
            if (delta > 0) {
                const fps = 1000 / delta;
                this.frames.push(fps);
                
                // During benchmark, do not cap frame count; for live display keep only the latest 60 frames
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
            // Take average of last 10 frames
            const recent = this.frames.slice(-10);
            const sum = recent.reduce((a, b) => a + b, 0);
            return Math.round(sum / recent.length);
        },
        
        reset() {
            this.frames = [];
            this.lastTime = performance.now();
        }
    };
    
    // Open settings panel
    window.openSettings = function() {
        const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
        
        // Load current settings
        const currentMode = localStorage.getItem('uiMode') || 'full';
        document.getElementById('uiMode' + currentMode.charAt(0).toUpperCase() + currentMode.slice(1)).checked = true;
        
        const showFps = localStorage.getItem('showFps') === 'true';
        document.getElementById('showFpsToggle').checked = showFps;
        
        // Load current language
        const currentLang = localStorage.getItem('lang') || 'en';
        const langRadio = document.getElementById(currentLang === 'zh' ? 'langZh' : 'langEn');
        if (langRadio) langRadio.checked = true;
        
        modal.show();
    };
    
    // Run benchmark
    window.runBenchmark = async function() {
        const btn = document.getElementById('benchmarkBtn');
        const resultDiv = document.getElementById('benchmarkResult');
        const alertDiv = document.getElementById('benchmarkAlert');
        
        // Disable button
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Testing...';
        
        // Hide previous results
        resultDiv.style.display = 'none';
        
        // Save current UI mode
        const wasLiteMode = document.body.classList.contains('ui-lite');
        
        // Force switch to full UI for the test
        if (wasLiteMode) {
            document.body.classList.remove('ui-lite');
            document.body.classList.add('ui-full');
        }
        
        // Wait 100ms for styles to take effect
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Mark as benchmark mode
        FPSMonitor.isBenchmarking = true;
        FPSMonitor.reset();
        FPSMonitor.start();
        
        // Force hover effect on all page elements
        const allCards = document.querySelectorAll('.stat-card, .factory-card, .card');
        let hoverIndex = 0;
        const hoverInterval = setInterval(() => {
            // Remove all hover effects
            allCards.forEach(card => {
                card.style.transform = '';
                card.style.boxShadow = '';
            });
            
            // Force current card hover effect
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
        }, 300); // Rotate to the next card every 0.3 seconds
        
        // Test for 10 seconds
        await new Promise(resolve => setTimeout(resolve, 10000));
        
        // Stop monitoring and hover effects
        FPSMonitor.stop();
        FPSMonitor.isBenchmarking = false;
        clearInterval(hoverInterval);
        
        // Restore all card styles
        allCards.forEach(card => {
            card.style.transform = '';
            card.style.boxShadow = '';
        });
        
        // Restore original UI mode
        if (wasLiteMode) {
            document.body.classList.remove('ui-full');
            document.body.classList.add('ui-lite');
        }
        
        // Calculate average FPS and minimum FPS
        const avgFps = FPSMonitor.getAverageFPS();
        const minFps = FPSMonitor.getMinFPS();
        
        // Show results
        document.getElementById('avgFps').textContent = avgFps;
        document.getElementById('minFps').textContent = minFps;
        
        let recommendation = '';
        let alertClass = '';
        
        // Determine performance based on minimum FPS (worst-case)
        if (minFps >= 50) {
            recommendation = '✅ Excellent device performance; full UI is recommended';
            alertClass = 'alert-success';
        } else if (minFps >= 30) {
            recommendation = '⚠️ Device performance is moderate; full UI is usable but may feel slightly laggy';
            alertClass = 'alert-warning';
        } else {
            recommendation = '❌ Device performance is low; lightweight UI is strongly recommended';
            alertClass = 'alert-danger';
        }
        
        document.getElementById('recommendation').textContent = recommendation;
        alertDiv.className = 'alert ' + alertClass;
        
        resultDiv.style.display = 'block';
        
        // Restore button
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-play-circle me-1"></i>Retest';
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
        
        setTimeout(updateFpsDisplay, 500); // Update every 0.5 seconds
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
        
        // Save to localStorage
        localStorage.setItem('uiMode', uiMode);
        localStorage.setItem('showFps', showFps);
        
        // Apply UI mode
        applyUIMode(uiMode);
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
        modal.hide();
        
        showSuccess('Settings saved');
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
    // Initialization
    // ========================================
    function init() {
        console.log('🚀 PeakShift Dashboard initializing...');
        
        // Show factory management view
        showView('factoryManagement');
        
        // Load factory list
        loadFactories();
        
        // Load admin notifications (deleted factories)
        loadDeletedNotifications();
        
        // Load saved settings
        const savedMode = localStorage.getItem('uiMode') || 'full';
        applyUIMode(savedMode);
        
        const showFps = localStorage.getItem('showFps') === 'true';
        if (showFps) {
            document.getElementById('fpsDisplay').style.display = 'block';
            FPSMonitor.start();
            updateFpsDisplay();
        }
        
        console.log('✅ Dashboard initialization complete');
    }
    
    // ========================================
    // Admin notifications (deleted factories)
    // ========================================
    async function loadDeletedNotifications() {
        try {
            const resp = await fetch('/api/factories/deleted-notifications', {
                credentials: 'same-origin'
            });
            const data = await resp.json();
            
            if (data.success && data.notifications.length > 0) {
                const btn = document.getElementById('adminNotifBtn');
                const countBadge = document.getElementById('adminNotifCount');
                if (btn) btn.style.display = 'inline-block';
                if (countBadge) countBadge.textContent = data.notifications.length;
                
                // Store for modal display
                window._deletedNotifications = data.notifications;
            }
        } catch (e) {
            console.error('Failed to load deleted notifications:', e);
        }
    }
    
    window.showDeletedNotifications = function() {
        const list = document.getElementById('deletedNotifList');
        const notifs = window._deletedNotifications || [];
        const isZh = typeof I18N !== 'undefined' && I18N.currentLang === 'zh';
        
        if (notifs.length === 0) {
            list.innerHTML = `<p class="text-muted text-center">${isZh ? '暂无通知' : 'No notifications'}</p>`;
        } else {
            list.innerHTML = notifs.map(n => {
                const msg = isZh
                    ? `工厂 <strong>${escapeHtml(n.name)}</strong> 已于 <strong>${n.deleted_at || '-'}</strong> 被管理员删除`
                    : `Factory <strong>${escapeHtml(n.name)}</strong> was deleted by admin at <strong>${n.deleted_at || '-'}</strong>`;
                return `
                    <div class="alert alert-warning d-flex align-items-start" role="alert">
                        <i class="bi bi-exclamation-triangle-fill me-2 mt-1" style="color: #ef4444;"></i>
                        <div>${msg}</div>
                    </div>
                `;
            }).join('');
        }
        
        const modal = new bootstrap.Modal(document.getElementById('deletedNotifModal'));
        modal.show();
    };
    
    // Initialize after DOM loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
