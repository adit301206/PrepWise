// Student Dashboard Logic
document.addEventListener('DOMContentLoaded', () => {
    console.log('Student Dashboard Loaded');

    // ==========================================
    // 1. Tab Switching Logic
    // ==========================================
    const tabs = {
        quiz: document.getElementById('tab-quiz'),
        history: document.getElementById('tab-history'),
        leaderboard: document.getElementById('tab-leaderboard')
    };

    const sections = {
        quiz: document.getElementById('section-quiz'),
        history: document.getElementById('section-history'),
        leaderboard: document.getElementById('section-leaderboard')
    };

    function switchTab(activeTabKey) {
        // Reset all tabs
        Object.values(tabs).forEach(tab => {
            if (tab) tab.classList.remove('active');
        });

        // Hide all sections and remove animation class
        Object.values(sections).forEach(section => {
            if (section) {
                section.classList.add('d-none');
                section.classList.remove('fade-in-up');
            }
        });

        // Activate clicked tab
        if (tabs[activeTabKey]) {
            tabs[activeTabKey].classList.add('active');
        }

        // Show active section and trigger animation
        const activeSection = sections[activeTabKey];
        if (activeSection) {
            activeSection.classList.remove('d-none');
            // Force Reflow to restart animation
            void activeSection.offsetWidth;
            activeSection.classList.add('fade-in-up');
        }
    }

    // Add Event Listeners if elements exist
    if (tabs.quiz) tabs.quiz.addEventListener('click', () => switchTab('quiz'));
    if (tabs.history) tabs.history.addEventListener('click', () => switchTab('history'));
    if (tabs.leaderboard) tabs.leaderboard.addEventListener('click', () => switchTab('leaderboard'));


    // ==========================================
    // 2. Dropdown Selection Logic
    // ==========================================
    // ==========================================
    // 2. Dynamic Dropdown Logic (API Connected)
    // ==========================================

    // A. Fetch Subjects on Load
    fetch('/api/subjects')
        .then(response => response.json())
        .then(subjects => {
            const subjectList = document.querySelector('#subjectDropdown + .dropdown-menu');
            subjectList.innerHTML = ''; // Clear existing items

            subjects.forEach(subject => {
                const li = document.createElement('li');
                // Assign colors based on subject name (simple hash or mapping)
                let iconClass = 'fa-book';
                let colorClass = 'text-primary';

                if (subject === 'Computers') { iconClass = 'fa-laptop-code'; colorClass = 'text-primary'; }
                else if (subject === 'Mathematics') { iconClass = 'fa-calculator'; colorClass = 'text-warning'; }
                else if (subject === 'Physics') { iconClass = 'fa-atom'; colorClass = 'text-info'; }
                else if (subject === 'Chemistry') { iconClass = 'fa-flask'; colorClass = 'text-danger'; }

                li.innerHTML = `<a class="dropdown-item" href="#" data-value="${subject}"><i class="fa-solid ${iconClass} me-2 ${colorClass}"></i>${subject}</a>`;
                subjectList.appendChild(li);
            });

            // Re-attach event listeners to new items
            attachDropdownListeners();
        })
        .catch(err => console.error('Error fetching subjects:', err));


    function attachDropdownListeners() {
        document.querySelectorAll('.dropdown-menu .dropdown-item').forEach(item => {
            // Remove old listeners to avoid duplicates (optional if completely re-rendering)
            item.removeEventListener('click', handleDropdownClick);
            item.addEventListener('click', handleDropdownClick);
        });

        // Also attach to Difficulty items since they are static
        const difficultyItems = document.querySelectorAll('[aria-labelledby="difficultyDropdown"] .dropdown-item');
        difficultyItems.forEach(item => {
            item.removeEventListener('click', handleDropdownClick);
            item.addEventListener('click', handleDropdownClick);
        });
    }

    function handleDropdownClick(e) {
        e.preventDefault();
        const toggleBtn = this.closest('.dropdown').querySelector('.custom-dropdown-toggle');
        const toggleText = toggleBtn.querySelector('span');

        if (toggleText) {
            toggleText.innerHTML = this.innerHTML;

            // Logic for Subject Selection -> Fetch Topics
            if (toggleBtn.id === 'subjectDropdown') {
                const selectedSubject = this.getAttribute('data-value');
                fetchTopics(selectedSubject);
            }
        }
    }

    let selectedTopics = new Set();
    // const floatingBar = document.getElementById('floating-bar'); // Removed
    // const selectedCountText = document.getElementById('selected-count-text'); // Removed

    // Main Start Quiz Button
    const btnStartQuizEngine = document.querySelector('.btn-start-quiz');

    // Attach Start Quiz Listener to the Main Button
    if (btnStartQuizEngine) {
        btnStartQuizEngine.addEventListener('click', () => {
            if (selectedTopics.size > 0) {
                const topicIds = Array.from(selectedTopics).join(',');
                const numQuestions = document.getElementById('numQuestions').value || 10;

                // Create a temporary form to POST data
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/start-quiz';

                // Topic IDs Input
                const topicsInput = document.createElement('input');
                topicsInput.type = 'hidden';
                topicsInput.name = 'topic_ids_hidden'; // Matches backend expectation
                topicsInput.value = topicIds;
                form.appendChild(topicsInput);

                // Num Questions Input
                const countInput = document.createElement('input');
                countInput.type = 'hidden';
                countInput.name = 'num_questions';
                countInput.value = numQuestions;
                form.appendChild(countInput);

                document.body.appendChild(form);
                form.submit();
            } else {
                alert("Please select at least one topic to start the quiz.");
            }
        });
    }

    function fetchTopics(subjectName) {
        const topicsSection = document.getElementById('topics-section');
        const topicsGrid = document.querySelector('.topics-grid');
        const emptyState = document.querySelector('.empty-state');
        const skeletonLoader = document.querySelector('.topics-skeleton');

        // Clear selection when changing subject
        selectedTopics.clear();

        // Show loading state or reset
        if (topicsSection) {
            topicsSection.classList.remove('d-none');
            // Fade in effect
            setTimeout(() => {
                topicsSection.classList.remove('opacity-0');
                topicsSection.classList.add('opacity-100');
            }, 50);
        }

        // 1. Show Skeleton, Hide others
        if (skeletonLoader) skeletonLoader.classList.remove('d-none');
        if (topicsGrid) topicsGrid.classList.add('d-none');
        if (emptyState) emptyState.classList.add('d-none');

        // Add a small artificial delay to show off the skeleton (optional but good for UX feel if API is too fast)
        const delay = 600; 
        const fetchPromise = fetch(`/api/topics?subject=${encodeURIComponent(subjectName)}`).then(res => res.json());
        const delayPromise = new Promise(resolve => setTimeout(resolve, delay));

        Promise.all([fetchPromise, delayPromise])
            .then(([topics]) => {
                // 2. Hide Skeleton
                if (skeletonLoader) skeletonLoader.classList.add('d-none');

                topicsGrid.innerHTML = ''; // Clear old topics

                if (topics.length > 0) {
                    emptyState.classList.add('d-none');
                    topicsGrid.classList.remove('d-none');

                    topics.forEach(topic => {
                        // Determine icon based on Subject Name
                        let iconClass = 'fa-book';
                        if (subjectName === 'Computers') iconClass = 'fa-code';
                        else if (subjectName === 'Mathematics') iconClass = 'fa-calculator';
                        else if (subjectName === 'Physics') iconClass = 'fa-atom';
                        else if (subjectName === 'Chemistry') iconClass = 'fa-flask';

                        if (topic.name === 'Database Management') iconClass = 'fa-database';
                        if (topic.name === 'Web Development') iconClass = 'fa-globe';
                        if (topic.name === 'Artificial Intelligence') iconClass = 'fa-brain';
                        if (topic.name === 'Cyber Security') iconClass = 'fa-shield-halved';

                        const chip = document.createElement('div');
                        chip.className = 'topic-chip';
                        chip.innerHTML = `
                            <div class="topic-check-indicator"></div>
                            <div class="topic-icon-wrapper">
                                <i class="fa-solid ${iconClass}"></i>
                            </div>
                            <span class="topic-name">${topic.name}</span>
                        `;

                        chip.addEventListener('click', () => {
                            if (selectedTopics.has(topic.id)) {
                                selectedTopics.delete(topic.id);
                                chip.classList.remove('selected');
                            } else {
                                selectedTopics.add(topic.id);
                                chip.classList.add('selected');
                            }
                        });

                        topicsGrid.appendChild(chip);
                    });
                } else {
                    emptyState.classList.remove('d-none');
                    topicsGrid.classList.add('d-none');
                    selectedTopics.clear();
                }
            })
            .catch(err => {
                console.error("Error fetching topics:", err);
                if (skeletonLoader) skeletonLoader.classList.add('d-none');
                topicsGrid.innerHTML = `<div class="col-12 text-center text-danger">Failed to load topics. Please check your connection or try again.</div>`;
                topicsGrid.classList.remove('d-none');
            });
    }

    // Floating bar function removed
    /*
    function updateFloatingBar() {
        const count = selectedTopics.size;
    
        if (count > 0) {
            if (floatingBar.classList.contains('d-none')) {
                floatingBar.classList.remove('d-none');
            }
            selectedCountText.textContent = `${count} Topic${count > 1 ? 's' : ''} Selected`;
        } else {
            floatingBar.classList.add('d-none');
        }
    }
    */

    // Initial attachment for static items (Difficulty, etc.)
    attachDropdownListeners();

});
