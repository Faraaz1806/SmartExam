// Global variables
let selectedExam = '';
let examId = '';
let studentId = '';
let examTimer;
let timeLeft = 45 * 60; // 45 minutes in seconds
let currentQuestion = 1;
let totalQuestions = 50;
let cameraStream = null;

// Show loading screen for a short time
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        document.getElementById('loading-screen').classList.add('hidden');
    }, 1500);
    
    // Set up event listeners
    setupEventListeners();
});

// Function to set up all event listeners
function setupEventListeners() {
    // Agreement checkbox
    const agreementCheckbox = document.getElementById('agreement-checkbox');
    const proceedBtn = document.getElementById('proceed-btn');
    
    agreementCheckbox.addEventListener('change', function() {
        proceedBtn.disabled = !this.checked;
    });
    
    // Close modal when clicking the X button
    const closeButtons = document.querySelectorAll('.close-btn');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modalId = this.closest('.modal').id;
            document.getElementById(modalId).style.display = 'none';
        });
    });
    
    // Close submit modal when clicking Cancel
    document.getElementById('cancel-submit').addEventListener('click', function() {
        document.getElementById('submit-modal').style.display = 'none';
    });
    
    // Handle final submission
    document.getElementById('confirm-submit').addEventListener('click', function() {
        finishExam();
    });
    
    // Add click handlers for question number buttons
    const questionButtons = document.querySelectorAll('.question-number-btn');
    questionButtons.forEach((btn, index) => {
        btn.addEventListener('click', function() {
            currentQuestion = index + 1;
            updateQuestionDisplay();
        });
    });
    
    // Handle marking questions for review
    document.getElementById('mark-btn').addEventListener('click', function() {
        const questionButtons = document.querySelectorAll('.question-number-btn');
        questionButtons[currentQuestion - 1].classList.toggle('marked');
        updateProgressStats();
    });
    
    // Navigation buttons
    document.getElementById('prev-btn').addEventListener('click', prevQuestion);
    document.getElementById('next-btn').addEventListener('click', nextQuestion);
    document.getElementById('submit-exam').addEventListener('click', submitExam);
    
    // Report issue button
    document.getElementById('report-issue').addEventListener('click', function() {
        document.getElementById('issue-modal').style.display = 'flex';
    });
    
    // Close issue modal
    document.getElementById('close-issue-modal').addEventListener('click', function() {
        document.getElementById('issue-modal').style.display = 'none';
    });
    
    document.getElementById('cancel-issue').addEventListener('click', function() {
        document.getElementById('issue-modal').style.display = 'none';
    });
    
    // Submit issue report
    document.getElementById('submit-issue').addEventListener('click', function() {
        const issueType = document.getElementById('issue-type').value;
        const issueDescription = document.getElementById('issue-description').value;
        
        if (!issueType || !issueDescription) {
            alert('Please fill in all fields');
            return;
        }
        
        alert('Your issue has been reported. An exam administrator will review it shortly.');
        document.getElementById('issue-modal').style.display = 'none';
        
        // Reset form
        document.getElementById('issue-type').value = '';
        document.getElementById('issue-description').value = '';
    });
    
    // Radio button change for options
    const optionInputs = document.querySelectorAll('.option input[type="radio"]');
    optionInputs.forEach(input => {
        input.addEventListener('change', function() {
            const questionButtons = document.querySelectorAll('.question-number-btn');
            questionButtons[currentQuestion - 1].classList.add('answered');
            updateProgressStats();
        });
    });
}

// Function to select an exam
function selectExam(examName) {
    selectedExam = examName;
    document.getElementById('exam-name').textContent = examName;
    document.getElementById('exam-list').classList.add('hidden');
    document.getElementById('exam-id-section').classList.remove('hidden');
    
    // Update exam title in the exam interface
    document.getElementById('exam-title').textContent = examName;
    
    // Set exam duration based on selection
    switch(examName) {
        case 'Python Programming':
            timeLeft = 60 * 60; // 60 minutes
            totalQuestions = 40;
            break;
        case 'Java Development':
            timeLeft = 75 * 60; // 75 minutes
            totalQuestions = 50;
            break;
        case 'General Knowledge':
            timeLeft = 45 * 60; // 45 minutes
            totalQuestions = 30;
            break;
        case 'Advanced Mathematics':
            timeLeft = 90 * 60; // 90 minutes
            totalQuestions = 50;
            break;
        default:
            timeLeft = 60 * 60; // Default 60 minutes
            totalQuestions = 40;
    }
    
    document.getElementById('total-questions').textContent = totalQuestions;
}

// Function to go back to exam list
function backToExamList() {
    document.getElementById('exam-id-section').classList.add('hidden');
    document.getElementById('exam-list').classList.remove('hidden');
}

// Function to go back to exam ID section
function backToExamId() {
    document.getElementById('instructions').classList.add('hidden');
    document.getElementById('exam-id-section').classList.remove('hidden');
    
    // Stop camera if it's running
    stopCamera();
}

// Function to start instructions
function startInstructions() {
    examId = document.getElementById('exam-id').value.trim();
    studentId = document.getElementById('student-id-input').value.trim();
    
    if (!examId) {
        alert('Please enter a valid Exam ID');
        return;
    }
    
    if (!studentId) {
        alert('Please enter your Student ID');
        return;
    }
    
    document.getElementById('exam-id-section').classList.add('hidden');
    document.getElementById('instructions').classList.remove('hidden');
    
    // Set the exam ID and student ID in the footer
    document.getElementById('display-exam-id').textContent = examId;
    document.getElementById('student-id').textContent = studentId;
}

// Function to request media access
function requestMediaAccess() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true, audio: true })
            .then(function(stream) {
                cameraStream = stream;
                
                const videoElement = document.getElementById('video');
                videoElement.srcObject = stream;
                
                // Update camera status
                document.getElementById('camera-status-text').textContent = 'Camera active';
                document.getElementById('camera-status-text').parentElement.classList.add('active');
                
                // If we're already in the exam, also set the exam video
                const examVideoElement = document.getElementById('exam-video');
                if (!document.getElementById('exam-interface').classList.contains('hidden')) {
                    examVideoElement.srcObject = stream;
                }
            })
            .catch(function(error) {
                console.error("Error accessing media devices:", error);
                alert("Failed to access camera and microphone. Please ensure they are connected and permissions are granted.");
            });
    } else {
        alert("Your browser doesn't support camera access. Please use a modern browser like Chrome, Firefox, or Edge.");
    }
}

// Function to stop camera
function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => {
            track.stop();
        });
        
        document.getElementById('camera-status-text').textContent = 'Camera not active';
        document.getElementById('camera-status-text').parentElement.classList.remove('active');
    }
}

// Function to start the exam
function startExam() {
    // Check if camera is active
    if (!cameraStream) {
        alert('Please enable your camera before proceeding');
        return;
    }
    
    // Check if agreement is checked
    if (!document.getElementById('agreement-checkbox').checked) {
        alert('Please agree to the exam rules before proceeding');
        return;
    }
    
    document.getElementById('selection-screen').classList.add('hidden');
    document.getElementById('exam-interface').classList.remove('hidden');
    
    // Start the timer
    startTimer();
    
    // Transfer the camera feed to the exam interface
    const examVideoElement = document.getElementById('exam-video');
    examVideoElement.srcObject = cameraStream;
    
    // Update question display
    updateQuestionDisplay();
    updateProgressStats();
}

// Function to start the timer
function startTimer() {
    updateTimerDisplay();
    
    examTimer = setInterval(function() {
        timeLeft--;
        
        if (timeLeft <= 0) {
            clearInterval(examTimer);
            submitExam();
        }
        
        updateTimerDisplay();
    }, 1000);
}

// Function to update timer display
function updateTimerDisplay() {
    const hours = Math.floor(timeLeft / 3600);
    const minutes = Math.floor((timeLeft % 3600) / 60);
    const seconds = timeLeft % 60;
    
    let timeString = '';
    
    if (hours > 0) {
        timeString = `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    } else {
        timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    document.getElementById('time-remaining').textContent = timeString;
    
    // Add warning class if less than 5 minutes remaining
    if (timeLeft < 300) {
        document.getElementById('time-remaining').classList.add('warning-time');
    }
}

// Function to navigate to previous question
function prevQuestion() {
    if (currentQuestion > 1) {
        currentQuestion--;
        updateQuestionDisplay();
    }
}

// Function to navigate to next question
function nextQuestion() {
    if (currentQuestion < totalQuestions) {
        currentQuestion++;
        updateQuestionDisplay();
    }
}

// Function to update question display
function updateQuestionDisplay() {
    document.getElementById('current-question').textContent = `Question ${currentQuestion}`;
    document.querySelector('.question-number').textContent = `Question ${currentQuestion}`;
    
    // Update the active question in the sidebar
    const questionButtons = document.querySelectorAll('.question-number-btn');
    questionButtons.forEach((btn, index) => {
        if (index + 1 === currentQuestion) {
            btn.classList.add('current');
        } else {
            btn.classList.remove('current');
        }
    });
    
    // Enable/disable previous button based on current question
    document.getElementById('prev-btn').disabled = (currentQuestion === 1);
    
    // For demo purposes, we're not actually changing the question content
    // In a real app, you would load the question data here
}

// Function to update progress statistics
function updateProgressStats() {
    const questionButtons = document.querySelectorAll('.question-number-btn');
    let answeredCount = 0;
    let markedCount = 0;
    
    questionButtons.forEach(btn => {
        if (btn.classList.contains('answered')) {
            answeredCount++;
        }
        if (btn.classList.contains('marked')) {
            markedCount++;
        }
    });
    
    // Update stats in the sidebar
    const statsElements = document.querySelectorAll('.stat-number');
    statsElements[0].textContent = `${answeredCount}/${totalQuestions}`;
    statsElements[1].textContent = `${markedCount}/${totalQuestions}`;
    
    // Update progress bar
    const progressPercentage = (answeredCount / totalQuestions) * 100;
    document.querySelector('.progress').style.width = `${progressPercentage}%`;
    
    // Update submission summary
    const summaryItems = document.querySelectorAll('.summary-item span:last-child');
    summaryItems[0].textContent = totalQuestions;
    summaryItems[1].textContent = answeredCount;
    summaryItems[2].textContent = markedCount;
    summaryItems[3].textContent = totalQuestions - answeredCount;
}

// Function to submit the exam
function submitExam() {
    updateProgressStats();
    document.getElementById('submit-modal').style.display = 'flex';
}

// Function to finish the exam
function finishExam() {
    // Stop the timer
    clearInterval(examTimer);
    
    // Stop the camera
    stopCamera();
    
    // Show completion message
    alert('Your exam has been submitted successfully!');
    
    // Redirect to a completion page (in a real app)
    // For demo purposes, we'll just reload the page
    window.location.reload();
}