// Minimal JS for Demo Flow
document.addEventListener('DOMContentLoaded', function () {
    // 1. Interactive Config Buttons (Visual Only)
    const configOptions = document.querySelectorAll('.config-option');
    configOptions.forEach(opt => {
        opt.addEventListener('click', function () {
            // Find siblings and remove active
            this.parentElement.querySelectorAll('.config-option').forEach(sib => sib.classList.remove('active'));
            // Add active to clicked
            this.classList.add('active');
        });
    });

    // 2. Initialize Quiz Transition
    document.getElementById('initQuizBtn').addEventListener('click', function () {
        document.getElementById('configCard').classList.add('d-none');
        document.getElementById('quizCard').classList.remove('d-none');

        // Get Difficulty
        let difficulty = 'medium';
        const activeDiff = document.querySelector('#difficultyOptions .config-option.active');
        if (activeDiff) {
            difficulty = activeDiff.getAttribute('data-value');
        }

        // Get Subject
        let subject = 'cs';
        const activeSubject = document.querySelector('#subjectOptions .config-option.active');
        if (activeSubject) {
            subject = activeSubject.getAttribute('data-value');
        }

        // Construct Start ID
        const startId = `${subject}-${difficulty}-q1`;
        console.log('Starting quiz:', startId);

        const startSlide = document.getElementById(startId);
        if (startSlide) {
            startSlide.classList.remove('d-none');
            startSlide.classList.add('active');
        } else {
            console.error('Quiz start slide not found:', startId);
            // Fallback
            const fallback = document.querySelector('.question-slide'); // Any slide
            if (fallback) fallback.classList.remove('d-none');
        }
    });
});

// 3. Handle Question Option Click (Navigation)
function handleOptionClick(element, nextQuestionId) {
    // Visual Select
    element.parentElement.querySelectorAll('.quiz-option').forEach(opt => opt.classList.remove('selected'));
    element.classList.add('selected');

    // Wait and go to next
    setTimeout(() => {
        // Hide current slide
        element.closest('.question-slide').classList.add('d-none');

        // Show next slide
        const nextSlide = document.getElementById(nextQuestionId);
        if (nextSlide) {
            nextSlide.classList.remove('d-none');
        }
    }, 600);
}
