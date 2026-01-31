
const express = require('express');
const app = express();
const router = express.Router();

// @desc Get all users
router.get('/users', (req, res) => {
    res.send('users');
});

// @desc Create user
app.post('/users', (req, res) => {
    res.send('created');
});
