// Variables globales
let imageBlob = null;
let audioBlob = null;
let authenticated = false;
let user = null;

// Vérifier l'état d'authentification
if (localStorage.getItem('authenticated') === 'true') {
    authenticated = true;
    user = localStorage.getItem('user');
    if (user) {
        showWelcomeMessage(user);
        showLogoutButton();
    } else {
        // Si l'utilisateur est authentifié mais le nom est manquant, réinitialiser l'authentification
        localStorage.removeItem('authenticated');
        localStorage.removeItem('user');
        authenticated = false;
    }
}

// Étape 1 : Capture d'image depuis la caméra
const video = document.getElementById('video');
const captureButton = document.getElementById('capture');
const step1 = document.getElementById('step1');
const step2 = document.getElementById('step2');
const authenticateButton = document.getElementById('authenticate');
const logoutButton = document.getElementById('logout');

// Accéder à la caméra
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(error => {
        console.error('Erreur d\'accès à la caméra:', error);
    });

// Capturer l'image
captureButton.addEventListener('click', () => {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(blob => {
        imageBlob = blob;
        step1.classList.remove('active');
        step2.classList.add('active');
    });
});

// Étape 2 : Enregistrement audio
const startRecordingButton = document.getElementById('startRecording');
const stopRecordingButton = document.getElementById('stopRecording');
const audioPlayback = document.getElementById('audioPlayback');
let mediaRecorder;
let audioChunks = [];

startRecordingButton.addEventListener('click', () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();
            audioChunks = [];

            mediaRecorder.addEventListener('dataavailable', event => {
                audioChunks.push(event.data);
            });

            mediaRecorder.addEventListener('stop', () => {
                audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioPlayback.src = URL.createObjectURL(audioBlob);
                audioPlayback.style.display = 'block';
                authenticateButton.classList.add('active');
            });

            startRecordingButton.style.display = 'none';
            stopRecordingButton.style.display = 'inline';
        })
        .catch(error => {
            console.error('Erreur d\'accès au micro:', error);
        });
});

stopRecordingButton.addEventListener('click', () => {
    mediaRecorder.stop();
    stopRecordingButton.style.display = 'none';
});

// Authentifier l'utilisateur
authenticateButton.addEventListener('click', () => {
    const formData = new FormData();
    formData.append('image', imageBlob, 'image.png');
    formData.append('audio', audioBlob, 'audio.wav');

    fetch('http://127.0.0.1:5000/authenticate', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showResult(`Erreur : ${data.error}`);
        } else {
            if (data.authorized) {
                localStorage.setItem('authenticated', 'true');
                localStorage.setItem('user', data.user);
                authenticated = true;
                user = data.user;
                showWelcomeMessage(user);
                showLogoutButton();
                hideAuthenticateButton();
            } else {
                showResult('Authentification échouée.',data.user);
            }
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showResult('Erreur lors de l\'authentification.');
    });
});

// Déconnexion
logoutButton.addEventListener('click', () => {
    localStorage.removeItem('authenticated');
    localStorage.removeItem('user');
    authenticated = false;
    window.location.reload();
});

// Afficher le message de bienvenue
function showWelcomeMessage(user) {
    document.getElementById('welcome-message').textContent = `Bienvenue, ${user}`;
}

// Afficher le bouton de déconnexion
function showLogoutButton() {
    logoutButton.classList.add('active');
}

// Cacher le bouton d'authentification
function hideAuthenticateButton() {
    authenticateButton.classList.remove('active');
}

// Afficher le résultat
function showResult(message) {
    document.getElementById('result').textContent = message;
}

// Initialiser l'étape 1 si l'utilisateur n'est pas authentifié
if (!authenticated) {
    step1.classList.add('active');
}
