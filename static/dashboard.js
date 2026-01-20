// DOM Elements
const universityLogo = document.getElementById('universityLogo');
const profilePhoto = document.getElementById('profilePhoto');

// Dashboard Buttons
const coursBtn = document.getElementById('coursBtn');
const assistantBtn = document.getElementById('assistantBtn');
const quizBtn = document.getElementById('quizBtn');
const studyPlannerBtn = document.getElementById('studyPlannerBtn');
const summarizeBtn = document.getElementById('summarizeBtn');
const documentsBtn = document.getElementById('documentsBtn');
const notesBtn = document.getElementById('notesBtn');
const presenceBtn = document.getElementById('presenceBtn');

// Placeholder images
const defaultLogoPath = 'https://via.placeholder.com/200x60/1e3c72/ffffff?text=UNIVERSITY+LOGO';
const defaultProfilePath = 'https://via.placeholder.com/50x50/1e3c72/ffffff?text=U';

// Check if images exist
if (universityLogo) {
    universityLogo.onerror = function() {
        this.src = defaultLogoPath;
        this.onerror = null;
    };
}

if (profilePhoto) {
    profilePhoto.onerror = function() {
        this.src = defaultProfilePath;
        this.onerror = null;
    };
}

// --- FIX: REMOVED "/templates/" FROM ALL LINKS ---
// Flask routes are just "/page.html", not "/templates/page.html"

if(coursBtn) {
    coursBtn.addEventListener('click', function() {
        window.location.href = 'cours.html';
    });
}

if(assistantBtn) {
    assistantBtn.addEventListener('click', function() {
        window.location.href = 'assistant.html'; // <--- THIS CONNECTS TO APP.PY
    });
}

if(quizBtn) {
    quizBtn.addEventListener('click', function() {
        window.location.href = 'quiz.html';
    });
}

if(studyPlannerBtn) {
    studyPlannerBtn.addEventListener('click', function() {
        window.location.href = 'study-planner.html';
    });
}

if(summarizeBtn) {
    summarizeBtn.addEventListener('click', function() {
        window.location.href = 'summarize.html';
    });
}

if(documentsBtn) {
    documentsBtn.addEventListener('click', function() {
        window.location.href = 'documents.html';
    });
}

if(notesBtn) {
    notesBtn.addEventListener('click', function() {
        window.location.href = 'notes.html';
    });
}

if(presenceBtn) {
    presenceBtn.addEventListener('click', function() {
        window.location.href = 'presence.html';
    });
}

// AI Assistant Bubble Button
const aiAssistantBtn = document.getElementById('aiAssistantBtn');
if (aiAssistantBtn) {
    aiAssistantBtn.addEventListener('click', function() {
        window.location.href = 'assistant.html'; // <--- THIS CONNECTS TO APP.PY
    });

    // Add hover effect
    aiAssistantBtn.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.15) rotate(5deg)';
    });

    aiAssistantBtn.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1) rotate(0deg)';
    });
}

// Add smooth transitions
document.documentElement.style.scrollBehavior = 'smooth';

// Add loading animation
window.addEventListener('load', function() {
    document.body.style.opacity = '0';
    setTimeout(function() {
        document.body.style.transition = 'opacity 0.5s ease-in';
        document.body.style.opacity = '1';
    }, 100);
});

// Add card animation on load
window.addEventListener('load', function() {
    const cards = document.querySelectorAll('.dashboard-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});