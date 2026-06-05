/**
 * PeakShift i18n Module - Full Coverage
 * Two approaches combined:
 * 1. data-i18n attributes for static elements
 * 2. Text node scanning for dynamic/JS-generated content
 * 
 * Language preference stored in localStorage.
 */

const I18N = {
    currentLang: localStorage.getItem('lang') || 'en',

    // Full English -> Chinese mapping (used for text node replacement)
    dict: {
        // ===== Navigation =====
        'Log out': '退出登录',
        'Settings': '设置',
        'Admin': '管理员',

        // ===== Auth / Login =====
        'Welcome back!': '欢迎回来！',
        'Please enter your details': '请输入您的账号信息',
        'Username or Email': '用户名或邮箱',
        'Enter your username or email': '请输入用户名或邮箱',
        'Password': '密码',
        'Log in': '登录',
        'Logging in...': '登录中...',
        "Don't have an account?": '还没有账号？',
        'Sign Up': '注册',
        'Create an account': '创建账号',
        'Join PeakShift to optimize your energy costs': '加入 PeakShift，优化您的用电成本',
        'Username': '用户名',
        'Choose a username': '请选择一个用户名',
        '3-32 characters, can only contain letters, numbers, underscores, and hyphens': '3-32个字符，只能包含字母、数字、下划线和连字符',
        'Email': '邮箱',
        'Maximum 120 characters': '最多120个字符',
        '6-128 characters, recommended to include uppercase and lowercase letters, numbers, and special characters': '6-128个字符，建议包含大小写字母、数字和特殊字符',
        'Create Account': '创建账号',
        'Creating Account...': '创建中...',
        'Already have an account?': '已有账号？',
        'Invalid username or password': '用户名或密码错误',
        'Registration successful! Please log in': '注册成功！请登录',
        'Sign in': '登录',
        'Get started': '立即开始',
        'Login successful!': '登录成功！',
        'Registration successful! Please log in.': '注册成功！请登录。',

        // ===== Welcome Page =====
        'Optimize electricity costs with peak-valley pricing': '利用峰谷电价优化用电成本',
        'Analyze time-of-use electricity rates, calculate monthly costs, and get actionable recommendations to reduce expenses and carbon emissions.': '分析分时电价，计算月度成本，获取可操作的建议来降低费用和碳排放。',
        'Start free trial': '免费试用',
        'Learn more': '了解更多',
        'Features': '功能',
        'About': '关于',
        'Everything you need to optimize energy': '优化能源所需的一切',
        "Analyze peak-valley pricing, calculate costs, and get recommendations to reduce your factory's electricity expenses.": '分析峰谷电价，计算成本，获取降低工厂电费的建议。',
        'Cost Calculation': '成本计算',
        "Calculate monthly electricity costs based on your factory's voltage level, transformer capacity, and time-of-use pricing.": '根据工厂的电压等级、变压器容量和分时电价计算月度电费。',
        'Peak-Valley Analysis': '峰谷分析',
        'Compare hourly electricity prices between grid and supplier rates to identify the best times for production.': '比较电网和售电商的逐时电价，找出最佳生产时段。',
        'Carbon Tracking': '碳排放追踪',
        'Calculate carbon emissions from grid electricity and compare with potential savings from renewable sources.': '计算电网用电的碳排放，并与可再生能源的潜在节省进行对比。',
        'Factory Management': '工厂管理',
        'Manage multiple factories with customizable work schedules, voltage levels, and transformer specifications.': '管理多个工厂，自定义工作时间、电压等级和变压器规格。',
        'Optimization Suggestions': '优化建议',
        'Get actionable recommendations on when to shift production to valley hours for maximum cost savings.': '获取可操作的建议，了解何时将生产转移到谷时以最大化节省。',
        'Supplier Comparison': '供应商对比',
        'Compare costs between purchasing from grid vs. third-party suppliers with detailed hourly breakdowns.': '对比电网购电与第三方供应商的成本，提供详细的逐时分析。',
        'How PeakShift works': 'PeakShift 如何工作',
        'Get started today': '立即开始使用',
        'Cost Analysis': '成本分析',
        'Compare peak, normal, and valley pricing': '对比峰、平、谷电价',
        '4 Voltage Levels': '4种电压等级',
        'Support 10/35/110/220 kV': '支持 10/35/110/220 kV',
        '24-Hour Tracking': '24小时追踪',
        'Hourly rate comparison': '逐时电价对比',
        'COST OPTIMIZATION': '成本优化',
        'Reduce Electricity Expenses': '降低电费支出',
        'Analyze peak-valley pricing and get recommendations to shift production to lower-cost periods': '分析峰谷电价，获取将生产转移到低成本时段的建议',
        'PEAK AVOIDANCE': '避峰',
        'Avoid High-Cost Hours': '避开高成本时段',
        'CARBON REDUCTION': '碳减排',
        'Lower Emissions': '降低排放',
        'Peak-Valley Optimization': '峰谷优化',
        'By analyzing hourly electricity rates and your work schedule, PeakShift identifies opportunities to shift production from peak to valley hours for cost reduction.': '通过分析逐时电价和您的工作时间表，PeakShift 识别将生产从峰时转移到谷时的机会以降低成本。',

        // ===== Dashboard =====
        'Factory management': '工厂管理',
        'Manage your factory information, view power data and cost analysis': '管理工厂信息，查看用电数据和成本分析',
        'Create Factory': '创建工厂',
        'No factories yet': '暂无工厂',
        'Click the "Create Factory" button to create your first factory': '点击"创建工厂"按钮创建您的第一个工厂',
        'Create now': '立即创建',
        'Return to factory list': '返回工厂列表',
        'Voltage level': '电压等级',
        'Transformer capacity': '变压器容量',
        'Daily usage': '日用电量',
        'Working days per month': '月工作天数',
        "Today's usage": '今日用电',
        'Monthly cost': '月度费用',
        'Carbon footprint': '碳排放',
        'Saving potential': '节省潜力',
        'Cost': '成本',
        'Carbon': '碳排',
        'Edit': '编辑',
        'View details': '查看详情',
        'Delete': '删除',
        'Real-time price chart': '实时电价图表',
        'Energy mix pie chart': '能源结构饼图',
        'Cost report': '成本报告',
        'Optimization suggestions': '优化建议',
        'Loading...': '加载中...',
        'Loading optimization suggestions...': '加载优化建议...',
        'Industry Efficiency Benchmark': '行业能效基准',
        'Green electricity procurement guide': '绿电采购引导',
        'Energy Saving Equipment': '节能设备推荐',
        'Pending backend implementation': '等待后端实现',
        'No data available': '暂无数据',
        'Loading failed': '加载失败',

        // ===== Factory Modal =====
        'New Factory': '新建工厂',
        'Edit Factory': '编辑工厂',
        'Factory name': '工厂名称',
        'Factory location': '工厂位置',
        'Industry type': '行业类型',
        'Please select': '请选择',
        'Voltage level': '电压等级',
        'Transformer capacity (kVA)': '变压器容量 (kVA)',
        'Daily usage (kWh/day)': '日用电量 (kWh/天)',
        'Work periods': '工作时段',
        'Start time': '开始时间',
        'End time': '结束时间',
        'Add': '添加',
        'Add factory work periods, e.g. 8:00-12:00, 13:00-18:00': '添加工厂工作时段，如 8:00-12:00, 13:00-18:00',
        'Cancel': '取消',
        'Create': '创建',
        'Save': '保存',
        'No work periods added yet': '尚未添加工作时段',

        // ===== Settings =====
        'System settings': '系统设置',
        'UI mode': 'UI 模式',
        'Full mode': '完整模式',
        'Lite mode': '轻量模式',
        'Full mode: full effects, suitable for high-performance devices': '完整模式：全部特效，适合高性能设备',
        'Lite mode: reduced animation, suitable for low-performance devices': '轻量模式：减少动画，适合低性能设备',
        'Performance test': '性能测试',
        'Start benchmark test (10 seconds)': '开始性能测试（10秒）',
        'Show real-time FPS': '显示实时帧率',
        'Close': '关闭',
        'Save settings': '保存设置',
        'Language': '语言',
        'Retest': '重新测试',
        'Testing...': '测试中...',
        'Average FPS:': '平均帧率：',
        'Minimum FPS:': '最低帧率：',
        'Settings saved': '设置已保存',
        'Excellent device performance; full UI is recommended': '设备性能优秀，推荐使用完整模式',
        'Device performance is moderate; full UI is usable but may feel slightly laggy': '设备性能中等，完整模式可用但可能略有卡顿',
        'Device performance is low; lightweight UI is strongly recommended': '设备性能较低，强烈建议使用轻量模式',
        'Excellent performance! Full mode recommended.': '性能优秀，推荐使用完整模式。',
        'Good performance. Full mode works well.': '性能良好，完整模式运行顺畅。',
        'Moderate performance. Consider Lite mode.': '性能中等，可考虑使用轻量模式。',
        'Low performance detected. Lite mode strongly recommended.': '检测到性能较低，强烈建议使用轻量模式。',

        // ===== Admin Dashboard =====
        'PeakShift Admin Console': 'PeakShift 管理员控制台',
        'Admin Console': '管理员控制台',
        'Total Registered Users': '注册用户总数',
        'Total Factories': '工厂总数',
        'Total Monthly Usage (kWh)': '总月用电量 (kWh)',
        'Total Carbon Emission (kg CO₂)': '总碳排放 (kg CO₂)',
        'User Management': '用户管理',
        'System Data': '系统数据',
        'User List': '用户列表',
        'Factory List': '工厂列表',
        'ID': 'ID',
        'Registered': '注册时间',
        'Factories': '工厂数量',
        'Total Usage (kWh)': '总用电量 (kWh)',
        'Carbon (kg)': '碳排放 (kg)',
        'Factory Name': '工厂名称',
        'Location': '位置',
        'Industry Type': '行业类型',
        'Voltage Level': '电压等级',
        'Monthly Usage (kWh)': '月用电量 (kWh)',
        'Owner': '所属用户',
        'No user data available': '暂无用户数据',
        'No factory data available': '暂无工厂数据',
        'System Data Management': '系统数据管理',
        'System data (electricity prices, carbon factors, etc.) is automatically synced from Excel files. To modify, edit the relevant files in the': '系统数据（电价、碳因子等）通过 Excel 文件自动同步。如需修改，请编辑',
        'directory. The system will detect and update on startup.': '目录下的相关文件，系统将在启动时自动检测并更新。',
        'System data (electricity prices, carbon factors, etc.) is automatically synced from Excel files. To modify, edit the relevant files in the data/ directory. The system will detect and update on startup.': '系统数据（电价、碳因子等）通过 Excel 文件自动同步。如需修改，请编辑 data/ 目录下的相关文件，系统将在启动时自动检测并更新。',
        'Electricity Price Data': '电价数据',
        'File path': '文件路径',
        'Carbon Emission Factors': '碳排放因子',
        'Grid carbon factor': '电网碳排放因子',
        'PV carbon factor': '光伏碳排放因子',
        'carbon factor': '碳排放因子',
        'Contains 24-hour time-of-use pricing and grid selling prices': '包含24小时分时电价和电网售卖价格数据',
        'Defined in': '定义于',

        // ===== Password Strength =====
        'Weak': '弱',
        'Medium': '中',
        'Strong': '强',

        // ===== Misc =====
        'Access Denied': '访问被拒绝',
        "You don't have permission to access this page.": '您没有权限访问此页面。',
        'This page is restricted to administrators only.': '此页面仅限管理员访问。',
        'Return to Home': '返回首页',
        'Successfully logged out': '已成功退出',
        'Factory created successfully': '工厂创建成功',
        'Factory updated successfully': '工厂更新成功',
        'Factory deleted successfully': '工厂删除成功',
        'Failed to load factory list': '加载工厂列表失败',
        'Failed to create factory': '创建工厂失败',
        'Failed to update factory': '更新工厂失败',
        'Failed to delete factory': '删除工厂失败',
        'Failed to load factory details': '加载工厂详情失败',
        'Please select a start and end time': '请选择开始和结束时间',
        'End time must be later than start time': '结束时间必须晚于开始时间',
        'Time periods cannot overlap': '时间段不能重叠',
        'Please add at least one work period': '请至少添加一个工作时段',
        'Factory not found': '未找到工厂',
        'Are you sure you want to delete factory': '确定要删除工厂',
        'This action cannot be undone.': '此操作不可撤销。',
        'Industry type is required': '行业类型为必填项',
        'days': '天',

        // ===== Cost Report Table =====
        'Period type': '时段类型',
        'Usage (kWh)': '用电量 (kWh)',
        'Price (CNY/kWh)': '电价 (元/kWh)',
        'Cost (CNY)': '费用 (元)',
        'Share': '占比',
        'Peak': '高峰',
        'Normal': '平时',
        'Valley': '低谷',
        'Total': '合计',

        // ===== Chart Labels =====
        'Agent company price (incl. fees)': '售电公司电价（含服务费）',
        'Grid price': '电网电价',
        'Grid electricity': '电网用电',
        'Photovoltaic': '光伏',

        // ===== Factory Details =====
        'CNY/month': '元/月',
        'kg CO₂/month': 'kg CO₂/月',
        'CNY': '元',
        'kWh': 'kWh',
        'kV': 'kV',
        'kVA': 'kVA',

        // ===== Factory Card (JS generated) =====
        'Voltage:': '电压：',
        'Capacity:': '容量：',
        'Capacity fee': '容量费',
        'Daily usage': '日用电量',
        'Monthly usage': '月用电量',
        'Working days': '工作天数',
        'Work periods:': '工作时段：',

        // ===== Benchmark (JS generated) =====
        'Excellent': '优秀',
        'Good': '良好',
        'Average': '一般',
        'Poor': '较差',
        'excellent': '优秀',
        'good': '良好',
        'average': '一般',
        'poor': '较差',
        'Monthly Electricity Consumption': '月用电量',
        'Estimated Monthly Output': '预估月产值',
        'kWh/ten thousand yuan': 'kWh/万元',
        'thousand yuan': '万元',

        // ===== Green Power (JS generated) =====
        'Recommended plan': '推荐方案',
        'Monthly electricity consumption:': '月用电量：',
        'Estimated monthly cost:': '预估月费用：',
        'Carbon reduction:': '碳减排：',
        'Official Purchase Platforms': '官方采购平台',
        'Implementation Steps': '实施步骤',

        // ===== Equipment (JS generated) =====
        'Investment:': '投资：',
        'Annual Saving:': '年节省：',
        'Payback:': '回收期：',
        'years': '年',

        // ===== Photovoltaic Comparison =====
        'Photovoltaic Power Comparison': '光伏发电对比',
        'Current Grid Carbon': '当前电网碳排',
        'With Photovoltaic': '使用光伏后',
        'Reduction Potential': '减排潜力',

        // ===== Optimization Suggestions =====
        'High impact': '高影响',
        'Medium impact': '中影响',
        'Low impact': '低影响',
        'Action recommendations:': '行动建议：',
        'The current power plan is already well optimized!': '当前用电方案已经很优化了！',
        'Failed to load optimization suggestions. Please try again later.': '加载优化建议失败，请稍后重试。',

        // ===== Backend-generated text (efficiency benchmark) =====
        'Steel': '钢铁',
        'Aluminum Smelting': '铝冶炼',
        'Cement': '水泥',
        'Chemical': '化工',
        'Coal Refining': '煤炼',
        'Textile': '纺织',
        'Other': '其他',
        'Below industry average, consider optimizing power usage patterns': '低于行业平均，建议优化用电模式',
        'In the bottom 30% of industry, optimization measures recommended': '处于行业后30%，建议尽快采取优化措施',

        // ===== Backend-generated text (green power) =====
        'Small and Medium-sized Enterprises': '中小型企业',
        'Medium-sized Enterprises': '中型企业',
        'Large-scale Electricity Consumers': '大型用电企业',
        'Electric Power Trading Centre': '电力交易中心',
        'Electric Power Medium and Long-term Trading Platform': '电力中长期交易平台',
        'National Green Power Certificate Subscription Trading Platform': '国家绿色电力证书认购交易平台',
        'Bidding price: 0.199-0.332 CNY/kWh': '竞价区间：0.199-0.332 元/kWh',
        'Market-based pricing': '市场化定价',
        '30-50 CNY per certificate (1000 kWh)': '每张证书30-50元（1000 kWh）',
        'It is recommended to directly purchase green certificates.': '建议直接购买绿色电力证书。',
        'It is recommended to sign a green power purchase agreement (PPA).': '建议签订绿电购买协议（PPA）。',
        'It is recommended to build a distributed photovoltaic system combined with green certificates.': '建议建设分布式光伏系统并结合绿证。',
        '1. Calculate monthly electricity consumption and determine the number of green certificates to purchase': '1. 计算月用电量，确定需购买的绿证数量',
        '2. Register enterprise account on the national green certificate platform': '2. 在国家绿证平台注册企业账号',
        '3. Purchase green certificates as needed and obtain green electricity certificates': '3. 按需购买绿证，获取绿电证书',
        '4. Disclose green certificate usage in ESG reports': '4. 在ESG报告中披露绿证使用情况',
        '1. Contact Electric Power Trading Centre to inquire about green power packages': '1. 联系电力交易中心咨询绿电套餐',
        '2. Sign a green power purchase agreement (PPA)': '2. 签订绿电购买协议（PPA）',
        '3. Obtain green power consumption certificates': '3. 获取绿电消费凭证',
        '4. Enjoy the carbon reduction benefits from the green power premium': '4. 享受绿电溢价带来的碳减排收益',
        '1. Evaluate the feasibility of installing rooftop solar panels at the factory': '1. 评估工厂屋顶安装光伏板的可行性',
        '2. Choose between the EMC (Energy Management Contract) model or self-investment': '2. 选择合同能源管理（EMC）模式或自投',
        '3. Remaining electricity consumption can be offset by green certificates': '3. 剩余用电量可通过绿证抵消',
        '4. Surplus green electricity can participate in market-based transactions': '4. 多余绿电可参与市场化交易',
        'Recommended to purchase:': '建议购买：',
        'green certificates/month': '张绿证/月',
        'tons/month': '吨/月',

        // ===== Cost report / chart =====
        'CNY/month': '元/月',
        'kg CO₂/month': 'kg CO₂/月',

        // ===== Optimization suggestions (backend generated) =====
        'Switch to Retail Supplier': '切换到售电商',
        'Retail supplier offers better prices, estimated monthly savings:': '售电商提供更优惠的电价，预计月节省：',
        'Consider': '考虑',
        'Power Generation': '发电',
        'Switching to photovoltaic power can significantly reduce carbon emissions.': '切换到光伏发电可以显著减少碳排放。',
        'Current monthly carbon:': '当前月碳排放：',
        'With PV': '使用光伏后',
        'Sign a long-term power purchase agreement with the retail supplier': '与售电商签订长期购电协议',
        'Monitor retail supplier price fluctuations': '关注售电商电价波动',
        'Regularly evaluate supplier cost-effectiveness': '定期评估供应商性价比',
        'Evaluate rooftop or ground-mounted PV system feasibility': '评估屋顶或地面光伏系统可行性',
        'Conduct solar irradiance assessment': '进行太阳辐照度评估',
        'Request quotations from PV system providers': '向光伏系统供应商询价',
        'Analyze investment ROI and payback period': '分析投资回报率和回收期',
        'Shift Production to Valley Hours': '将生产转移到谷时',
        'Move production to off-peak hours for lower electricity costs': '将生产转移到非高峰时段以降低电费',
        'Reduce Peak Hour Usage': '减少高峰时段用电',

        // ===== Equipment recommendations (backend generated) =====
        'Energy Storage': '储能设备',
        'Variable Frequency Drive': '变频器',
        'LED Lighting': 'LED照明',
        'Compact Storage Unit': '紧凑型储能单元',
        'High-Performance VFD': '高性能变频器',
        'Replace traditional lighting with LED': '用LED替换传统照明',
        'Solar PV System': '光伏发电系统',
        'Power Factor Correction': '功率因数校正',
        'Smart Energy Management': '智能能源管理',
        'Rooftop solar panel installation': '屋顶光伏板安装',
        'Automatic power factor correction unit': '自动功率因数校正装置',
        'IoT-based energy monitoring system': '基于物联网的能源监控系统',

        // ===== Welcome/About page =====
        'Key capabilities:': '核心功能：',
        'Hourly cost analysis': '逐时成本分析',
        'with peak/normal/valley pricing': '含峰/平/谷电价',
        'Carbon emission calculation': '碳排放计算',
        'for grid vs. renewable sources': '电网 vs. 可再生能源对比',
        'Supplier comparison': '供应商对比',
        'between grid and third-party rates': '电网与第三方电价对比',
        'Factory configuration': '工厂配置',
        'with voltage levels and work schedules': '含电压等级和工作时间表',
        'PeakShift analyzes time-of-use electricity pricing to help industrial facilities reduce costs. The system calculates monthly expenses based on your factory\'s specifications and provides recommendations for shifting production to lower-cost periods.': 'PeakShift 分析分时电价，帮助工业设施降低成本。系统根据工厂参数计算月度费用，并提供将生产转移到低成本时段的建议。',
        'Smart energy management for modern factories.': '现代工厂的智能能源管理。',

        // ===== Chart axis labels =====
        'Time': '时间',
        'Price (CNY/kWh)': '电价（元/kWh）',

        // ===== Placeholders =====
        'e.g. Beijing Aluminum Electrolyzer': '例如：北京铝电解厂',
        'e.g. Chaoyang District, Beijing': '例如：北京市朝阳区',
        'e.g. 5000': '例如：5000',
        'e.g. 50000': '例如：50000',
        'e.g. 26': '例如：26',
        'your.email@company.com': '您的邮箱@公司.com',

        // ===== Policy notes (green power) =====
        'According to the policy of June 2025, existing projects put into operation before 1 June 2025 will be settled based on the coal-fired benchmark price': '根据2025年6月政策，2025年6月1日前投运的存量项目按燃煤基准价结算',
        'According to the policy of June 2025, incremental projects put into operation after 1 June 2025 will have their mechanism prices determined through bidding': '根据2025年6月政策，2025年6月1日后投运的增量项目通过竞价确定机制电价',
        'Mechanism electricity price for existing projects': '存量项目机制电价',

        // ===== Admin actions / notifications =====
        'Admin Notifications': '管理员通知',
        'No notifications': '暂无通知',
        'Status': '状态',
        'Actions': '操作',
        'Active': '正常',
        'Banned': '已封禁',
        'Ban': '封禁',
        'Unban': '解封',
        'Delete': '删除',
        'View': '查看',
        'Your account has been banned. Please contact the administrator.': '您的账号已被封禁，请联系管理员。',

        // ===== Misc missing =====
        'Outperforms': '优于',
        'of industry peers': '的同行',
        'Outperforms 7% of industry peers': '优于 7% 的同行',
        'less than': '低于',
        'greater than': '大于',
    },

    // Reverse dict (Chinese -> English) built automatically
    _reverseDict: null,

    getReverseDict() {
        if (!this._reverseDict) {
            this._reverseDict = {};
            for (const [en, zh] of Object.entries(this.dict)) {
                this._reverseDict[zh] = en;
            }
        }
        return this._reverseDict;
    },

    /**
     * Translate a single string
     */
    t(text) {
        if (!text || typeof text !== 'string') return text;
        const trimmed = text.trim();
        if (!trimmed) return text;
        
        // Never translate PeakShift brand name
        if (trimmed === 'PeakShift') return text;

        if (this.currentLang === 'zh') {
            // Exact match first
            if (this.dict[trimmed]) return this.dict[trimmed];
            
            // Partial match: replace known English phrases within the text
            let result = trimmed;
            // Sort keys by length (longest first) to avoid partial replacements
            const keys = Object.keys(this.dict).sort((a, b) => b.length - a.length);
            for (const key of keys) {
                if (key.length >= 5 && result.includes(key)) {
                    // Skip if the match is part of "PeakShift"
                    const idx = result.indexOf(key);
                    const before = result.substring(Math.max(0, idx - 10), idx);
                    const after = result.substring(idx + key.length, idx + key.length + 10);
                    if (before.includes('Peak') && key === 'Shift') continue;
                    if (after.includes('Shift') && key === 'Peak') continue;
                    if (key === 'Peak' && result.includes('PeakShift')) continue;
                    if (key === 'Shift' && result.includes('PeakShift')) continue;
                    result = result.replace(key, this.dict[key]);
                }
            }
            return result !== trimmed ? result : text;
        } else {
            // English: reverse lookup in case text is Chinese
            const rev = this.getReverseDict();
            if (rev[trimmed]) return rev[trimmed];

            const peerMatch = trimmed.match(/^优于\s*([0-9]+(?:\.[0-9]+)?)%\s*的同行$/);
            if (peerMatch) {
                return `Outperforms ${peerMatch[1]}% of industry peers`;
            }
            
            // Partial reverse match
            let result = trimmed;
            const revKeys = Object.keys(rev).sort((a, b) => b.length - a.length);
            for (const key of revKeys) {
                if ((key.length >= 4 || key === '优于' || key === '的同行') && result.includes(key)) {
                    result = result.replace(key, rev[key]);
                }
            }
            return result !== trimmed ? result : text;
        }
    },

    /**
     * Walk all text nodes in the document and translate them
     */
    translatePage() {
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode(node) {
                    // Skip script/style/textarea/input
                    const parent = node.parentElement;
                    if (!parent) return NodeFilter.FILTER_REJECT;
                    const tag = parent.tagName;
                    if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'TEXTAREA' || tag === 'NOSCRIPT') {
                        return NodeFilter.FILTER_REJECT;
                    }
                    // Skip if text is only whitespace
                    if (!node.textContent.trim()) return NodeFilter.FILTER_REJECT;
                    return NodeFilter.FILTER_ACCEPT;
                }
            }
        );

        const nodes = [];
        while (walker.nextNode()) nodes.push(walker.currentNode);

        for (const node of nodes) {
            const original = node.textContent.trim();
            if (!original) continue;

            // Skip PeakShift brand name and usernames (parent has no-translate class)
            const parent = node.parentElement;
            if (parent && (parent.classList.contains('no-translate') || parent.closest('.no-translate'))) {
                continue;
            }

            const translated = this.t(original);
            if (translated !== original) {
                // Preserve leading/trailing whitespace
                const leading = node.textContent.match(/^\s*/)[0];
                const trailing = node.textContent.match(/\s*$/)[0];
                node.textContent = leading + translated + trailing;
            }
        }

        // Also translate placeholders
        document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(el => {
            if (el.closest('.no-translate')) return;
            const ph = el.placeholder.trim();
            if (ph) {
                const translated = this.t(ph);
                if (translated !== ph) el.placeholder = translated;
            }
        });

        // Translate title attributes
        document.querySelectorAll('[title]').forEach(el => {
            if (el.closest('.no-translate')) return;
            const title = el.getAttribute('title').trim();
            if (title) {
                const translated = this.t(title);
                if (translated !== title) el.setAttribute('title', translated);
            }
        });

        // Update html lang
        document.documentElement.lang = this.currentLang === 'zh' ? 'zh-CN' : 'en';
    },

    /**
     * Apply translations (full page text node scan)
     */
    apply() {
        // Do full page text node scan
        this.translatePage();
        document.documentElement.classList.remove('i18n-preload');
    },

    /**
     * Switch language and apply
     */
    setLang(lang) {
        if (lang !== 'en' && lang !== 'zh') return;
        this.currentLang = lang;
        localStorage.setItem('lang', lang);
        this.apply();
        window.dispatchEvent(new CustomEvent('peakshift:languageChanged', {
            detail: { lang }
        }));
    },

    /**
     * Initialize on page load
     */
    init() {
        this.apply();
        // Re-apply translations after a short delay to let dynamic content render
        setTimeout(() => this.apply(), 100);

        // Also observe DOM changes to translate dynamically added content
        const observer = new MutationObserver((mutations) => {
            let shouldTranslate = false;
            for (const mutation of mutations) {
                if (mutation.addedNodes.length > 0) {
                    shouldTranslate = true;
                    break;
                }
            }
            if (shouldTranslate) {
                // Debounce
                clearTimeout(this._translateTimeout);
                this._translateTimeout = setTimeout(() => this.apply(), 200);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    },

    _translateTimeout: null
};

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
    I18N.init();
});
