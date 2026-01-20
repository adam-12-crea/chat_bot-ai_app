const signinForm = document.getElementById('signinForm');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');

if(signinForm) {
    signinForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const submitButton = signinForm.querySelector('.btn-signin');
        const originalText = submitButton.textContent;

        submitButton.textContent = 'Connexion...';
        submitButton.disabled = true;

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (data.success) {
                const successDiv = document.createElement('div');
                successDiv.className = 'success-message';
                successDiv.textContent = 'Connexion réussie !';
                successDiv.style.cssText = 'background: #efe; color: #3c3; padding: 10px; border-radius: 8px; margin-bottom: 10px; text-align: center;';
                
                const existing = signinForm.querySelector('.success-message, .error-message');
                if(existing) existing.remove();
                
                signinForm.insertBefore(successDiv, signinForm.firstChild);

                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 1000);
            } else {
                showError(data.error);
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        } catch (error) {
            showError("Erreur de connexion au serveur.");
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }
    });
}

function showError(message) {
    const existing = signinForm.querySelector('.error-message');
    if(existing) existing.remove();

    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.cssText = 'background: #fee; color: #c33; padding: 10px; border-radius: 8px; margin-bottom: 10px; text-align: center; border: 1px solid #fcc;';
    
    signinForm.insertBefore(errorDiv, signinForm.firstChild);
    setTimeout(() => errorDiv.remove(), 5000);
}