/**
 * PeakShift i18n (Internationalization) Module
 * Supports English and Chinese language switching.
 * Usage: Add data-i18n="key" attribute to HTML elements.
 */

const I18N = {
    currentLang: localStorage.getItem('lang') || 'en',

    translations: {
        en: {
            // ===== Navbar =====
            'nav.admin_console': 'PeakShift Admin Console',
            'nav.logout': 'Log out',
            'nav.admin': 'Admin',
            'nav.settings': 'Settings',

            // ===== Auth Page =====
            'auth.welcome_back': 'Welcome back!',
            'auth.enter_details': 'Please enter your details',
            'auth.username_or_email': 'Username or Email',
            'auth.username_placeholder': 'Enter your username or email',
            'auth.password': 'Password',
            'auth.login': 'Log in',
            'auth.logging_in': 'Logging in...',
            'auth.no_account': "Don't have an account?",
            'auth.sign_up': 'Sign Up',
            'auth.create_account': 'Create an account',
            'auth.join_subtitle': 'Join PeakShift to optimize your energy costs',
            'auth.username': 'Username',
            'auth.username_placeholder_reg': 'Choose a username',
            'auth.username_hint': '3-32 characters, can only contain letters, numbers, underscores, and hyphens',
            'auth.email': 'Email',
            'auth.email_hint': 'Maximum 120 characters',
            'auth.password_hint': '6-128 characters, recommended to include uppercase and lowercase letters, numbers, and special characters',
            'auth.create_btn': 'Create Account',
            'auth.creating': 'Creating Account...',
            'auth.have_account': 'Already have an account?',
            'auth.login_link': 'Log in',
            'auth.invalid_credentials': 'Invalid username or password',
            'auth.reg_success': 'Registration successful! Please log in',
            'auth.sign_in': 'Sign in',
            'auth.get_started': 'Get started',

            // ===== Welcome Page =====
            'welcome.hero_title': 'Optimize electricity costs with peak-valley pricing',
            'welcome.hero_subtitle': 'Analyze time-of-use electricity rates, calculate monthly costs, and get actionable recommendations to reduce expenses and carbon emissions.',
            'welcome.start_trial': 'Start free trial',
            'welcome.learn_more': 'Learn more',
            'welcome.features': 'Features',
            'welcome.about': 'About',
            'welcome.section_title': 'Everything you need to optimize energy',
            'welcome.section_subtitle': 'Analyze peak-valley pricing, calculate costs, and get recommendations to reduce your factory\'s electricity expenses.',
            'welcome.cost_calc': 'Cost Calculation',
            'welcome.cost_calc_desc': 'Calculate monthly electricity costs based on your factory\'s voltage level, transformer capacity, and time-of-use pricing.',
            'welcome.peak_valley': 'Peak-Valley Analysis',
            'welcome.peak_valley_desc': 'Compare hourly electricity prices between grid and supplier rates to identify the best times for production.',
            'welcome.carbon': 'Carbon Tracking',
            'welcome.carbon_desc': 'Calculate carbon emissions from grid electricity and compare with potential savings from renewable sources.',
            'welcome.factory_mgmt': 'Factory Management',
            'welcome.factory_mgmt_desc': 'Manage multiple factories with customizable work schedules, voltage levels, and transformer specifications.',
            'welcome.optimization': 'Optimization Suggestions',
            'welcome.optimization_desc': 'Get actionable recommendations on when to shift production to valley hours for maximum cost savings.',
            'welcome.supplier': 'Supplier Comparison',
            'welcome.supplier_desc': 'Compare costs between purchasing from grid vs. third-party suppliers with detailed hourly breakdowns.',
            'welcome.how_it_works': 'How PeakShift works',
            'welcome.get_started_today': 'Get started today',

            // ===== Dashboard =====
            'dash.factory_mgmt': 'Factory management',
            'dash.factory_desc': 'Manage your factory information, view power data and cost analysis',
            'dash.create_factory': 'Create Factory',
            'dash.no_factories': 'No factories yet',
            'dash.no_factories_hint': 'Click the "Create Factory" button to create your first factory',
            'dash.create_now': 'Create now',
            'dash.return_list': 'Return to factory list',
            'dash.voltage_level': 'Voltage level',
            'dash.transformer_cap': 'Transformer capacity',
            'dash.daily_usage': 'Daily usage',
            'dash.working_days': 'Working days per month',
            'dash.today_usage': "Today's usage",
            'dash.monthly_cost': 'Monthly cost',
            'dash.carbon_footprint': 'Carbon footprint',
            'dash.saving_potential': 'Saving potential',
            'dash.cost': 'Cost',
            'dash.carbon': 'Carbon',
            'dash.edit': 'Edit',
            'dash.view_details': 'View details',
            'dash.delete': 'Delete',
            'dash.real_time_price': 'Real-time price chart',
            'dash.energy_mix': 'Energy mix pie chart',
            'dash.cost_report': 'Cost report',
            'dash.opt_suggestions': 'Optimization suggestions',
            'dash.loading': 'Loading...',
            'dash.benchmark': 'Industry Efficiency Benchmark',
            'dash.green_power': 'Green electricity procurement guide',
            'dash.equipment': 'Energy Saving Equipment',

            // ===== Factory Modal =====
            'modal.create_factory': 'Create Factory',
            'modal.edit_factory': 'Edit Factory',
            'modal.factory_name': 'Factory name',
            'modal.factory_location': 'Factory location',
            'modal.industry_type': 'Industry type',
            'modal.please_select': 'Please select',
            'modal.voltage_level': 'Voltage level',
            'modal.transformer_cap': 'Transformer capacity (kVA)',
            'modal.daily_usage': 'Daily usage (kWh/day)',
            'modal.working_days': 'Working days per month',
            'modal.work_periods': 'Work periods',
            'modal.start_time': 'Start time',
            'modal.end_time': 'End time',
            'modal.add': 'Add',
            'modal.work_periods_hint': 'Add factory work periods, e.g. 8:00-12:00, 13:00-18:00',
            'modal.cancel': 'Cancel',
            'modal.create': 'Create',
            'modal.save': 'Save',

            // ===== Settings =====
            'settings.title': 'System settings',
            'settings.ui_mode': 'UI mode',
            'settings.full_mode': 'Full mode',
            'settings.lite_mode': 'Lite mode',
            'settings.full_desc': 'Full mode: full effects, suitable for high-performance devices',
            'settings.lite_desc': 'Lite mode: reduced animation, suitable for low-performance devices',
            'settings.perf_test': 'Performance test',
            'settings.start_benchmark': 'Start benchmark test (10 seconds)',
            'settings.show_fps': 'Show real-time FPS',
            'settings.close': 'Close',
            'settings.save': 'Save settings',
            'settings.language': 'Language',
            'settings.lang_en': 'English',
            'settings.lang_zh': '中文',

            // ===== Admin Dashboard =====
            'admin.total_users': 'Total Registered Users',
            'admin.total_factories': 'Total Factories',
            'admin.total_usage': 'Total Monthly Usage (kWh)',
            'admin.total_carbon': 'Total Carbon Emission (kg CO₂)',
            'admin.user_mgmt': 'User Management',
            'admin.factory_mgmt': 'Factory Management',
            'admin.system_data': 'System Data',
            'admin.user_list': 'User List',
            'admin.factory_list': 'Factory List',
            'admin.th_id': 'ID',
            'admin.th_username': 'Username',
            'admin.th_email': 'Email',
            'admin.th_registered': 'Registered',
            'admin.th_factories': 'Factories',
            'admin.th_usage': 'Total Usage (kWh)',
            'admin.th_carbon': 'Carbon (kg)',
            'admin.th_name': 'Factory Name',
            'admin.th_location': 'Location',
            'admin.th_industry': 'Industry Type',
            'admin.th_voltage': 'Voltage Level',
            'admin.th_monthly_usage': 'Monthly Usage (kWh)',
            'admin.th_owner': 'Owner',
            'admin.no_users': 'No user data available',
            'admin.no_factories': 'No factory data available',
            'admin.system_data_mgmt': 'System Data Management',
            'admin.system_data_desc': 'System data (electricity prices, carbon factors, etc.) is automatically synced from Excel files. To modify, edit the relevant files in the data/ directory. The system will detect and update on startup.',
            'admin.price_data': 'Electricity Price Data',
            'admin.carbon_factors': 'Carbon Emission Factors',

            // ===== Password Strength =====
            'pwd.weak': 'Weak',
            'pwd.medium': 'Medium',
            'pwd.strong': 'Strong',
        },

        zh: {
            // ===== Navbar =====
            'nav.admin_console': 'PeakShift 管理员控制台',
            'nav.logout': '退出登录',
            'nav.admin': '管理员',
            'nav.settings': '设置',

            // ===== Auth Page =====
            'auth.welcome_back': '欢迎回来！',
            'auth.enter_details': '请输入您的账号信息',
            'auth.username_or_email': '用户名或邮箱',
            'auth.username_placeholder': '请输入用户名或邮箱',
            'auth.password': '密码',
            'auth.login': '登录',
            'auth.logging_in': '登录中...',
            'auth.no_account': '还没有账号？',
            'auth.sign_up': '注册',
            'auth.create_account': '创建账号',
            'auth.join_subtitle': '加入 PeakShift，优化您的用电成本',
            'auth.username': '用户名',
            'auth.username_placeholder_reg': '请选择一个用户名',
            'auth.username_hint': '3-32个字符，只能包含字母、数字、下划线和连字符',
            'auth.email': '邮箱',
            'auth.email_hint': '最多120个字符',
            'auth.password_hint': '6-128个字符，建议包含大小写字母、数字和特殊字符',
            'auth.create_btn': '创建账号',
            'auth.creating': '创建中...',
            'auth.have_account': '已有账号？',
            'auth.login_link': '登录',
            'auth.invalid_credentials': '用户名或密码错误',
            'auth.reg_success': '注册成功！请登录',
            'auth.sign_in': '登录',
            'auth.get_started': '立即开始',

            // ===== Welcome Page =====
            'welcome.hero_title': '利用峰谷电价优化用电成本',
            'welcome.hero_subtitle': '分析分时电价，计算月度成本，获取可操作的建议来降低费用和碳排放。',
            'welcome.start_trial': '免费试用',
            'welcome.learn_more': '了解更多',
            'welcome.features': '功能',
            'welcome.about': '关于',
            'welcome.section_title': '优化能源所需的一切',
            'welcome.section_subtitle': '分析峰谷电价，计算成本，获取降低工厂电费的建议。',
            'welcome.cost_calc': '成本计算',
            'welcome.cost_calc_desc': '根据工厂的电压等级、变压器容量和分时电价计算月度电费。',
            'welcome.peak_valley': '峰谷分析',
            'welcome.peak_valley_desc': '比较电网和售电商的逐时电价，找出最佳生产时段。',
            'welcome.carbon': '碳排放追踪',
            'welcome.carbon_desc': '计算电网用电的碳排放，并与可再生能源的潜在节省进行对比。',
            'welcome.factory_mgmt': '工厂管理',
            'welcome.factory_mgmt_desc': '管理多个工厂，自定义工作时间、电压等级和变压器规格。',
            'welcome.optimization': '优化建议',
            'welcome.optimization_desc': '获取可操作的建议，了解何时将生产转移到谷时以最大化节省。',
            'welcome.supplier': '供应商对比',
            'welcome.supplier_desc': '对比电网购电与第三方供应商的成本，提供详细的逐时分析。',
            'welcome.how_it_works': 'PeakShift 如何工作',
            'welcome.get_started_today': '立即开始使用',

            // ===== Dashboard =====
            'dash.factory_mgmt': '工厂管理',
            'dash.factory_desc': '管理工厂信息，查看用电数据和成本分析',
            'dash.create_factory': '创建工厂',
            'dash.no_factories': '暂无工厂',
            'dash.no_factories_hint': '点击"创建工厂"按钮创建您的第一个工厂',
            'dash.create_now': '立即创建',
            'dash.return_list': '返回工厂列表',
            'dash.voltage_level': '电压等级',
            'dash.transformer_cap': '变压器容量',
            'dash.daily_usage': '日用电量',
            'dash.working_days': '月工作天数',
            'dash.today_usage': '今日用电',
            'dash.monthly_cost': '月度费用',
            'dash.carbon_footprint': '碳排放',
            'dash.saving_potential': '节省潜力',
            'dash.cost': '成本',
            'dash.carbon': '碳排',
            'dash.edit': '编辑',
            'dash.view_details': '查看详情',
            'dash.delete': '删除',
            'dash.real_time_price': '实时电价图表',
            'dash.energy_mix': '能源结构饼图',
            'dash.cost_report': '成本报告',
            'dash.opt_suggestions': '优化建议',
            'dash.loading': '加载中...',
            'dash.benchmark': '行业能效基准',
            'dash.green_power': '绿电采购引导',
            'dash.equipment': '节能设备推荐',

            // ===== Factory Modal =====
            'modal.create_factory': '创建工厂',
            'modal.edit_factory': '编辑工厂',
            'modal.factory_name': '工厂名称',
            'modal.factory_location': '工厂位置',
            'modal.industry_type': '行业类型',
            'modal.please_select': '请选择',
            'modal.voltage_level': '电压等级',
            'modal.transformer_cap': '变压器容量 (kVA)',
            'modal.daily_usage': '日用电量 (kWh/天)',
            'modal.working_days': '月工作天数',
            'modal.work_periods': '工作时段',
            'modal.start_time': '开始时间',
            'modal.end_time': '结束时间',
            'modal.add': '添加',
            'modal.work_periods_hint': '添加工厂工作时段，如 8:00-12:00, 13:00-18:00',
            'modal.cancel': '取消',
            'modal.create': '创建',
            'modal.save': '保存',

            // ===== Settings =====
            'settings.title': '系统设置',
            'settings.ui_mode': 'UI 模式',
            'settings.full_mode': '完整模式',
            'settings.lite_mode': '轻量模式',
            'settings.full_desc': '完整模式：全部特效，适合高性能设备',
            'settings.lite_desc': '轻量模式：减少动画，适合低性能设备',
            'settings.perf_test': '性能测试',
            'settings.start_benchmark': '开始性能测试（10秒）',
            'settings.show_fps': '显示实时帧率',
            'settings.close': '关闭',
            'settings.save': '保存设置',
            'settings.language': '语言',
            'settings.lang_en': 'English',
            'settings.lang_zh': '中文',

            // ===== Admin Dashboard =====
            'admin.total_users': '注册用户总数',
            'admin.total_factories': '工厂总数',
            'admin.total_usage': '总月用电量 (kWh)',
            'admin.total_carbon': '总碳排放 (kg CO₂)',
            'admin.user_mgmt': '用户管理',
            'admin.factory_mgmt': '工厂管理',
            'admin.system_data': '系统数据',
            'admin.user_list': '用户列表',
            'admin.factory_list': '工厂列表',
            'admin.th_id': 'ID',
            'admin.th_username': '用户名',
            'admin.th_email': '邮箱',
            'admin.th_registered': '注册时间',
            'admin.th_factories': '工厂数量',
            'admin.th_usage': '总用电量 (kWh)',
            'admin.th_carbon': '碳排放 (kg)',
            'admin.th_name': '工厂名称',
            'admin.th_location': '位置',
            'admin.th_industry': '行业类型',
            'admin.th_voltage': '电压等级',
            'admin.th_monthly_usage': '月用电量 (kWh)',
            'admin.th_owner': '所属用户',
            'admin.no_users': '暂无用户数据',
            'admin.no_factories': '暂无工厂数据',
            'admin.system_data_mgmt': '系统数据管理',
            'admin.system_data_desc': '系统数据（电价、碳因子等）通过 Excel 文件自动同步。如需修改，请编辑 data/ 目录下的相关文件，系统将在启动时自动检测并更新。',
            'admin.price_data': '电价数据',
            'admin.carbon_factors': '碳排放因子',

            // ===== Password Strength =====
            'pwd.weak': '弱',
            'pwd.medium': '中',
            'pwd.strong': '强',
        }
    },

    /**
     * Get translation for a key
     */
    t(key) {
        const lang = this.translations[this.currentLang];
        return lang && lang[key] ? lang[key] : key;
    },

    /**
     * Apply translations to all elements with data-i18n attribute
     */
    apply() {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            const text = this.t(key);
            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                if (el.getAttribute('data-i18n-attr') === 'placeholder') {
                    el.placeholder = text;
                } else {
                    el.value = text;
                }
            } else if (el.tagName === 'OPTION') {
                el.textContent = text;
            } else {
                el.textContent = text;
            }
        });

        // Update html lang attribute
        document.documentElement.lang = this.currentLang === 'zh' ? 'zh-CN' : 'en';
    },

    /**
     * Switch language
     */
    setLang(lang) {
        if (this.translations[lang]) {
            this.currentLang = lang;
            localStorage.setItem('lang', lang);
            this.apply();
        }
    },

    /**
     * Initialize - apply saved language on page load
     */
    init() {
        this.apply();
    }
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    I18N.init();
});
