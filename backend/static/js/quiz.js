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
            btnExplain: document.getElementById('btn-explain'), // AI Tutor
            btnAction: document.getElementById('btn-action'),
            btnConfirm: document.getElementById('btn-confirm-finish'), // FIXED: Added missing selector
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

        // Explain Button (AI Tutor)
        this.dom.btnExplain.addEventListener('click', () => {
            const q = this.questions[this.currentIndex];
            const state = this.history[this.currentIndex];
            // Get text for options
            const selectedText = q[`option_${state.selected.toLowerCase()}`];
            const correctText = q[`option_${q.correct_option.toLowerCase()}`];

            this.openAIExplanation(q.question_text, selectedText, correctText);
        });

        // Chat Form (Follow-up) - Updated with robust logic
        const chatForm = document.getElementById('ai-chat-form');
        if (chatForm) {
            chatForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const inputField = document.getElementById('chat-input');
                const submitBtn = document.querySelector('#ai-chat-form button');
                const msg = inputField.value.trim();
                if (!msg) return;

                this.appendMessage('user', msg);
                inputField.value = '';
                inputField.disabled = true;
                submitBtn.disabled = true;

                const typingId = 'typing-chat-' + Date.now();
                this.appendMessage('ai', `<span id="${typingId}" class="typing-indicator"><span>.</span><span>.</span><span>.</span></span>`);

                try {
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ action: 'chat', message: msg, history: this.chatHistory || [] })
                    });

                    if (!res.ok) throw new Error(`Server returned ${res.status}`);
                    const data = await res.json();

                    const typingElem = document.getElementById(typingId);
                    if (typingElem) typingElem.closest('.chat-bubble').remove();

                    if (data.error) {
                        this.appendMessage('ai', `<span class="text-danger">${data.error}</span>`);
                    } else if (data.reply) {
                        this.appendMessage('ai', data.reply);
                        if (!this.chatHistory) this.chatHistory = [];
                        this.chatHistory.push({ sender: 'user', text: msg });
                        this.chatHistory.push({ sender: 'ai', text: data.reply });
                    }
                } catch (err) {
                    console.error("Chat Error:", err);
                    const typingElem = document.getElementById(typingId);
                    if (typingElem) typingElem.closest('.chat-bubble').remove();
                    this.appendMessage('ai', `<span class="text-danger">Network error. Please try again.</span>`);
                } finally {
                    inputField.disabled = false;
                    submitBtn.disabled = false;
                    inputField.focus();
                }
            });
        }

        // Action Button
        this.dom.btnAction.addEventListener('click', () => this.handleAction());

        // Confirm Finish Modal Button
        if (this.dom.btnConfirm) {
            this.dom.btnConfirm.addEventListener('click', () => {
                // Hide modal first to correct backdrop issues
                const modalEl = document.getElementById('finishQuizModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();

                this.finishQuiz();
            });
        }

        // Global Keyboard Shortcuts (A, B, C, D)
        document.addEventListener('keydown', (e) => {
            // Ignore if user is typing in an input field (search, chat, etc.)
            const tag = e.target.tagName.toUpperCase();
            if (tag === 'INPUT' || tag === 'TEXTAREA') return;

            const key = e.key.toUpperCase();
            const optionMap = { 'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D' };

            if (optionMap.hasOwnProperty(key)) {
                const selectedLetter = optionMap[key];

                // Only select if current question has this option
                const q = this.questions[this.currentIndex];
                const optKey = `option_${selectedLetter.toLowerCase()}`;

                if (q[optKey]) {
                    this.selectOption(selectedLetter);
                }
            }
        });
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

        // Explain Button State
        if (state.locked && state.result === 'incorrect') {
            this.dom.btnExplain.classList.remove('d-none');
        } else {
            this.dom.btnExplain.classList.add('d-none');
        }
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
            // Show Explain Button
            this.dom.btnExplain.classList.remove('d-none');
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
        // FIX 1: Do NOT lock the state. Allow the user to come back and answer it later.
        state.locked = false;
        state.result = 'skipped';

        // Update the toast to let them know they can return
        this.showToast('skipped', 'Skipped. You can return to this from the palette!');

        this.updateActionBtn();
        this.updateSidebarUI();
        this.updateFooterUI();

        // Auto-move after brief delay
        setTimeout(() => {
            if (this.currentIndex < this.questions.length - 1) {
                this.loadQuestion(this.currentIndex + 1);
            } else {
                // FIX 2: Do NOT auto-finish the quiz if they skip the last question.
                // Show the confirmation modal so they have a chance to go back and review.
                const modal = new bootstrap.Modal(document.getElementById('finishQuizModal'));
                modal.show();
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

        // Build Detailed History Array for the Review Page
        const detailed_history = this.questions.map((q, i) => {
            const state = this.history[i];
            let status = 'skipped';
            if (state.result === 'correct') status = 'correct';
            else if (state.result === 'incorrect') status = 'incorrect';

            return {
                question_text: q.question_text,
                correct_option_text: q[`option_${(q.correct_option || '').toLowerCase()}`] || 'N/A',
                user_selected_text: state.selected ? q[`option_${state.selected.toLowerCase()}`] : null,
                is_correct: status === 'correct',
                is_skipped: status === 'skipped',
                explanation: q.explanation
            };
        });

        const skippedCount = this.history.filter(h => h.result === 'skipped').length;

        const payload = {
            user_id: this.userId,
            score: this.score,
            total: this.questions.length,
            topic_id: this.topicId,
            detailed_history: detailed_history // Send data to backend
        };

        try {
            await fetch('/api/save-quiz-result', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            window.location.href = `/quiz/result?score=${this.score}&total=${this.questions.length}&skipped=${skippedCount}`;
        } catch (e) {
            console.error(e);
            window.location.href = `/quiz/result?score=${this.score}&total=${this.questions.length}&skipped=${skippedCount}`;
        }
    }

    // ================= AI TUTOR METHODS ================= //

    openAIExplanation(qText, selectedText, correctText) {
        const offcanvas = new bootstrap.Offcanvas(document.getElementById('aiChatOffcanvas'));
        offcanvas.show();

        const chatContainer = document.getElementById('chat-messages');
        chatContainer.innerHTML = '';
        this.chatHistory = [];

        // Use a unique ID for safe removal later
        const typingId = 'typing-explain';
        this.appendMessage('ai', `<span id="${typingId}" class="typing-indicator"><span>.</span><span>.</span><span>.</span></span>`);

        fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: 'explain',
                question: qText,
                selected: selectedText,
                correct: correctText,
                history: []
            })
        })
            .then(res => {
                if (!res.ok) throw new Error(`Server returned ${res.status}`);
                return res.json();
            })
            .then(data => {
                console.log("AI Response Data:", data); // DEBUGGING

                // Safely remove typing indicator
                const typingElem = document.getElementById(typingId);
                if (typingElem) typingElem.closest('.chat-bubble').remove();

                if (data.error) {
                    this.appendMessage('ai', `<span class="text-danger">${data.error}</span>`);
                } else if (data.reply) {
                    this.appendMessage('ai', data.reply);
                    this.chatHistory.push({ sender: 'user', text: data.internal_prompt || "Explain mistake" });
                    this.chatHistory.push({ sender: 'ai', text: data.reply });
                } else {
                    this.appendMessage('ai', `<span class="text-danger">Received empty response.</span>`);
                }
            })
            .catch(err => {
                console.error("Fetch Error:", err);
                const typingElem = document.getElementById(typingId);
                if (typingElem) typingElem.closest('.chat-bubble').remove();
                this.appendMessage('ai', `<span class="text-danger">Failed to connect to AI Tutor. Check browser console for details.</span>`);
            });
    }

    appendMessage(sender, text) {
        const chatContainer = document.getElementById('chat-messages');
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-bubble ${sender === 'user' ? 'bubble-user' : 'bubble-ai'}`;

        // Check if text is HTML (typing indicator) or plain text
        let formattedText = text;
        if (!text.includes('<span') && !text.includes('<div')) {
            formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
        }

        msgDiv.innerHTML = formattedText;
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}