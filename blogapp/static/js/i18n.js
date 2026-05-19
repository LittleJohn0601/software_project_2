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

        // ===== Factory Card =====
        'Voltage:': '电压：',
        'Capacity:': '容量：',
        'Capacity fee': '容量费',
        'Monthly usage': '月用电量',
        'Working days': '工作天数',
        'Work periods:': '工作时段：',

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
        'System data (electricity prices, carbon factors, etc.) is automatically synced from Excel files. To modify, edit the relevant files in the data/ directory. The system will detect and update on startup.': '系统数据（电价、碳因子等）通过 Excel 文件自动同步。如需修改，请编辑 data/ 目录下的相关文件，系统将在启动时自动检测并更新。',
        'Electricity Price Data': '电价数据',
        'Carbon Emission Factors': '碳排放因子',
        'Contains 24-hour time-of-use pricing and grid selling prices': '包含24小时分时电价和电网售卖价格数据',
        'Defined in': '定义于',

        // ===== Optimization / Benchmark =====
        'Photovoltaic Power Comparison': '光伏发电对比',
        'Current Grid Carbon': '当前电网碳排',
        'With Photovoltaic': '使用光伏后',
        'Reduction Potential': '减排潜力',
        'High impact': '高影响',
        'Medium impact': '中影响',
        'Low impact': '低影响',
        'Action recommendations:': '行动建议：',
        'The current power plan is already well optimized!': '当前用电方案已经很优化了！',
        'Failed to load optimization suggestions. Please try again later.': '加载优化建议失败，请稍后重试。',
        'Excellent': '优秀',
        'Good': '良好',
        'Average': '一般',
        'Poor': '较差',
        'Monthly Electricity Consumption': '月用电量',
        'Estimated Monthly Output': '预估月产值',
        'kWh/ten thousand yuan': 'kWh/万元',
        'Recommended plan': '推荐方案',
        'Monthly electricity consumption:': '月用电量：',
        'Estimated monthly cost:': '预估月费用：',
        'Carbon reduction:': '碳减排：',
        'Official Purchase Platforms': '官方采购平台',
        'Implementation Steps': '实施步骤',
        'Investment:': '投资：',
        'Annual Saving:': '年节省：',
        'Payback:': '回收期：',

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

        if (this.currentLang === 'zh') {
            return this.dict[trimmed] || text;
        } else {
            // English: reverse lookup in case text is Chinese
            const rev = this.getReverseDict();
            return rev[trimmed] || text;
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
     * Apply translations (data-i18n attributes + full page scan)
     */
    apply() {
        // First handle data-i18n elements (for backward compat)
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            // data-i18n stores the English text as key
            if (this.currentLang === 'zh' && this.dict[key]) {
                el.textContent = this.dict[key];
            } else if (this.currentLang === 'en') {
                const rev = this.getReverseDict();
                // If current text is Chinese, revert to English key
                if (rev[el.textContent.trim()]) {
                    el.textContent = key;
                } else {
                    el.textContent = key;
                }
            }
        });

        // Then do full page text node scan
        this.translatePage();
    },

    /**
     * Switch language and apply
     */
    setLang(lang) {
        if (lang !== 'en' && lang !== 'zh') return;
        // If switching to same language, still re-apply (for newly rendered content)
        this.currentLang = lang;
        localStorage.setItem('lang', lang);
        // Reload page to ensure clean translation (avoids partial state)
        window.location.reload();
    },

    /**
     * Initialize on page load
     */
    init() {
        // Apply translations after a short delay to let dynamic content render
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
