// script.js

let currentQuestionIndex = 0;
let timerInterval;
let seconds = 900; // 15 minutes in seconds
let cameraStream = null; // Variable to hold the camera stream

const questions = [
    {
        question: "What is Python used for?",
        options: ["Web Development", "Data Science", "Game Development", "All of the Above"],
        correctAnswer: "All of the Above"
    },
    {
        question: "Which of these is a primitive data type in Java?",
        options: ["String", "int", "List", "Set"],
        correctAnswer: "int"
    },
    {
        question: "Who is the first President of the United States?",
        options: ["George Washington", "Abraham Lincoln", "Thomas Jefferson", "John Adams"],
        correctAnswer: "George Washington"
    }
];

function selectExam(examName) {
    document.getElementById("exam-list").classList.add("hidden");
    document.getElementById("exam-id-section").classList.remove("hidden");
    document.getElementById("exam-name").textContent = examName;
}

function startInstructions() {
    const examId = document.getElementById("exam-id").value;
    if (examId === "") {
        alert("Please enter a valid exam ID.");
        return;
    }

    // Request camera and microphone access during instructions
    requestMediaAccess().then(() => {
        // Camera access granted, show instructions
        document.getElementById("exam-id-section").classList.add("hidden");
        document.getElementById("instructions").classList.remove("hidden");
    }).catch((err) => {
        // Camera access denied or error occurred
        alert("Camera and microphone access is required to proceed. Error: " + err.message);
    });
}

function requestMediaAccess() {
    return new Promise((resolve, reject) => {
        navigator.mediaDevices.getUserMedia({ video: true, audio: true })
            .then(function (stream) {
                // Display the camera feed on instructions page
                const video = document.getElementById("video");
                video.srcObject = stream;

                // Store the stream globally for later use
                cameraStream = stream;
                resolve();
            })
            .catch(function (err) {
                reject(err);
            });
    });
}

function startExam() {
    document.getElementById("instructions").classList.add("hidden");
    document.getElementById("exam-page").classList.remove("hidden");

    // Display the camera feed on the exam page
    const video = document.getElementById("exam-video");
    video.srcObject = cameraStream;

    startTimer();
    showQuestion();
}

function startTimer() {
    timerInterval = setInterval(function () {
        if (seconds > 0) {
            seconds--;
            updateTimer();
        } else {
            clearInterval(timerInterval);
            alert("Time's up!");
        }
    }, 1000);
}

function updateTimer() {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    document.getElementById("timer").textContent = `${minutes < 10 ? '0' : ''}${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
}

function showQuestion() {
    const question = questions[currentQuestionIndex];
    const questionContainer = document.getElementById("exam-question");
    questionContainer.innerHTML = `
        <h4>${question.question}</h4>
        ${question.options.map((option, index) => `
            <label>
                <input type="radio" name="answer" value="${option}" /> ${option}
            </label>
        `).join('')}
    `;
}

function nextQuestion() {
    const selectedAnswer = document.querySelector('input[name="answer"]:checked');
    if (!selectedAnswer) {
        alert("Please select an answer.");
        return;
    }

    const answer = selectedAnswer.value;
    const correctAnswer = questions[currentQuestionIndex].correctAnswer;

    if (answer === correctAnswer) {
        alert("Correct!");
    } else {
        alert("Incorrect. The correct answer was: " + correctAnswer);
    }

    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
        showQuestion();
    } else {
        alert("You've completed the exam!");
        submitExam();
    }
}

function prevQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        showQuestion();
    }
}

function submitExam() {
    clearInterval(timerInterval);
    alert("Your exam has been submitted.");
    stopCamera();
    resetExamPage();
}

function stopCamera() {
    if (cameraStream) {
        const tracks = cameraStream.getTracks();
        tracks.forEach(track => track.stop()); // Stop each track (video and audio)
    }
}

function resetExamPage() {
    document.getElementById("exam-page").classList.add("hidden");
    document.getElementById("exam-list").classList.remove("hidden");
    currentQuestionIndex = 0;
    seconds = 900; // Reset timer
    document.getElementById("timer").textContent = "15:00";
}

function submitExam() {
    clearInterval(timerInterval);
    alert("Your exam has been submitted.");
    stopMediaStream(); // Stop camera and mic
    resetExamPage();
}

function stopMediaStream() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop()); // Stops all media tracks (video & audio)
        cameraStream = null; // Clear the stream reference
    }
}