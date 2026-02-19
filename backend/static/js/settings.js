document.addEventListener('DOMContentLoaded', () => {

    // --- TAB SWITCHING ---
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(nav => nav.classList.remove('active'));
            tabContents.forEach(tab => tab.classList.remove('active'));

            item.classList.add('active');
            const tabId = item.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // --- PASSWORD VISIBILITY ---
    document.querySelectorAll('.toggle-password').forEach(icon => {
        icon.addEventListener('click', () => {
            const input = icon.previousElementSibling;
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('fa-eye', 'fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('fa-eye-slash', 'fa-eye');
            }
        });
    });

    // --- TOAST NOTIFICATIONS ---
    function showToast(message, isError = false) {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.style.background = isError ? 'rgba(239, 68, 68, 0.9)' : 'rgba(16, 185, 129, 0.9)';
        toast.classList.remove('hidden');
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.classList.add('hidden'), 300);
        }, 3000);
    }

    // --- API: CHANGE EMAIL ---
    const emailForm = document.getElementById('email-form');
    if (emailForm) {
        emailForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const newEmail = document.getElementById('new-email').value;
            const btn = emailForm.querySelector('button');
            const originalText = btn.innerText;

            btn.disabled = true;
            btn.innerText = "Updating...";

            try {
                const res = await fetch('/api/settings/update-email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ new_email: newEmail })
                });
                const data = await res.json();

                if (data.error) throw new Error(data.error);
                showToast(data.message);
                emailForm.reset();
            } catch (err) {
                showToast(err.message, true);
            } finally {
                btn.disabled = false;
                btn.innerText = originalText;
            }
        });
    }

    // --- API: CHANGE PASSWORD ---
    const passwordForm = document.getElementById('password-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const newPass = document.getElementById('new-password').value;
            const confirmPass = document.getElementById('confirm-password').value;

            if (newPass !== confirmPass) {
                showToast("New passwords do not match!", true);
                return;
            }

            const btn = passwordForm.querySelector('button');
            const originalText = btn.innerText;
            btn.disabled = true;
            btn.innerText = "Updating...";

            try {
                const res = await fetch('/api/settings/update-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ new_password: newPass })
                });
                const data = await res.json();

                if (data.error) throw new Error(data.error);
                showToast(data.message);
                passwordForm.reset();
            } catch (err) {
                showToast(err.message, true);
            } finally {
                btn.disabled = false;
                btn.innerText = originalText;
            }
        });
    }

    // --- API: DELETE HISTORY ---
    window.confirmDelete = async function () {
        if (confirm("Are you sure you want to delete all your quiz history? This cannot be undone!")) {
            try {
                const res = await fetch('/api/settings/delete-history', { method: 'POST' });
                const data = await res.json();
                if (data.error) throw new Error(data.error);

                showToast(data.message);
                // Optional: Reload to update stats
                setTimeout(() => location.reload(), 1500);
            } catch (err) {
                showToast(err.message, true);
            }
        }
    };

    // --- PDF GENERATION ---
    const pdfBtn = document.querySelector('.btn-outline');
    if (pdfBtn) {
        pdfBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const originalText = pdfBtn.innerHTML;
            pdfBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating PDF...';
            pdfBtn.style.pointerEvents = 'none';

            try {
                // Update Date
                const dateElem = document.getElementById('pdf-date');
                if (dateElem) dateElem.innerText = new Date().toLocaleDateString();

                // Target the specific content container
                const element = document.getElementById('pdf-content');
                if (!element) throw new Error("PDF Content container not found.");

                // Generate
                const opt = {
                    margin: 10,
                    filename: 'Student_Analysis_Report.pdf',
                    image: { type: 'jpeg', quality: 0.98 },
                    html2canvas: { scale: 2, useCORS: true, logging: false },
                    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
                };

                await html2pdf().set(opt).from(element).save();
                showToast("Report downloaded successfully!");

            } catch (err) {
                console.error(err);
                showToast("Error generating PDF: " + err.message, true);
            } finally {
                pdfBtn.innerHTML = originalText;
                pdfBtn.style.pointerEvents = 'auto';
            }
        });
    }
});
