document.addEventListener('DOMContentLoaded', () => {

    // Scroll Reveal Animation
    const revealElements = document.querySelectorAll('.reveal');

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                // Optional: Stop observing once revealed
                // observer.unobserve(entry.target);
            }
        });
    }, {
        root: null,
        threshold: 0.15, // Trigger when 15% of the element is visible
        rootMargin: "0px"
    });

    revealElements.forEach(el => revealObserver.observe(el));

    const navLinks = document.querySelectorAll('.nav-links a');
    const sections = document.querySelectorAll('section, header#hero');

    function switchTab(targetId) {
        // Hide all sections
        sections.forEach(section => {
            section.classList.remove('active-section');
        });

        // Deactivate all links
        navLinks.forEach(link => {
            link.classList.remove('active');
        });

        // Show target section
        const targetSection = document.querySelector(targetId);
        if (targetSection) {
            targetSection.classList.add('active-section');
        }

        // Activate target link
        const targetLink = document.querySelector(`.nav-links a[href="${targetId}"]`);
        if (targetLink) {
            targetLink.classList.add('active');
        }

        // Special case: If target is #hero (Home), activate the Home link (if we add one)
        // or just ensure the logo click works.
    }

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            switchTab(targetId);
        });
    });

    // Handle Logo Click -> Go to Home (#hero)
    const logo = document.querySelector('.logo');
    if (logo) {
        logo.style.cursor = 'pointer';
        logo.addEventListener('click', () => {
            switchTab('#hero');
        });
    }

    // Initialize: Check hash or default to #hero
    const initialHash = window.location.hash;
    if (initialHash && document.querySelector(initialHash)) {
        switchTab(initialHash);
    } else {
        switchTab('#hero');
    }

    // Trigger animations for elements inside the active section
    // We can just add 'active' to .reveal elements in the active section
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.target.classList.contains('active-section')) {
                const reveals = mutation.target.querySelectorAll('.reveal');
                reveals.forEach((reveal, index) => {
                    setTimeout(() => {
                        reveal.classList.add('active');
                    }, index * 100);
                });
            }
        });
    });

    sections.forEach(section => {
        observer.observe(section, { attributes: true, attributeFilter: ['class'] });
    });

    // Navbar Background on Scroll (Optional for tabs, but good for polish)
    const nav = document.querySelector('nav');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.style.background = 'rgba(5, 5, 5, 0.95)';
            nav.style.boxShadow = '0 2px 10px rgba(0,0,0,0.5)';
        } else {
            nav.style.background = 'rgba(5, 5, 5, 0.7)';
            nav.style.boxShadow = 'none';
        }
    });

});
