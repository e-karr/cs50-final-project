const newPassword = document.querySelector("#new-password");
const confirmPassword = document.querySelector("#confirm-password");
const errorMessage = document.querySelector(".error-msg");

const firstName = document.querySelector("#first-name");
const lastName = document.querySelector("#last-name");
const phoneNumber = document.querySelector("#phone-number");
const email = document.querySelector("#email");

// firstName.addEventListener('blur', addInvalidBorder(firstName));

firstName.addEventListener('invalid', () => {
    firstName.setCustomValidity('Please enter your first name.');
});

lastName.addEventListener('invalid', () => {
    lastName.setCustomValidity('Please enter your last name.');
});

phoneNumber.addEventListener('invalid', () => {
    phoneNumber.setCustomValidity('Please enter a valid phone number.');
});

email.addEventListener('invalid', () => {
    email.setCustomValidity('Please enter a valid email.');
});

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

// function addInvalidBorder(element) {
//     element.classList.add('invalid');
// }