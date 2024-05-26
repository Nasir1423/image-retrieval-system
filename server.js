// const express = require('express');
// const multer = require('multer');
// const path = require('path');
// const { spawn } = require('child_process');
// const app = express();
// const PORT = 3000;

// app.use(express.static('public'));
// app.set('view engine', 'ejs');
// app.set('views', path.join(__dirname, 'views'));

// const storage = multer.diskStorage({
//     destination: function (req, file, cb) {
//         cb(null, 'uploads/');
//     },
//     filename: function (req, file, cb) {
//         cb(null, Date.now() + path.extname(file.originalname));
//     }
// });

// const upload = multer({ storage: storage });

// app.get('/', (req, res) => {

//     res.render('index');
// });

// app.post('/searchResult', upload.single('image'), (req, res) => {
//     console.log("/searchResult")

//     const filePath = req.file.path;

//     const process = spawn('python', ['imageRetrieval.py', filePath]);

//     process.stdout.on('data', (data) => {
//         console.log("out success")
//         const results = JSON.parse(data.toString());
//         console.log(results);
//         res.render('searchResult', { results: results });
//     });

//     process.stderr.on('data', (data) => {
//         console.log("err");
//         console.error(`stderr: ${data}`);
//     });

//     process.on('close', (code) => {
//         console.log("close");
//         console.log(`child process exited with code ${code}`);
//     });
// });

// app.listen(PORT, () => {
//     console.log(`Server is running on http://localhost:${PORT}`);
// });

const express = require('express');
const multer = require('multer');
const path = require('path');
const { spawn } = require('child_process');
const app = express();
const PORT = 3000;

app.use(express.static('public'));
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/');
    },
    filename: function (req, file, cb) {
        cb(null, Date.now() + path.extname(file.originalname));
    }
});

const upload = multer({ storage: storage });

app.get('/', (req, res) => {
    console.log("/");
    res.render('index');
});

app.post('/searchResult', upload.single('image'), (req, res) => {
    console.log("/searchResult");

    const filePath = req.file.path;

    const process = spawn('python', ['imageRetrieval.py', filePath]);

    process.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
        const results = JSON.parse(data.toString());
        res.json({ results });  // 返回 JSON 格式结果
    });

    process.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    process.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });
});

app.get('/searchResult', (req, res) => {
    console.log("/searchResult-get");

    res.render('searchResult');  // 渲染 searchResult 页面
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
