const signupForm = document.getElementById('signupForm');
const fullNameInput = document.getElementById('fullName');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const userTypeSelect = document.getElementById('userType');

if(signupForm) {
    signupForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const submitButton = signupForm.querySelector('.btn-signin');
        const originalText = submitButton.textContent;

        submitButton.textContent = 'Création...';
        submitButton.disabled = true;

        try {
            const response = await fetch('/api/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    fullName: fullNameInput.value,
                    email: emailInput.value,
                    password: passwordInput.value,
                    userType: userTypeSelect.value
                })
            });

            const data = await response.json();

            if (data.success) {
                const successDiv = document.createElement('div');
                successDiv.className = 'success-message';
                successDiv.textContent = 'Compte créé ! Redirection...';
                successDiv.style.cssText = 'background: #efe; color: #3c3; padding: 10px; border-radius: 8px; margin-bottom: 10px; text-align: center;';
                
                const existing = signupForm.querySelector('.success-message, .error-message');
                if(existing) existing.remove();
                
                signupForm.insertBefore(successDiv, signupForm.firstChild);

                setTimeout(() => {
                    window.location.href = 'signin.html';
                }, 1500);
            } else {
                showError(data.error);
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        } catch (error) {
            showError("Erreur serveur.");
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }
    });
}

function showError(message) {
    const existing = signupForm.querySelector('.error-message');
    if(existing) existing.remove();

    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.cssText = 'background: #fee; color: #c33; padding: 10px; border-radius: 8px; margin-bottom: 10px; text-align: center; border: 1px solid #fcc;';
    
    signupForm.insertBefore(errorDiv, signupForm.firstChild);
    setTimeout(() => errorDiv.remove(), 5000);
}