document.addEventListener('DOMContentLoaded', () => {
    const btnGenerate = document.getElementById('btn-generate-insight');

    if (btnGenerate) {
        btnGenerate.addEventListener('click', analyzePerformance);
    }
});

async function analyzePerformance() {
    const contentDiv = document.getElementById('ai-insight-content');
    const loader = document.getElementById('ai-insight-loader');
    const btn = document.getElementById('btn-generate-insight');

    // Hide button & content, show loader
    btn.style.display = 'none';
    contentDiv.style.display = 'none';
    loader.style.display = 'block';

    try {
        const response = await fetch('/api/review/ai-insight', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({}) // Data is pulled securely from Flask session
        });

        const data = await response.json();

        if (data.error) {
            contentDiv.innerHTML = `<div class="alert alert-danger mb-0">${data.error}</div>`;
        } else {
            // Render the AI HTML response
            contentDiv.innerHTML = data.insight;
        }

    } catch (err) {
        console.error(err);
        contentDiv.innerHTML = `<div class="alert alert-danger mb-0">Failed to connect to AI server. Check your connection.</div>`;
    } finally {
        // Hide loader, show the newly generated content
        loader.style.display = 'none';
        contentDiv.style.display = 'block';
    }
}
