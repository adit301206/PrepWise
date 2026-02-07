/**
 * Quiz Manager - Strict Version
 * Handles logic for:
 * - Left Sidebar (Question Palette)
 * - Glass Card Interaction (Tiles)
 * - Smart Buttons (Skip/Check/Next)
 * - Segmented Progress Footer
 */

class QuizManager {
    constructor(questionsData, userId, topicId) {
        this.questions = questionsData;
        this.userId = userId;
        this.topicId = topicId;

        this.currentIndex = 0;
        this.score = 0;

        // State Array: Stores result for each question
        // { selected: 'A', result: 'correct'|'incorrect'|'skipped'|null, locked: false }
        this.history = this.questions.map(() => ({
            selected: null,
            result: null,
            locked: false
        }));

        // DOM Cache
        this.dom = {
            sidebar: document.getElementById('sidebar-grid'),
            footer: document.getElementById('progress-bar-container'),
            qNum: document.getElementById('question-number'),
            qText: document.getElementById('question-text'),
            diffBadge: document.getElementById('difficulty-badge'),
            optionsBox: document.getElementById('options-container'),
            btnPrev: document.getElementById('btn-prev'),
            btnAction: document.getElementById('btn-action'),
            toast: document.getElementById('explanation-toast'),
            toastHead: document.getElementById('toast-header'),
            toastBody: document.getElementById('toast-body')
        };

        this.init();
    }

    init() {
        this.renderSidebar();
        this.renderFooter();
        this.loadQuestion(0);
        this.attachListeners();
    }

    attachListeners() {
        // Prev
        this.dom.btnPrev.addEventListener('click', () => {
            if (this.currentIndex > 0) this.loadQuestion(this.currentIndex - 1);
        });

        // Action Button
        this.dom.btnAction.addEventListener('click', () => this.handleAction());

        // Confirm Finish Modal Button
        const btnConfirm = document.getElementById('btn-confirm-finish');
        if (btnConfirm) {
            btnConfirm.addEventListener('click', () => {
                // Hide modal first to correct backdrop issues
                const modalEl = document.getElementById('finishQuizModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();

                this.finishQuiz();
            });
        }
    }

    // ================= RENDERERS ================= //

    renderSidebar() {
        this.dom.sidebar.innerHTML = '';
        this.questions.forEach((_, i) => {
            const badge = document.createElement('div');
            badge.className = 'q-badge';
            badge.textContent = i + 1;
            badge.dataset.index = i;
            badge.onclick = () => this.loadQuestion(i);
            this.dom.sidebar.appendChild(badge);
        });
    }

    renderFooter() {
        this.dom.footer.innerHTML = '';
        this.questions.forEach((_, i) => {
            const seg = document.createElement('div');
            seg.className = 'progress-segment';
            seg.id = `seg-${i}`;
            this.dom.footer.appendChild(seg);
        });
    }

    // ================= LOAD QUESTION ================= //

    loadQuestion(index) {
        if (index < 0 || index >= this.questions.length) return;
        this.currentIndex = index;
        const q = this.questions[index];
        const state = this.history[index];

        // 1. Text Content
        this.dom.qNum.textContent = `QUESTION ${index + 1} OF ${this.questions.length}`;
        let diffColor = 'text-warning';
        if (q.difficulty === 'Easy') diffColor = 'text-success';
        if (q.difficulty === 'Hard') diffColor = 'text-danger';
        this.dom.diffBadge.className = `fw-bold ${diffColor} text-uppercase`;
        this.dom.diffBadge.textContent = q.difficulty || 'Medium';
        this.dom.qText.textContent = q.question_text;

        // 2. Options
        this.dom.optionsBox.innerHTML = '';
        ['A', 'B', 'C', 'D'].forEach(letter => {
            const optText = q[`option_${letter.toLowerCase()}`];
            if (!optText) return;

            const tile = document.createElement('div');
            tile.className = 'option-tile';
            tile.dataset.value = letter;

            // Rehydrate visual state
            if (state.selected === letter) {
                tile.classList.add('selected');
                if (state.locked) {
                    // Show correct/incorrect styles
                    if (state.result === 'correct') tile.classList.add('correct');
                    if (state.result === 'incorrect') tile.classList.add('incorrect');
                }
            }

            // Show correct answer if incorrect
            if (state.locked && state.result === 'incorrect' && letter === q.correct_option) {
                tile.classList.add('correct');
            }

            const marker = document.createElement('div');
            marker.className = 'option-marker';
            marker.textContent = letter;

            const text = document.createElement('div');
            text.className = 'option-text';
            text.textContent = optText;

            tile.innerHTML = ''; // Clear just in case
            tile.appendChild(marker);
            tile.appendChild(text);

            tile.onclick = () => this.selectOption(letter);
            this.dom.optionsBox.appendChild(tile);
        });

        // 3. UI Updates
        this.dom.btnPrev.disabled = (index === 0);
        this.hideToast();
        this.updateActionBtn();
        this.updateSidebarUI();
        this.updateFooterUI();
    }

    // ================= INTERACTION ================= //

    selectOption(letter) {
        const state = this.history[this.currentIndex];
        if (state.locked) return; // Prevent changing after lock

        state.selected = letter;

        // Update DOM classes
        const tiles = this.dom.optionsBox.querySelectorAll('.option-tile');
        tiles.forEach(t => {
            t.classList.remove('selected');
            if (t.dataset.value === letter) t.classList.add('selected');
        });

        this.updateActionBtn();
    }

    updateActionBtn() {
        const state = this.history[this.currentIndex];
        const btn = this.dom.btnAction;

        // Reset Variant Classes
        btn.classList.remove('skip', 'check');

        if (state.locked) {
            // Completed Question
            if (this.currentIndex === this.questions.length - 1) {
                btn.textContent = "FINISH QUIZ";
            } else {
                btn.textContent = "NEXT QUESTION";
            }
        } else {
            // Not Checked Yet
            if (state.selected) {
                btn.textContent = "CHECK ANSWER";
                btn.classList.add('check');
            } else {
                btn.textContent = "SKIP & NEXT";
                btn.classList.add('skip'); // Yellow styling
            }
        }
    }

    handleAction() {
        const state = this.history[this.currentIndex];

        if (state.locked) {
            // Logic for "NEXT QUESTION" or "FINISH"
            if (this.currentIndex < this.questions.length - 1) {
                this.loadQuestion(this.currentIndex + 1);
            } else {
                // SHOW CONFIRMATION MODAL INSTEAD OF IMMEDIATE FINISH
                const modal = new bootstrap.Modal(document.getElementById('finishQuizModal'));
                modal.show();
            }
        } else {
            // Logic for "CHECK" or "SKIP"
            if (state.selected) {
                this.checkAnswer(state);
            } else {
                this.skipQuestion(state);
            }
        }
    }

    // ================= CORE LOGIC ================= //

    checkAnswer(state) {
        const q = this.questions[this.currentIndex];
        const correctVal = (q.correct_option || '').trim().toUpperCase();

        state.locked = true;

        if (state.selected === correctVal) {
            state.result = 'correct';
            this.score++;
            this.showToast(true, q.explanation);
        } else {
            state.result = 'incorrect';
            this.showToast(false, q.explanation);
        }

        // Trigger animations/styles
        const tiles = this.dom.optionsBox.querySelectorAll('.option-tile');
        tiles.forEach(t => {
            if (t.dataset.value === state.selected) {
                t.classList.add(state.result); // .correct or .incorrect
            }
            if (state.result === 'incorrect' && t.dataset.value === correctVal) {
                t.classList.add('correct'); // Highlight actual correct
            }
        });

        this.updateActionBtn();
        this.updateSidebarUI();
        this.updateFooterUI();
    }

    skipQuestion(state) {
        state.locked = true;
        state.result = 'skipped';

        this.showToast('skipped', 'You skipped this question.');

        this.updateActionBtn();
        this.updateSidebarUI();
        this.updateFooterUI();

        // Auto-move after brief delay
        setTimeout(() => {
            if (this.currentIndex < this.questions.length - 1) {
                this.loadQuestion(this.currentIndex + 1);
            } else {
                this.finishQuiz();
            }
        }, 800);
    }

    // ================= UI HELPERS ================= //

    showToast(status, text) {
        const t = this.dom.toast;
        t.className = 'explanation-toast show'; // Reset

        const h = this.dom.toastHead;

        if (status === true) {
            h.innerHTML = '<i class="fa-solid fa-check-circle text-success"></i> Correct!';
            t.classList.add('correct');
        } else if (status === 'skipped') {
            h.innerHTML = '<i class="fa-solid fa-forward text-warning"></i> Skipped';
            t.classList.add('skipped');
        } else {
            h.innerHTML = '<i class="fa-solid fa-times-circle text-danger"></i> Incorrect';
            t.classList.add('incorrect');
        }

        this.dom.toastBody.innerHTML = text || "No explanation available.";
    }

    hideToast() {
        this.dom.toast.classList.remove('show');
    }

    updateSidebarUI() {
        const badges = this.dom.sidebar.querySelectorAll('.q-badge');
        badges.forEach((b, i) => {
            b.className = 'q-badge'; // reset
            if (i === this.currentIndex) b.classList.add('active');

            const r = this.history[i].result;
            if (r === 'correct') b.classList.add('solved-correct');
            if (r === 'incorrect') b.classList.add('solved-incorrect');
            if (r === 'skipped') b.classList.add('skipped');
        });
    }

    updateFooterUI() {
        const segs = this.dom.footer.querySelectorAll('.progress-segment');
        segs.forEach((s, i) => {
            s.className = 'progress-segment';
            if (i === this.currentIndex) s.classList.add('active');

            const r = this.history[i].result;
            if (r === 'correct') s.classList.add('correct');
            if (r === 'incorrect') s.classList.add('incorrect');
            if (r === 'skipped') s.classList.add('skipped');
        });
    }

    async finishQuiz() {
        const btn = this.dom.btnAction;
        btn.innerHTML = '<span class="loading-spinner"></span> Saving...';
        btn.disabled = true;

        const payload = {
            user_id: this.userId,
            score: this.score,
            total: this.questions.length,
            topic_id: this.topicId
        };

        try {
            await fetch('/api/save-quiz-result', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            window.location.href = `/quiz/result?score=${this.score}&total=${this.questions.length}`;
        } catch (e) {
            console.error(e);
            window.location.href = `/quiz/result?score=${this.score}&total=${this.questions.length}`;
        }
    }
}
