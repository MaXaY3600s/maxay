const express = require("express");
const sqlite3 = require("sqlite3").verbose();
const bcrypt = require("bcryptjs");

const app = express();
const db = new sqlite3.Database("./users.db");

app.use(express.json());

// Создание таблицы пользователей
db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT)");

// Регистрация пользователя
app.post("/register", (req, res) => {
  const { email, password } = req.body;

  // Проверка, существует ли уже такой пользователь
  db.get("SELECT * FROM users WHERE email = ?", [email], (err, row) => {
    if (err) return res.status(500).send("Server error");
    if (row) return res.status(400).send("Email уже зарегистрирован");

    // Хешируем пароль
    bcrypt.hash(password, 10, (err, hashedPassword) => {
      if (err) return res.status(500).send("Server error");

      // Сохраняем нового пользователя в базе данных
      db.run("INSERT INTO users (email, password) VALUES (?, ?)", [email, hashedPassword], function (err) {
        if (err) return res.status(500).send("Ошибка при регистрации");
        res.status(201).send("Регистрация прошла успешно");
      });
    });
  });
});

// Вход пользователя
app.post("/login", (req, res) => {
  const { email, password } = req.body;

  db.get("SELECT * FROM users WHERE email = ?", [email], (err, row) => {
    if (err) return res.status(500).send("Server error");
    if (!row) return res.status(400).send("Пользователь не найден");

    // Сравниваем введенный пароль с хешированным паролем в базе данных
    bcrypt.compare(password, row.password, (err, isMatch) => {
      if (err) return res.status(500).send("Server error");
      if (!isMatch) return res.status(400).send("Неверный пароль");
      res.status(200).send("Вход успешен");
    });
  });
});

// Запуск сервера
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Сервер запущен на порту ${PORT}`);
});



