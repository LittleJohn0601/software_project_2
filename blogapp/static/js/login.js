// ===== State Management =====
const state = {
    mouseX: 0,
    mouseY: 0,
    isTyping: false,
    isLookingAtEachOther: false,
    showPassword: false,
    password: '',
    isPurplePeeking: false,
    purpleBlinkTimeout: null,
    blackBlinkTimeout: null,
    peekTimeout: null,
    lookTimeout: null
};

// ===== DOM Elements =====
const elements = {
    // Characters
    purpleChar: document.getElementById('purpleChar'),
    blackChar: document.getElementById('blackChar'),
    orangeChar: document.getElementById('orangeChar'),
    yellowChar: document.getElementById('yellowChar'),
    
    // Eyes
    purpleEyes: document.getElementById('purpleEyes'),
    blackEyes: document.getElementById('blackEyes'),
    orangeEyes: document.getElementById('orangeEyes'),
    yellowEyes: document.getElementById('yellowEyes'),
    
    // Eyeballs
    purpleEye1: document.getElementById('purpleEye1'),
    purpleEye2: document.getElementById('purpleEye2'),
    blackEye1: document.getElementById('blackEye1'),
    blackEye2: document.getElementById('blackEye2'),
    
    // Pupils
    purplePupil1: document.getElementById('purplePupil1'),
    purplePupil2: document.getElementById('purplePupil2'),
    blackPupil1: document.getElementById('blackPupil1'),
    blackPupil2: document.getElementById('blackPupil2'),
    orangePupil1: document.getElementById('orangePupil1'),
    orangePupil2: document.getElementById('orangePupil2'),
    yellowPupil1: document.getElementById('yellowPupil1'),
    yellowPupil2: document.getElementById('yellowPupil2'),
    
    // Mouth
    yellowMouth: document.getElementById('yellowMouth'),
    
    // Form elements - Updated for Flask
    usernameInput: document.getElementById('username'),
    passwordInput: document.getElementById('password'),
    togglePassword: document.getElementById('togglePassword'),
    iconEye: document.getElementById('iconEye'),
    iconEyeOff: document.getElementById('iconEyeOff'),
    loginForm: document.getElementById('loginForm'),
    loginBtn: document.getElementById('loginBtn'),
    errorMessage: document.getElementById('errorMessage')
};

// ===== Mouse Tracking =====
document.addEventListener('mousemove', (e) => {
    state.mouseX = e.clientX;
    state.mouseY = e.clientY;
    updateCharacters();
});

// ===== Calculate Position Helper =====
function calculatePosition(element) {
    if (!element) return { faceX: 0, faceY: 0, bodySkew: 0 };
    
    const rect = element.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 3;
    
    const deltaX = state.mouseX - centerX;
    const deltaY = state.mouseY - centerY;
    
    // Face movement (limited range)
    const faceX = Math.max(-15, Math.min(15, deltaX / 20));
    const faceY = Math.max(-10, Math.min(10, deltaY / 30));
    
    // Body lean (skew)
    const bodySkew = Math.max(-6, Math.min(6, -deltaX / 120));
    
    return { faceX, faceY, bodySkew };
}

// ===== Calculate Pupil Position =====
function calculatePupilPosition(pupilElement, maxDistance, forceLookX, forceLookY) {
    if (!pupilElement) return { x: 0, y: 0 };
    
    // If forced look direction is provided
    if (forceLookX !== undefined && forceLookY !== undefined) {
        return { x: forceLookX, y: forceLookY };
    }
    
    const rect = pupilElement.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    const deltaX = state.mouseX - centerX;
    const deltaY = state.mouseY - centerY;
    const distance = Math.min(Math.sqrt(deltaX ** 2 + deltaY ** 2), maxDistance);
    
    const angle = Math.atan2(deltaY, deltaX);
    const x = Math.cos(angle) * distance;
    const y = Math.sin(angle) * distance;
    
    return { x, y };
}

// ===== Update Characters =====
function updateCharacters() {
    const hasPassword = state.password.length > 0;
    const passwordVisible = state.showPassword && hasPassword;
    const passwordHidden = !state.showPassword && hasPassword;
    
    // Calculate positions
    const purplePos = calculatePosition(elements.purpleChar);
    const blackPos = calculatePosition(elements.blackChar);
    const orangePos = calculatePosition(elements.orangeChar);
    const yellowPos = calculatePosition(elements.yellowChar);
    
    // Update Purple Character
    if (passwordVisible) {
        elements.purpleChar.style.transform = 'skewX(0deg)';
    } else if (state.isTyping || passwordHidden) {
        elements.purpleChar.style.transform = `skewX(${purplePos.bodySkew - 12}deg) translateX(40px)`;
        elements.purpleChar.classList.add('typing');
    } else {
        elements.purpleChar.style.transform = `skewX(${purplePos.bodySkew}deg)`;
        elements.purpleChar.classList.remove('typing');
    }
    
    // Update Black Character
    if (passwordVisible) {
        elements.blackChar.style.transform = 'skewX(0deg)';
    } else if (state.isLookingAtEachOther) {
        elements.blackChar.style.transform = `skewX(${blackPos.bodySkew * 1.5 + 10}deg) translateX(20px)`;
    } else if (state.isTyping || passwordHidden) {
        elements.blackChar.style.transform = `skewX(${blackPos.bodySkew * 1.5}deg)`;
    } else {
        elements.blackChar.style.transform = `skewX(${blackPos.bodySkew}deg)`;
    }
    
    // Update Orange Character
    elements.orangeChar.style.transform = passwordVisible ? 'skewX(0deg)' : `skewX(${orangePos.bodySkew}deg)`;
    
    // Update Yellow Character
    elements.yellowChar.style.transform = passwordVisible ? 'skewX(0deg)' : `skewX(${yellowPos.bodySkew}deg)`;
    
    // Update Eyes Positions
    updateEyesPositions(purplePos, blackPos, orangePos, yellowPos, passwordVisible);
    
    // Update Pupils
    updatePupils(passwordVisible);
}

// ===== Update Eyes Positions =====
function updateEyesPositions(purplePos, blackPos, orangePos, yellowPos, passwordVisible) {
    // Purple Eyes
    if (passwordVisible) {
        elements.purpleEyes.style.left = '20px';
        elements.purpleEyes.style.top = '35px';
    } else if (state.isLookingAtEachOther) {
        elements.purpleEyes.style.left = '55px';
        elements.purpleEyes.style.top = '65px';
    } else {
        elements.purpleEyes.style.left = `${45 + purplePos.faceX}px`;
        elements.purpleEyes.style.top = `${40 + purplePos.faceY}px`;
    }
    
    // Black Eyes
    if (passwordVisible) {
        elements.blackEyes.style.left = '10px';
        elements.blackEyes.style.top = '28px';
    } else if (state.isLookingAtEachOther) {
        elements.blackEyes.style.left = '32px';
        elements.blackEyes.style.top = '12px';
    } else {
        elements.blackEyes.style.left = `${26 + blackPos.faceX}px`;
        elements.blackEyes.style.top = `${32 + blackPos.faceY}px`;
    }
    
    // Orange Eyes
    if (passwordVisible) {
        elements.orangeEyes.style.left = '50px';
        elements.orangeEyes.style.top = '85px';
    } else {
        elements.orangeEyes.style.left = `${82 + orangePos.faceX}px`;
        elements.orangeEyes.style.top = `${90 + orangePos.faceY}px`;
    }
    
    // Yellow Eyes
    if (passwordVisible) {
        elements.yellowEyes.style.left = '20px';
        elements.yellowEyes.style.top = '35px';
    } else {
        elements.yellowEyes.style.left = `${52 + yellowPos.faceX}px`;
        elements.yellowEyes.style.top = `${40 + yellowPos.faceY}px`;
    }
    
    // Yellow Mouth
    if (passwordVisible) {
        elements.yellowMouth.style.left = '10px';
        elements.yellowMouth.style.top = '88px';
    } else {
        elements.yellowMouth.style.left = `${40 + yellowPos.faceX}px`;
        elements.yellowMouth.style.top = `${88 + yellowPos.faceY}px`;
    }
}

// ===== Update Pupils =====
function updatePupils(passwordVisible) {
    const hasPassword = state.password.length > 0;
    
    // Purple pupils
    let purpleForceLookX, purpleForceLookY;
    if (passwordVisible) {
        purpleForceLookX = state.isPurplePeeking ? 4 : -4;
        purpleForceLookY = state.isPurplePeeking ? 5 : -4;
    } else if (state.isLookingAtEachOther) {
        purpleForceLookX = 3;
        purpleForceLookY = 4;
    }
    
    const purplePos1 = calculatePupilPosition(elements.purplePupil1, 5, purpleForceLookX, purpleForceLookY);
    const purplePos2 = calculatePupilPosition(elements.purplePupil2, 5, purpleForceLookX, purpleForceLookY);
    elements.purplePupil1.style.transform = `translate(${purplePos1.x}px, ${purplePos1.y}px)`;
    elements.purplePupil2.style.transform = `translate(${purplePos2.x}px, ${purplePos2.y}px)`;
    
    // Black pupils
    let blackForceLookX, blackForceLookY;
    if (passwordVisible) {
        blackForceLookX = -4;
        blackForceLookY = -4;
    } else if (state.isLookingAtEachOther) {
        blackForceLookX = 0;
        blackForceLookY = -4;
    }
    
    const blackPos1 = calculatePupilPosition(elements.blackPupil1, 4, blackForceLookX, blackForceLookY);
    const blackPos2 = calculatePupilPosition(elements.blackPupil2, 4, blackForceLookX, blackForceLookY);
    elements.blackPupil1.style.transform = `translate(${blackPos1.x}px, ${blackPos1.y}px)`;
    elements.blackPupil2.style.transform = `translate(${blackPos2.x}px, ${blackPos2.y}px)`;
    
    // Orange pupils (simple)
    let orangeForceLookX, orangeForceLookY;
    if (passwordVisible) {
        orangeForceLookX = -5;
        orangeForceLookY = -4;
    }
    
    const orangePos1 = calculatePupilPosition(elements.orangePupil1, 5, orangeForceLookX, orangeForceLookY);
    const orangePos2 = calculatePupilPosition(elements.orangePupil2, 5, orangeForceLookX, orangeForceLookY);
    elements.orangePupil1.style.transform = `translate(${orangePos1.x}px, ${orangePos1.y}px)`;
    elements.orangePupil2.style.transform = `translate(${orangePos2.x}px, ${orangePos2.y}px)`;
    
    // Yellow pupils (simple)
    let yellowForceLookX, yellowForceLookY;
    if (passwordVisible) {
        yellowForceLookX = -5;
        yellowForceLookY = -4;
    }
    
    const yellowPos1 = calculatePupilPosition(elements.yellowPupil1, 5, yellowForceLookX, yellowForceLookY);
    const yellowPos2 = calculatePupilPosition(elements.yellowPupil2, 5, yellowForceLookX, yellowForceLookY);
    elements.yellowPupil1.style.transform = `translate(${yellowPos1.x}px, ${yellowPos1.y}px)`;
    elements.yellowPupil2.style.transform = `translate(${yellowPos2.x}px, ${yellowPos2.y}px)`;
}

// ===== Blinking Animation =====
function scheduleBlink(eyeElements, stateKey) {
    const getRandomInterval = () => Math.random() * 4000 + 3000; // 3-7 seconds
    
    const blink = () => {
        eyeElements.forEach(eye => eye.classList.add('blinking'));
        
        setTimeout(() => {
            eyeElements.forEach(eye => eye.classList.remove('blinking'));
            state[stateKey] = setTimeout(blink, getRandomInterval());
        }, 150); // Blink duration
    };
    
    state[stateKey] = setTimeout(blink, getRandomInterval());
}

// ===== Purple Peeking Animation =====
function schedulePeek() {
    if (state.password.length > 0 && state.showPassword) {
        const peekInterval = Math.random() * 3000 + 2000; // 2-5 seconds
        
        state.peekTimeout = setTimeout(() => {
            state.isPurplePeeking = true;
            updateCharacters();
            
            setTimeout(() => {
                state.isPurplePeeking = false;
                updateCharacters();
                schedulePeek(); // Schedule next peek
            }, 800); // Peek duration
        }, peekInterval);
    }
}

// ===== Form Event Handlers =====
// Note: Changed from emailInput to username input for Flask compatibility
const usernameInput = document.getElementById('username');

if (usernameInput) {
    usernameInput.addEventListener('focus', () => {
        state.isTyping = true;
        state.isLookingAtEachOther = true;
        updateCharacters();
        
        // Look at each other for 800ms, then back to mouse tracking
        clearTimeout(state.lookTimeout);
        state.lookTimeout = setTimeout(() => {
            state.isLookingAtEachOther = false;
            updateCharacters();
        }, 800);
    });

    usernameInput.addEventListener('blur', () => {
        state.isTyping = false;
        updateCharacters();
    });
}

elements.passwordInput.addEventListener('input', (e) => {
    state.password = e.target.value;
    
    // Clear existing peek timeout
    clearTimeout(state.peekTimeout);
    
    // Schedule peeking if password is visible
    if (state.password.length > 0 && state.showPassword) {
        schedulePeek();
    } else {
        state.isPurplePeeking = false;
    }
    
    updateCharacters();
});

elements.togglePassword.addEventListener('click', () => {
    state.showPassword = !state.showPassword;
    
    // Toggle password visibility
    elements.passwordInput.type = state.showPassword ? 'text' : 'password';
    
    // Toggle icons
    elements.iconEye.classList.toggle('d-none');
    elements.iconEyeOff.classList.toggle('d-none');
    
    // Clear existing peek timeout
    clearTimeout(state.peekTimeout);
    
    // Schedule peeking if password is visible
    if (state.password.length > 0 && state.showPassword) {
        schedulePeek();
    } else {
        state.isPurplePeeking = false;
    }
    
    updateCharacters();
});

// ===== Form Submission =====
// Using traditional form submission for Flask compatibility
// The form will submit to the action URL specified in the HTML
// Flask will handle the POST request and redirect accordingly

// Optional: Add loading state on form submit
if (elements.loginForm) {
    elements.loginForm.addEventListener('submit', (e) => {
        // Show loading state
        if (elements.loginBtn) {
            elements.loginBtn.disabled = true;
            elements.loginBtn.textContent = 'Signing in...';
        }
        
        // Let the form submit naturally to Flask backend
        // Flask will handle validation, authentication, and redirect
    });
}

// ===== Initialize =====
function init() {
    // Start blinking animations
    scheduleBlink([elements.purpleEye1, elements.purpleEye2], 'purpleBlinkTimeout');
    scheduleBlink([elements.blackEye1, elements.blackEye2], 'blackBlinkTimeout');
    
    // Initial update
    updateCharacters();
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
