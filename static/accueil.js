// DOM Elements
const signInBtn = document.getElementById('signInBtn');
const aiAssistantBtn = document.getElementById('aiAssistantBtn');

// Sign In Button Handler
if (signInBtn) {
    signInBtn.addEventListener('click', function() {
        window.location.href = 'signin.html';
    });
}

// REMOVED Sign Up Button Handler

// AI Assistant Handler
if (aiAssistantBtn) {
    aiAssistantBtn.addEventListener('click', function() {
        // Only allow chat if logged in, or redirect to login?
        // For now, let's redirect to login if they try to use AI without auth
        window.location.href = '/templates/signin.html'; 
    });
}