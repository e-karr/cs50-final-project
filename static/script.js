const newPassword = document.querySelector("#new-password");
const confirmPassword = document.querySelector("#confirm-password");
const errorMessage = document.querySelector(".error-msg");

confirmPassword.addEventListener('blur', () => {
    if (newPassword.value !== confirmPassword.value) {
        newPassword.classList.add('invalid');
        confirmPassword.classList.add('invalid');
        errorMessage.classList.add('no-match');
    } else {
        newPassword.classList.remove('invalid');
        confirmPassword.classList.remove('invalid');
        errorMessage.classList.remove('no-match');
    }
});