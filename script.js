// Переключение между регистрацией и входом
const authSlider = document.getElementById("auth-slider");
const registerForm = document.getElementById("register-form");
const loginForm = document.getElementById("login-form");

authSlider.addEventListener("input", function() {
    if (authSlider.value == 0) {
        registerForm.style.display = "block";
        loginForm.style.display = "none";
    } else {
        registerForm.style.display = "none";
        loginForm.style.display = "block";
    }
});

// Проверка и регистрация
document.getElementById("register").addEventListener("submit", function(e) {
    e.preventDefault();

    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    const registerError = document.getElementById("register-error");

    if (password !== confirmPassword) {
        registerError.textContent = "Пароли не совпадают!";
        return;
    }

    // Проверка уникальности почты (в реальности это должна быть проверка на сервере)
    if (localStorage.getItem(email)) {
        registerError.textContent = "Такая почта уже используется!";
        return;
    }

    // Сохраняем данные в localStorage (в реальности это должна быть запись в базу данных)
    localStorage.setItem(email, password);
    alert("Вы успешно зарегистрированы!");
    registerError.textContent = "";  // Очищаем ошибку
    authSlider.value = 1;  // Переключаем на форму входа
});

// Вход
document.getElementById("login").addEventListener("submit", function(e) {
    e.preventDefault();

    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    const loginError = document.getElementById("login-error");

    // Проверка, существует ли такая почта
    const savedPassword = localStorage.getItem(email);

    if (!savedPassword) {
        loginError.textContent = "Почта не зарегистрирована!";
        return;
    }

    if (savedPassword !== password) {
        loginError.textContent = "Неверный пароль!";
        return;
    }

    alert("Вы успешно вошли!");
    loginError.textContent = "";  // Очищаем ошибку
});
