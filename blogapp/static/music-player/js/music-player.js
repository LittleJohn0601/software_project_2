/* ========================================
   Global Music Player Script
   独立音乐播放器脚本 - 可安全删除
   ======================================== */

(function() {
    'use strict';
    
    // 防止重复初始化
    if (window.MusicPlayerInitialized) {
        console.log('🎵 Music player already initialized');
        return;
    }
    window.MusicPlayerInitialized = true;
    
    console.log('🎵 Initializing Global Music Player...');
    
    // ========================================
    // 配置项 - 可自定义
    // ========================================
    const CONFIG = {
        // 音频文件夹路径
        audioFolder: '/static/music-player/audio/',
        
        // 播放列表文件名（可通过 data-playlist 属性自定义）
        playlistFile: 'playlist.json',
        
        // 默认音量 (0.0 - 1.0)
        defaultVolume: 0.3,
        
        // 是否自动播放
        autoPlay: true,
        
        // 是否循环播放整个播放列表
        loop: true,
        
        // 本地存储键名前缀
        storageKeyPrefix: 'peakshift_music_'
    };
    
    // ========================================
    // 音乐播放器类
    // ========================================
    class MusicPlayer {
        constructor(playlistName = 'playlist') {
            this.audio = null;
            this.isPlaying = false;
            this.isMuted = false;
            this.volume = CONFIG.defaultVolume;
            this.button = null;
            this.playlist = [];
            this.currentIndex = 0;
            this.savedTime = 0;  // 保存的播放位置
            this.userPaused = false;  // 用户是否手动暂停
            this.playlistName = playlistName;  // 播放列表名称
            this.storageKey = CONFIG.storageKeyPrefix + playlistName;  // 每个播放列表独立存储
            
            this.init();
        }
        
        async init() {
            // 不加载保存的状态，每次都默认自动播放
            this.isMuted = false;
            
            // 获取播放列表
            await this.loadPlaylist();
            
            if (this.playlist.length === 0) {
                console.warn('⚠️ No audio files found in audio folder');
                return;
            }
            
            // 加载播放进度
            this.loadPlaybackState();
            
            // 创建音频元素
            this.createAudio();
            
            // 创建播放器按钮
            this.createButton();
            
            // 绑定事件
            this.bindEvents();
            
            // 自动播放（只有在用户没有手动暂停过的情况下）
            if (CONFIG.autoPlay && !this.userPaused) {
                this.attemptAutoPlay();
            }
            
            console.log('✅ Music player initialized with', this.playlist.length, 'songs');
        }
        
        async loadPlaylist() {
            try {
                // 从指定的播放列表文件读取
                const playlistFile = `${this.playlistName}.json`;
                const response = await fetch(CONFIG.audioFolder + playlistFile);
                const data = await response.json();
                
                this.playlist = data.playlist.map(filename => 
                    CONFIG.audioFolder + filename
                );
                
                console.log(`📋 Loaded playlist (${this.playlistName}):`, data.playlist);
                
            } catch (error) {
                console.warn(`⚠️ Could not load ${this.playlistName}.json:`, error);
                console.log('💡 Please create the playlist file in audio folder');
                this.playlist = [];
            }
        }
        
        createAudio() {
            this.audio = new Audio();
            this.audio.src = this.playlist[this.currentIndex];
            this.audio.volume = this.volume;
            this.audio.preload = 'auto';
            
            // 恢复播放进度
            if (this.savedTime > 0) {
                this.audio.currentTime = this.savedTime;
                console.log('⏩ Restored playback position:', this.savedTime.toFixed(1), 'seconds');
            }
            
            // 音频事件监听
            this.audio.addEventListener('play', () => {
                this.isPlaying = true;
                this.updateButton();
            });
            
            this.audio.addEventListener('pause', () => {
                this.isPlaying = false;
                this.updateButton();
            });
            
            // 定期保存播放进度
            this.audio.addEventListener('timeupdate', () => {
                this.savePlaybackState();
            });
            
            this.audio.addEventListener('ended', () => {
                // 播放下一首
                this.playNext();
            });
            
            this.audio.addEventListener('error', (e) => {
                console.error('❌ Audio loading error:', e);
                console.log('Failed to load:', this.audio.src);
                // 尝试播放下一首
                this.playNext();
            });
        }
        
        playNext() {
            // 先保存当前状态，清除播放位置
            this.savedTime = 0;
            this.savePlaybackState();
            
            this.currentIndex++;
            
            // 如果到达列表末尾
            if (this.currentIndex >= this.playlist.length) {
                if (CONFIG.loop) {
                    // 循环播放，回到第一首
                    this.currentIndex = 0;
                } else {
                    // 不循环，停止播放
                    this.pause();
                    return;
                }
            }
            
            // 加载并播放下一首
            this.audio.src = this.playlist[this.currentIndex];
            this.audio.currentTime = 0;
            this.play();
            console.log('▶️ Playing:', this.playlist[this.currentIndex]);
        }
        
        createButton() {
            // 创建容器
            const container = document.createElement('div');
            container.className = 'music-player-container';
            container.id = 'musicPlayerContainer';
            
            // 创建按钮
            const button = document.createElement('button');
            button.className = 'music-player-btn';
            button.id = 'musicPlayerBtn';
            button.setAttribute('aria-label', 'Toggle music');
            button.setAttribute('title', 'Toggle music');
            
            // 创建图标
            const icon = document.createElement('span');
            icon.className = 'music-icon';
            icon.innerHTML = '🎵';
            
            // 创建音波动画
            const soundWave = document.createElement('div');
            soundWave.className = 'sound-wave';
            soundWave.innerHTML = `
                <div class="sound-bar"></div>
                <div class="sound-bar"></div>
                <div class="sound-bar"></div>
            `;
            
            // 创建提示文字
            const tooltip = document.createElement('span');
            tooltip.className = 'music-tooltip';
            tooltip.textContent = 'Click to toggle music';
            
            // 组装
            button.appendChild(icon);
            button.appendChild(soundWave);
            button.appendChild(tooltip);
            container.appendChild(button);
            
            // 添加到页面
            document.body.appendChild(container);
            
            this.button = button;
            this.updateButton();
        }
        
        bindEvents() {
            // 点击切换播放/暂停
            this.button.addEventListener('click', () => {
                this.toggle();
            });
            
            // 监听用户交互（用于自动播放）
            const enableAutoPlay = () => {
                if (CONFIG.autoPlay && !this.isMuted && !this.isPlaying) {
                    this.play();
                }
                // 只需要一次交互
                document.removeEventListener('click', enableAutoPlay);
                document.removeEventListener('keydown', enableAutoPlay);
            };
            
            document.addEventListener('click', enableAutoPlay, { once: true });
            document.addEventListener('keydown', enableAutoPlay, { once: true });
        }
        
        attemptAutoPlay() {
            // 尝试自动播放（可能会被浏览器阻止）
            const playPromise = this.audio.play();
            
            if (playPromise !== undefined) {
                playPromise
                    .then(() => {
                        console.log('✅ Auto-play started');
                    })
                    .catch((error) => {
                        console.log('⚠️ Auto-play blocked by browser. Waiting for user interaction...');
                        // 浏览器阻止了自动播放，等待用户交互
                    });
            }
        }
        
        play() {
            if (!this.audio) return;
            
            const playPromise = this.audio.play();
            
            if (playPromise !== undefined) {
                playPromise
                    .then(() => {
                        this.isMuted = false;
                        this.userPaused = false; // 用户点击播放，清除暂停标记
                        this.savePlaybackState();
                        console.log('▶️ Music playing');
                    })
                    .catch((error) => {
                        console.log('⚠️ Play failed:', error.message);
                    });
            }
        }
        
        pause() {
            if (!this.audio) return;
            
            this.audio.pause();
            this.isMuted = true;
            this.userPaused = true; // 用户手动暂停，设置标记
            this.savePlaybackState();
            console.log('⏸️ Music paused by user');
        }
        
        toggle() {
            if (this.isPlaying) {
                this.pause();
            } else {
                this.play();
            }
        }
        
        updateButton() {
            if (!this.button) return;
            
            if (this.isPlaying) {
                this.button.classList.add('playing');
                this.button.classList.remove('muted');
                this.button.querySelector('.music-tooltip').textContent = 'Click to mute';
            } else {
                this.button.classList.remove('playing');
                this.button.classList.add('muted');
                this.button.querySelector('.music-tooltip').textContent = 'Click to play';
            }
        }
        
        loadPlaybackState() {
            try {
                const saved = localStorage.getItem(this.storageKey);
                if (saved) {
                    const state = JSON.parse(saved);
                    this.currentIndex = state.currentIndex || 0;
                    // 不恢复播放进度，每次都从头开始
                    this.savedTime = 0;
                    this.volume = state.volume || CONFIG.defaultVolume;
                    this.userPaused = state.userPaused || false; // 记录用户是否手动暂停
                    console.log('📂 Loaded playback state (progress reset):', state);
                } else {
                    this.currentIndex = 0;
                    this.savedTime = 0;
                    this.userPaused = false;
                }
            } catch (error) {
                console.warn('⚠️ Failed to load playback state:', error);
                this.currentIndex = 0;
                this.savedTime = 0;
                this.userPaused = false;
            }
        }
        
        savePlaybackState() {
            if (!this.audio) return;
            
            try {
                const state = {
                    currentIndex: this.currentIndex,
                    currentTime: this.audio.currentTime,
                    volume: this.volume,
                    userPaused: this.userPaused, // 保存用户暂停状态
                    timestamp: Date.now()
                };
                localStorage.setItem(this.storageKey, JSON.stringify(state));
            } catch (error) {
                // 静默失败，不影响播放
            }
        }
        
        // 公共方法：销毁播放器
        destroy() {
            if (this.audio) {
                this.audio.pause();
                this.audio.src = '';
                this.audio = null;
            }
            
            if (this.button && this.button.parentElement) {
                this.button.parentElement.remove();
            }
            
            window.MusicPlayerInitialized = false;
            console.log('🗑️ Music player destroyed');
        }
    }
    
    // ========================================
    // 初始化
    // ========================================
    let player = null;
    
    // 从 body 标签的 data-playlist 属性读取播放列表名称
    const getPlaylistName = () => {
        const bodyElement = document.body;
        return bodyElement.getAttribute('data-playlist') || 'playlist';
    };
    
    // DOM 加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            const playlistName = getPlaylistName();
            player = new MusicPlayer(playlistName);
            console.log(`🎵 Music player initialized with playlist: ${playlistName}`);
        });
    } else {
        const playlistName = getPlaylistName();
        player = new MusicPlayer(playlistName);
        console.log(`🎵 Music player initialized with playlist: ${playlistName}`);
    }
    
    // 暴露到全局（可选，用于调试）
    window.MusicPlayer = {
        getInstance: () => player,
        destroy: () => player && player.destroy()
    };
    
})();
