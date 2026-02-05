/**
 * Shared Authentication & Profile Logic
 * Handles profile fetching, offcanvas population, and logout.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Run auth check on load
    initAuth();
});

function initAuth() {
    const accessToken = localStorage.getItem('access_token');
    const userJson = localStorage.getItem('user');

    if (!accessToken || !userJson) {
        // Optional: Redirect to login if not on public pages
        // For now, simple check. Dashboard pages typically require auth.
        // We won't auto-redirect here to avoid breaking public demos, 
        // but we will try to load the profile if token exists.
        return;
    }

    // 1. Fetch Real Profile Data
    fetchUserProfile(accessToken);
}

async function fetchUserProfile(token) {
    try {
        const response = await fetch('/api/user/profile', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            const name = data.name || "User";
            const initial = name.charAt(0).toUpperCase();

            // 2. Update UI Elements with delay
            setTimeout(() => {
                updateAvatarUI(initial);
                populateOffcanvas(name, data.email, initial);
            }, 100);

        } else {
            console.warn("Failed to fetch profile:", response.status);
            if (response.status === 401) {
                // Token expired
                handleLogout(); // Auto logout? Or just let it fail.
            }
        }
    } catch (error) {
        console.error("Error fetching user profile:", error);
    }
}

function updateAvatarUI(initial) {
    // Update Navbar Badge
    const navbarInitial = document.getElementById('navbarUserInitial');
    // Also support finding by class if ID isn't unique enough or if multiple
    if (navbarInitial) {
        navbarInitial.innerText = initial;
    }
}

function populateOffcanvas(name, email, initial) {
    const offcanvasName = document.getElementById('offcanvasUserName');
    const offcanvasEmail = document.getElementById('offcanvasUserEmail');
    const offcanvasInitial = document.getElementById('offcanvasUserInitial');

    if (offcanvasName) offcanvasName.innerText = name;
    if (offcanvasEmail) offcanvasEmail.innerText = email;
    if (offcanvasInitial) offcanvasInitial.innerText = initial;
}

function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = "/";
}
