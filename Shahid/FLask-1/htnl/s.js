// Global variables
let selectedExam = ""
let examTimer
let timeRemaining = 0
let mediaStream = null
let currentQuestion = 1
let totalQuestions = 50
const answeredQuestions = []
const markedQuestions = []

// DOM Elements
const selectionScreen = document.getElementById("selection-screen")
const examList = document.getElementById("exam-list")
const examIdSection = document.getElementById("exam-id-section")
const examNameElement = document.getElementById("exam-name")
const instructionsSection = document.getElementById("instructions")
const examInterface = document.getElementById("exam-interface")
const agreementCheckbox = document.getElementById("agreement-checkbox")
const proceedBtn = document.getElementById("proceed-btn")
const cameraStatusText = document.getElementById("camera-status-text")
const video = document.getElementById("video")
const examVideo = document.getElementById("exam-video")
const timeRemainingElement = document.getElementById("time-remaining")
const examTitle = document.getElementById("exam-title")
const currentQuestionElement = document.getElementById("current-question")
const totalQuestionsElement = document.getElementById("total-questions")
const studentIdElement = document.getElementById("student-id")
const displayExamIdElement = document.getElementById("display-exam-id")
const submitModal = document.getElementById("submit-modal")
const issueModal = document.getElementById("issue-modal")
const prevBtn = document.getElementById("prev-btn")
const nextBtn = document.getElementById("next-btn")
const markBtn = document.getElementById("mark-btn")
const submitExamBtn = document.getElementById("submit-exam")
const reportIssueBtn = document.getElementById("report-issue")
const cancelSubmitBtn = document.getElementById("cancel-submit")
const confirmSubmitBtn = document.getElementById("confirm-submit")
const closeSubmitModalBtn = document.querySelector("#submit-modal .close-btn")
const closeIssueModalBtn = document.getElementById("close-issue-modal")
const cancelIssueBtn = document.getElementById("cancel-issue")
const submitIssueBtn = document.getElementById("submit-issue")

// Exam data (would normally come from a server)
const examData = {
  "Python Programming": {
    duration: 60, // minutes
    questions: 40,
    examId: "PYTHON-2023-A",
  },
  "Java Development": {
    duration: 75,
    questions: 50,
    examId: "JAVA-2023-A",
  },
  "General Knowledge": {
    duration: 45,
    questions: 30,
    examId: "GK-2023-A",
  },
  "Advanced Mathematics": {
    duration: 90,
    questions: 50,
    examId: "MATH-2023-A",
  },
}

// Event Listeners
window.addEventListener("DOMContentLoaded", () => {
  // Set up event listeners
  agreementCheckbox.addEventListener("change", toggleProceedButton)
  submitExamBtn.addEventListener("click", showSubmitModal)
  reportIssueBtn.addEventListener("click", showIssueModal)
  cancelSubmitBtn.addEventListener("click", hideSubmitModal)
  closeSubmitModalBtn.addEventListener("click", hideSubmitModal)
  confirmSubmitBtn.addEventListener("click", submitExam)
  closeIssueModalBtn.addEventListener("click", hideIssueModal)
  cancelIssueBtn.addEventListener("click", hideIssueModal)
  submitIssueBtn.addEventListener("click", submitIssueReport)
  prevBtn.addEventListener("click", goToPreviousQuestion)
  nextBtn.addEventListener("click", goToNextQuestion)
  markBtn.addEventListener("click", toggleMarkQuestion)

  // Set up question grid buttons
  const questionButtons = document.querySelectorAll(".question-number-btn")
  questionButtons.forEach((button) => {
    button.addEventListener("click", () => {
      navigateToQuestion(Number.parseInt(button.textContent))
    })
  })
})

// Functions for exam selection and navigation
function selectExam(examName) {
  selectedExam = examName
  examNameElement.textContent = examName
  examList.classList.add("hidden")
  examIdSection.classList.remove("hidden")
}

function backToExamList() {
  examIdSection.classList.add("hidden")
  examList.classList.remove("hidden")
  selectedExam = ""
}

function startInstructions() {
  const examIdInput = document.getElementById("exam-id").value
  const studentIdInput = document.getElementById("student-id-input").value

  if (!examIdInput || !studentIdInput) {
    alert("Please enter both Exam ID and Student ID to continue.")
    return
  }

  examIdSection.classList.add("hidden")
  instructionsSection.classList.remove("hidden")
}

function backToExamId() {
  instructionsSection.classList.add("hidden")
  examIdSection.classList.remove("hidden")

  // Stop camera if it was started
  stopMediaStream()
}

function toggleProceedButton() {
  proceedBtn.disabled = !agreementCheckbox.checked
}

// Camera and microphone access
async function requestMediaAccess() {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true,
    })

    video.srcObject = mediaStream
    cameraStatusText.textContent = "Camera active"
    cameraStatusText.parentElement.classList.add("active")
  } catch (error) {
    console.error("Error accessing media devices:", error)
    cameraStatusText.textContent = "Failed to access camera"
    alert("Failed to access camera and microphone. Please ensure they are connected and permissions are granted.")
  }
}

function stopMediaStream() {
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop())
    mediaStream = null
    video.srcObject = null
    cameraStatusText.textContent = "Camera not active"
    cameraStatusText.parentElement.classList.remove("active")
  }
}

// Start the exam
function startExam() {
  if (!agreementCheckbox.checked) {
    alert("You must agree to the exam rules to proceed.")
    return
  }

  // Get exam details
  const examDetails = examData[selectedExam]
  if (!examDetails) {
    alert("Invalid exam selection.")
    return
  }

  // Set up exam interface
  examTitle.textContent = selectedExam
  totalQuestions = examDetails.questions
  totalQuestionsElement.textContent = totalQuestions
  currentQuestionElement.textContent = `Question ${currentQuestion}`

  // Set student ID and exam ID in the footer
  const studentIdInput = document.getElementById("student-id-input").value
  const examIdInput = document.getElementById("exam-id").value
  studentIdElement.textContent = studentIdInput
  displayExamIdElement.textContent = examIdInput

  // Set up timer
  timeRemaining = examDetails.duration * 60 // convert to seconds
  updateTimer()
  examTimer = setInterval(updateTimer, 1000)

  // Transfer camera feed to exam interface
  if (mediaStream) {
    examVideo.srcObject = mediaStream
  }

  // Hide selection screen and show exam interface
  selectionScreen.classList.add("hidden")
  examInterface.classList.remove("hidden")
}

// Timer functions
function updateTimer() {
  if (timeRemaining <= 0) {
    clearInterval(examTimer)
    submitExam()
    return
  }

  timeRemaining--

  const minutes = Math.floor(timeRemaining / 60)
  const seconds = timeRemaining % 60

  timeRemainingElement.textContent = `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`

  // Add warning class when time is running low (less than 5 minutes)
  if (timeRemaining < 300) {
    timeRemainingElement.classList.add("warning")
  }
}

// Question navigation
function goToPreviousQuestion() {
  if (currentQuestion > 1) {
    navigateToQuestion(currentQuestion - 1)
  }
}

function goToNextQuestion() {
  if (currentQuestion < totalQuestions) {
    navigateToQuestion(currentQuestion + 1)
  }
}

function navigateToQuestion(questionNumber) {
  // Save current question state (would normally save answers too)

  // Update current question
  currentQuestion = questionNumber
  currentQuestionElement.textContent = `Question ${currentQuestion}`

  // Update navigation buttons
  prevBtn.disabled = currentQuestion === 1
  nextBtn.disabled = currentQuestion === totalQuestions

  // Update question display (would normally load question content)

  // Update question number buttons
  const questionButtons = document.querySelectorAll(".question-number-btn")
  questionButtons.forEach((button) => {
    button.classList.remove("current")
    if (Number.parseInt(button.textContent) === currentQuestion) {
      button.classList.add("current")
    }
  })

  // Update mark button state
  if (markedQuestions.includes(currentQuestion)) {
    markBtn.innerHTML = '<i class="fas fa-bookmark"></i> Unmark'
    markBtn.classList.add("marked")
  } else {
    markBtn.innerHTML = '<i class="fas fa-bookmark"></i> Mark for Review'
    markBtn.classList.remove("marked")
  }
}

function toggleMarkQuestion() {
  const index = markedQuestions.indexOf(currentQuestion)

  if (index === -1) {
    // Mark the question
    markedQuestions.push(currentQuestion)
    markBtn.innerHTML = '<i class="fas fa-bookmark"></i> Unmark'
    markBtn.classList.add("marked")
  } else {
    // Unmark the question
    markedQuestions.splice(index, 1)
    markBtn.innerHTML = '<i class="fas fa-bookmark"></i> Mark for Review'
    markBtn.classList.remove("marked")
  }

  // Update question grid
  updateQuestionGrid()
}

function updateQuestionGrid() {
  const questionButtons = document.querySelectorAll(".question-number-btn")

  questionButtons.forEach((button) => {
    const questionNum = Number.parseInt(button.textContent)

    // Reset classes
    button.className = "question-number-btn"

    // Add appropriate classes
    if (questionNum === currentQuestion) {
      button.classList.add("current")
    }
    if (answeredQuestions.includes(questionNum)) {
      button.classList.add("answered")
    }
    if (markedQuestions.includes(questionNum)) {
      button.classList.add("marked")
    }
  })
}

// Modal functions
function showSubmitModal() {
  submitModal.classList.add("active")
}

function hideSubmitModal() {
  submitModal.classList.remove("active")
}

function showIssueModal() {
  issueModal.classList.add("active")
}

function hideIssueModal() {
  issueModal.classList.remove("active")
}

// Submission functions
function submitExam() {
  // Stop the timer
  clearInterval(examTimer)

  // Stop the camera
  stopMediaStream()

  // Hide the modal
  hideSubmitModal()

  // In a real application, this would send the answers to the server
  alert("Your exam has been submitted successfully!")

  // Redirect to a completion page or back to the selection screen
  setTimeout(() => {
    window.location.reload()
  }, 2000)
}

function submitIssueReport() {
  const issueType = document.getElementById("issue-type").value
  const issueDescription = document.getElementById("issue-description").value

  if (!issueType || !issueDescription) {
    alert("Please select an issue type and provide a description.")
    return
  }

  // In a real application, this would send the report to the server
  alert("Your issue has been reported. Thank you!")

  // Reset and hide the modal
  document.getElementById("issue-type").value = ""
  document.getElementById("issue-description").value = ""
  hideIssueModal()
}

// Simulate answering a question (for demo purposes)
function simulateAnswer() {
  // Add to answered questions if not already there
  if (!answeredQuestions.includes(currentQuestion)) {
    answeredQuestions.push(currentQuestion)
  }

  // Update the progress stats
  document.querySelector(".stat-number").textContent = `${answeredQuestions.length}/${totalQuestions}`

  // Update the progress bar
  const progressPercentage = (answeredQuestions.length / totalQuestions) * 100
  document.querySelector(".progress").style.width = `${progressPercentage}%`

  // Update question grid
  updateQuestionGrid()
}

// Add event listeners to radio buttons for demo purposes
document.querySelectorAll('input[type="radio"]').forEach((radio) => {
  radio.addEventListener("change", simulateAnswer)
})

