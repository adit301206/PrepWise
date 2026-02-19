document.addEventListener('DOMContentLoaded', () => {
    // --- CUSTOM GLASS DROPDOWN LOGIC ---
    const dropdownTrigger = document.getElementById('dropdownTrigger');
    const dropdownOptions = document.getElementById('dropdownOptions');
    const selectedText = document.getElementById('selectedText');
    const options = document.querySelectorAll('.custom-option');
    const chartImg = document.getElementById('progressChartImg');
    const loader = document.getElementById('chartLoader');

    if (dropdownTrigger && dropdownOptions) {
        // Toggle Dropdown
        dropdownTrigger.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent closing immediately
            dropdownOptions.classList.toggle('show');
            dropdownTrigger.classList.toggle('active');
        });

        // Close when clicking outside
        document.addEventListener('click', (e) => {
            if (!dropdownTrigger.contains(e.target) && !dropdownOptions.contains(e.target)) {
                dropdownOptions.classList.remove('show');
                dropdownTrigger.classList.remove('active');
            }
        });

        // Handle Option Click
        options.forEach(option => {
            option.addEventListener('click', async function () {
                // 1. Update UI Selection
                options.forEach(opt => opt.classList.remove('selected'));
                this.classList.add('selected');

                // 2. Update Trigger Text
                selectedText.textContent = this.textContent;

                // 3. Close Dropdown
                dropdownOptions.classList.remove('show');
                dropdownTrigger.classList.remove('active');

                // 4. Trigger Chart Update
                const timeFilter = this.dataset.value;
                await updateChart(timeFilter);
            });
        });
    }

    async function updateChart(timeFilter) {
        if (!chartImg || !loader) return;

        // UI Feedback: Show Loader & Dim Image
        loader.classList.remove('d-none');
        chartImg.style.opacity = '0.3';

        try {
            const response = await fetch('/api/analytics/progress-chart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ time_filter: timeFilter })
            });

            if (!response.ok) {
                throw new Error(`Server Error: ${response.status}`);
            }

            const data = await response.json();

            if (data.chart) {
                // Update Image Source
                chartImg.src = `data:image/png;base64,${data.chart}`;
            } else if (data.error) {
                console.error("API Error:", data.error);
                alert("Failed to update chart: " + data.error);
            }

        } catch (error) {
            console.error("Fetch Error:", error);
            alert("Something went wrong. Please try again.");
        } finally {
            // Restore UI
            loader.classList.add('d-none');
            chartImg.style.opacity = '1';
        }
    }
});
