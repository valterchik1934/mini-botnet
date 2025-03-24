```
const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');

const app = express();
const upload = multer({ dest: 'uploads/' });

let users = {}; // Хранение пользователей: {id: данные}
let files = {}; // Хранение файлов: {id: файл}

// Регистрация
app.post('/register', (req, res) => {
    const userId = Object.keys(users).length + 1;
    users[userId] = { id: userId };
    res.json({ id: userId });
});

// Отправка файла
app.post('/send_file', upload.single('file'), (req, res) => {
    const senderId = req.body.sender_id;
    const receiverId = req.body.receiver_id;
    const file = req.file;

    if (!senderId || !receiverId || !file) {
        return res.status(400).json({ error: 'Invalid request' });
    }

    files[receiverId] = file;
    res.json({ message: 'File sent successfully' });
});

// Получение файла
app.get('/get_file/:userId', (req, res) => {
    const userId = req.params.userId;
    const file = files[userId];

    if (!file) {
        return res.status(404).json({ error: 'File not found' });
    }

    res.download(file.path, file.originalname);
});

// Модерация (только для пользователя с ID 1)
app.post('/moderate', (req, res) => {
    const moderatorId = req.body.moderator_id;

    if (moderatorId !== 1) {
        return res.status(403).json({ error: 'Access denied' });
    }

    // Логика модерации
    res.json({ message: 'Moderation successful' });
});

app.listen(3000, () => console.log('Server running on http://localhost:3000'));