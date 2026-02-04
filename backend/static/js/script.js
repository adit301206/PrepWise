document.addEventListener('DOMContentLoaded', function () {
    const navbarContent = document.getElementById('navbarContent');
    const mainContent = document.querySelector('main');
    const originalPadding = 100; // Match the inline style padding-top: 100px

    /* --- AUTH STATE LOGIC --- */
    const userJson = localStorage.getItem('user');
    const accessToken = localStorage.getItem('access_token');
    const isLoggedIn = userJson && accessToken;

    const loginBtnContainer = document.getElementById('loginBtnContainer');
    const profileAvatarContainer = document.getElementById('profileAvatarContainer');
    const mobileProfileContainer = document.getElementById('mobileProfileContainer');
    const getStartedBtns = document.querySelectorAll('.btn-get-started');

    if (isLoggedIn) {
        // 1. Navbar State
        if (loginBtnContainer) loginBtnContainer.classList.add('d-none');
        if (profileAvatarContainer) profileAvatarContainer.classList.remove('d-none');
        if (mobileProfileContainer) mobileProfileContainer.classList.remove('d-none');

        // 2. Parse User Data
        let user = {};
        try { user = JSON.parse(userJson); } catch (e) { console.error("Error parsing user data", e); }

        const role = user.role || 'student';
        const dashboardUrl = role === 'teacher' ? '/teacher-console' : '/student-dashboard';

        // 3. Get Started Button Redirection
        getStartedBtns.forEach(btn => {
            btn.href = dashboardUrl;
            btn.innerHTML = `Go to Dashboard <i class="fa-solid fa-arrow-right ms-2"></i>`;
        });

        // 4. Initial UI Setup (Fallback)
        const dashboardLink = document.getElementById('dashboardLink');
        if (dashboardLink) dashboardLink.href = dashboardUrl;

        // 5. Fetch Real Profile Data from DB
        fetchUserProfile(accessToken);

    } else {
        // Logged Out State
        if (loginBtnContainer) loginBtnContainer.classList.remove('d-none');
        if (profileAvatarContainer) profileAvatarContainer.classList.add('d-none');
        if (mobileProfileContainer) mobileProfileContainer.classList.add('d-none');

        // Ensure Get Started goes to Login
        getStartedBtns.forEach(btn => {
            btn.href = "/login";
        });
    }

    /* --- EXISTING ANIMATION LOGIC --- */
    if (navbarContent && mainContent) {
        // Add transition for smooth effect
        mainContent.style.transition = 'padding-top 0.35s ease-in-out';

        navbarContent.addEventListener('show.bs.collapse', function () {
            const navList = navbarContent.querySelector('.navbar-nav');
            const authButtons = navbarContent.querySelector('.d-flex');
            let estimatedHeight = 0;
            if (navList) estimatedHeight += navList.scrollHeight;
            if (authButtons) estimatedHeight += authButtons.scrollHeight;
            // Add some buffer
            estimatedHeight += 20;

            mainContent.style.paddingTop = (originalPadding + estimatedHeight) + 'px';
        });

        navbarContent.addEventListener('hide.bs.collapse', function () {
            mainContent.style.paddingTop = originalPadding + 'px';
        });

        navbarContent.addEventListener('shown.bs.collapse', function () {
            const exactHeight = navbarContent.scrollHeight;
            mainContent.style.paddingTop = (originalPadding + exactHeight) + 'px';
        });
    }

    // Lightning Split Logic
    const boltTrigger = document.querySelector('.bolt-trigger');
    const demoWrapper = document.querySelector('.demo-wrapper');

    if (boltTrigger && demoWrapper) {
        // Hover Effects
        boltTrigger.addEventListener('mouseenter', () => {
            demoWrapper.classList.add('split-active');
        });

        boltTrigger.addEventListener('mouseleave', () => {
            demoWrapper.classList.remove('split-active');
        });

        // Click Logic
        boltTrigger.addEventListener('click', () => {
            // 1. Trigger the Gravity Drop Animation on both layers
            const leftLayer = demoWrapper.querySelector('.layer-left');
            const rightLayer = demoWrapper.querySelector('.layer-right');

            if (leftLayer) leftLayer.classList.add('gravity-drop');
            if (rightLayer) rightLayer.classList.add('gravity-drop');

            // 2. Wait for animation to finish, then navigate
            setTimeout(() => {
                const demoUrl = boltTrigger.getAttribute('data-demo-url') || '/demo';
                window.location.href = demoUrl;
            }, 800); // Matches CSS animation duration (0.8s)
        });
    }
});

// Logout Function (Global)
function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = "/";
}

// Fetch Profile Function
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

            // Update UI Elements with smooth delay
            setTimeout(() => {
                const navbarInitial = document.getElementById('navbarUserInitial');
                const offcanvasInitial = document.getElementById('offcanvasUserInitial');
                const offcanvasName = document.getElementById('offcanvasUserName');
                const offcanvasEmail = document.getElementById('offcanvasUserEmail');

                // Update content
                if (navbarInitial) navbarInitial.innerText = initial;
                if (offcanvasInitial) offcanvasInitial.innerText = initial;

                if (offcanvasName) offcanvasName.innerText = name;
                if (offcanvasEmail) offcanvasEmail.innerText = data.email || "";
            }, 100);

            // Apply new badge style if requested (optional logic to swap class if needed)
            // For now, we update the existing elements content and they inherit current style
            // or we could add the class dynamically:
            // const avatar = document.querySelector('.avatar');
            // if(avatar) avatar.classList.add('user-avatar-badge');

        } else {
            console.warn("Failed to fetch profile:", response.status);
        }
    } catch (error) {
        console.error("Error fetching user profile:", error);
    }
}
