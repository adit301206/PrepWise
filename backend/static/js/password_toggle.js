
/**
 * Toggles password visibility for the input field associated with the clicked icon.
 * Assumes the icon is a sibling of the input field or structured such that
 * we can find the input. Ideally, the icon is inside a .position-relative wrapper
 * along with the input.
 */

document.addEventListener('DOMContentLoaded', () => {
    const toggleIcons = document.querySelectorAll('.password-toggle-icon');

    toggleIcons.forEach(icon => {
        icon.addEventListener('click', function () {
            // Find the previous sibling input element
            // Since we are using position-relative wrapper, the input should be 
            // the previous element sibling or we search within the parent.
            const input = this.previousElementSibling;

            if (input && input.tagName === 'INPUT') {
                // Toggle the type attribute
                const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
                input.setAttribute('type', type);

                // Toggle the eye / eye-slash icon
                this.classList.toggle('fa-eye');
                this.classList.toggle('fa-eye-slash');
            }
        });
    });
});
