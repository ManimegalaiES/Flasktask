document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.querySelector(
        'form[data-validate="register"]'
    );

    if (!registerForm) {
        return;
    }

    registerForm.addEventListener("submit", function (event) {
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById(
            "confirm_password"
        ).value;

        const errorElement = document.getElementById("form-error");

        errorElement.textContent = "";

        if (password.length < 8) {
            event.preventDefault();
            errorElement.textContent =
                "Password must contain at least 8 characters.";
            return;
        }

        if (password !== confirmPassword) {
            event.preventDefault();
            errorElement.textContent =
                "Passwords do not match. Please try again.";
        }
    });
});
