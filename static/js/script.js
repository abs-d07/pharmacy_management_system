document.addEventListener('DOMContentLoaded', function () {
    const authContainer = document.getElementById('auth-container');
    const loginTab = document.getElementById('login-tab');
    const signupTab = document.getElementById('signup-tab');

    loginTab.addEventListener('click', function () {
        authContainer.style.transform = 'translateX(0)';
    });

    signupTab.addEventListener('click', function () {
        authContainer.style.transform = 'translateX(-50%)'; // Adjust to -50% for exact half-slide
    });
});
