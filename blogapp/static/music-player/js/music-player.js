/* ========================================
   Global Music Player Script
   Standalone music player script - safe to remove
   ======================================== */

(function() {
    'use strict';
    
    // Prevent duplicate initialization
    if (window.MusicPlayerInitialized) {
        console.log('🎵 Music player already initialized');
        return;
    }
    window.MusicPlayerInitialized = true;
    
    console.log('🎵 Initializing Global Music Player...');
    
    // ========================================
    // Configuration - customizable
    // ========================================
    const CONFIG = {
        // Audio folder path
        audioFolder: '/static/music-player/audio/',
        
        // Playlist file name (customizable via data-playlist attribute)
        playlistFile: 'playlist.json',
        
        // Default volume (0.0 - 1.0)
        defaultVolume: 0.3,
        
        // Auto-play enabled
        autoPlay: true,
        
        // Loop through the whole playlist
        loop: true,
        
        // Local storage key prefix
        storageKeyPrefix: 'peakshift_music_'
    };
    
    // ========================================
    // Music player class
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
            this.savedTime = 0;  // Saved playback position
            this.userPaused = false;  // Whether user manually paused
            this.playlistName = playlistName;  // Playlist name
            this.storageKey = CONFIG.storageKeyPrefix + playlistName;  // Separate storage per playlist
            
            this.init();
        }
        
        async init() {
            // Do not load saved state; default to auto-play each time
            this.isMuted = false;
            
            // Load playlist
            await this.loadPlaylist();
            
            if (this.playlist.length === 0) {
                console.warn('⚠️ No audio files found in audio folder');
                return;
            }
            
            // Load playback state
            this.loadPlaybackState();
            
            // Create audio element
            this.createAudio();
            
            // Create player button
            this.createButton();
            
            // Bind events
            this.bindEvents();
            
            // Auto-play (only if user has not manually paused)
            if (CONFIG.autoPlay && !this.userPaused) {
                this.attemptAutoPlay();
            }
            
            console.log('✅ Music player initialized with', this.playlist.length, 'songs');
        }
        
        async loadPlaylist() {
            try {
                // Read from the specified playlist file
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
            
            // Restore playback position
            if (this.savedTime > 0) {
                this.audio.currentTime = this.savedTime;
                console.log('⏩ Restored playback position:', this.savedTime.toFixed(1), 'seconds');
            }
            
            // Audio event listeners
            this.audio.addEventListener('play', () => {
                this.isPlaying = true;
                this.updateButton();
            });
            
            this.audio.addEventListener('pause', () => {
                this.isPlaying = false;
                this.updateButton();
            });
            
            // Periodically save playback progress
            this.audio.addEventListener('timeupdate', () => {
                this.savePlaybackState();
            });
            
            this.audio.addEventListener('ended', () => {
                // Play the next track
                this.playNext();
            });
            
            this.audio.addEventListener('error', (e) => {
                console.error('❌ Audio loading error:', e);
                console.log('Failed to load:', this.audio.src);
                // Try the next track
                this.playNext();
            });
        }
        
        playNext() {
            // Save current state first and reset playback position
            this.savedTime = 0;
            this.savePlaybackState();
            
            this.currentIndex++;
            
            // If we reached the end of the playlist
            if (this.currentIndex >= this.playlist.length) {
                if (CONFIG.loop) {
                    // Loop playback back to the first track
                    this.currentIndex = 0;
                } else {
                    // Stop playback when not looping
                    this.pause();
                    return;
                }
            }
            
            // Load and play the next track
            this.audio.src = this.playlist[this.currentIndex];
            this.audio.currentTime = 0;
            this.play();
            console.log('▶️ Playing:', this.playlist[this.currentIndex]);
        }
        
        createButton() {
            // Create container
            const container = document.createElement('div');
            container.className = 'music-player-container';
            container.id = 'musicPlayerContainer';
            
            // Create button
            const button = document.createElement('button');
            button.className = 'music-player-btn';
            button.id = 'musicPlayerBtn';
            button.setAttribute('aria-label', 'Toggle music');
            button.setAttribute('title', 'Toggle music');
            
            // Create icon
            const icon = document.createElement('span');
            icon.className = 'music-icon';
            icon.innerHTML = '🎵';
            
            // Create sound wave animation
            const soundWave = document.createElement('div');
            soundWave.className = 'sound-wave';
            soundWave.innerHTML = `
                <div class="sound-bar"></div>
                <div class="sound-bar"></div>
                <div class="sound-bar"></div>
            `;
            
            // Create tooltip text
            const tooltip = document.createElement('span');
            tooltip.className = 'music-tooltip';
            tooltip.textContent = 'Click to toggle music';
            
            // Assemble
            button.appendChild(icon);
            button.appendChild(soundWave);
            button.appendChild(tooltip);
            container.appendChild(button);
            
            // Add to page
            document.body.appendChild(container);
            
            this.button = button;
            this.updateButton();
        }
        
        bindEvents() {
            // Toggle play/pause on click
            this.button.addEventListener('click', () => {
                this.toggle();
            });
            
            // Listen for user interaction (for auto-play)
            const enableAutoPlay = () => {
                if (CONFIG.autoPlay && !this.isMuted && !this.isPlaying) {
                    this.play();
                }
                // Only need one interaction
                document.removeEventListener('click', enableAutoPlay);
                document.removeEventListener('keydown', enableAutoPlay);
            };
            
            document.addEventListener('click', enableAutoPlay, { once: true });
            document.addEventListener('keydown', enableAutoPlay, { once: true });
        }
        
        attemptAutoPlay() {
            // Attempt auto-play (may be blocked by browser)
            const playPromise = this.audio.play();
            
            if (playPromise !== undefined) {
                playPromise
                    .then(() => {
                        console.log('✅ Auto-play started');
                    })
                    .catch((error) => {
                        console.log('⚠️ Auto-play blocked by browser. Waiting for user interaction...');
                        // Browser blocked auto-play; wait for user interaction
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
                        this.userPaused = false; // User clicked play, clear pause flag
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
            this.userPaused = true; // User manually paused, set flag
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
                    // Do not restore playback position; always start from beginning
                    this.savedTime = 0;
                    this.volume = state.volume || CONFIG.defaultVolume;
                    this.userPaused = state.userPaused || false; // Record whether user manually paused
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
                    userPaused: this.userPaused, // Save user pause state
                    timestamp: Date.now()
                };
                localStorage.setItem(this.storageKey, JSON.stringify(state));
            } catch (error) {
                // Fail silently without affecting playback
            }
        }
        
        // Public method: destroy player
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
    // Initialization
    // ========================================
    let player = null;
    
    // Read playlist name from the body tag's data-playlist attribute
    const getPlaylistName = () => {
        const bodyElement = document.body;
        return bodyElement.getAttribute('data-playlist') || 'playlist';
    };
    
    // Initialize after DOM is ready
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
    
    // Expose globally (optional, for debugging)
    window.MusicPlayer = {
        getInstance: () => player,
        destroy: () => player && player.destroy()
    };
    
})();
