document.addEventListener('DOMContentLoaded', () => {

    // Smooth Scroll initialization (Lenis) - with safety check
    let lenis = null;
    if (typeof Lenis !== 'undefined') {
        try {
            lenis = new Lenis();
            function raf(time) {
                lenis.raf(time);
                requestAnimationFrame(raf);
            }
            requestAnimationFrame(raf);
        } catch (e) {
            console.warn('Lenis could not be initialized:', e);
        }
    } else {
        console.warn('Lenis is not loaded. Falling back to native scrolling.');
    }

    // Defined Tabs matching IDs in HTML
    const tabs = ['overview', 'design', 'analysis', 'project01', 'team', 'gallery', 'references'];

    const navLinks = document.querySelectorAll('.nav-links a');
    const initBtn = document.getElementById('init-system-btn');

    // Function to switch tabs
    function switchTab(targetId) {
        if (!tabs.includes(targetId)) return;

        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(el => {
            el.style.display = 'none';
            el.classList.remove('active-tab');
        });

        // Show target tab
        const target = document.getElementById(targetId);
        if (target) {
            target.style.display = 'block';
            target.classList.add('active-tab');

            // Scroll to top
            window.scrollTo(0, 0);

            // Trigger reveal animations for content in this tab
            setTimeout(() => {
                target.querySelectorAll('.reveal').forEach(el => {
                    // Start observing them or just add active if visible
                    observer.observe(el);
                });
            }, 100);
        }

        // Update Nav Active State
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${targetId}`) {
                link.classList.add('active');
            }
        });

        // Update Button State
        updateNavButtons(targetId);
    }

    // State to track current tab
    let activeTabId = 'overview';

    // Update Button State helper with Scroll Logic
    function updateNavButtons(currentId) {
        activeTabId = currentId; // Update global state

        const index = tabs.indexOf(currentId);
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const navControls = document.querySelector('.nav-controls');

        // Initial visibility check
        checkNavVisibility();

        if (prevBtn && nextBtn) {
            prevBtn.disabled = index <= 0;

            // On last tab (References), change Next button to Home
            if (index === tabs.length - 1) {
                nextBtn.textContent = "Home";
                nextBtn.disabled = false;
            } else {
                nextBtn.textContent = "Next";
                nextBtn.disabled = false;
            }
        }
    }

    // Function to check visibility based on Tab + Scroll
    function checkNavVisibility() {
        const navControls = document.querySelector('.nav-controls');
        if (!navControls) return;

        if (activeTabId === 'overview') {
            // If on Overview, check if Hero is visible
            const hero = document.getElementById('hero');
            if (hero) {
                const rect = hero.getBoundingClientRect();
                // If Hero bottom is roughly above the viewport top OR user has scrolled down significantly
                // Simple heuristic: if Hero takes up most of screen, hide buttons.
                // Better: If we are viewing Abstract, Hero is scrolled up.
                // Let's use the intersection observer result or a simple scroll check
                if (rect.bottom < window.innerHeight / 2) {
                    navControls.style.display = 'flex';
                } else {
                    navControls.style.display = 'none';
                }
            }
        } else {
            // Other tabs: always show
            navControls.style.display = 'flex';
        }
    }

    // Add Scroll Listener to toggle buttons on Overview
    window.addEventListener('scroll', () => {
        if (activeTabId === 'overview') {
            checkNavVisibility();
        }
    });

    // Initialize Default Tab
    switchTab('overview');

    // Nav Click Listeners
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            switchTab(targetId);
        });
    });

    // Next/Prev Button Listeners
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            const currentTab = document.querySelector('.active-tab');
            if (currentTab) {
                const currentIndex = tabs.indexOf(currentTab.id);
                if (currentIndex > 0) {
                    const newId = tabs[currentIndex - 1];
                    switchTab(newId);
                }
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            const currentTab = document.querySelector('.active-tab');
            if (currentTab) {
                const currentIndex = tabs.indexOf(currentTab.id);
                if (currentIndex < tabs.length - 1) {
                    // Normal Next behavior
                    const newId = tabs[currentIndex + 1];
                    switchTab(newId);
                } else {
                    // Start Over behavior (Last Tab -> First Tab)
                    switchTab(tabs[0]);
                }
            }
        });
    }

    // Initialize System Button Listener
    if (initBtn) {
        initBtn.addEventListener('click', () => {
            // Check if we are on Overview tab (we should be), if not switch
            const overviewTab = document.getElementById('overview');
            if (overviewTab.style.display === 'none') {
                switchTab('overview');
            }

            // Scroll to Abstract
            if (lenis) {
                lenis.scrollTo('#abstract-content', { offset: 0, duration: 2 });
            } else {
                const abstractSection = document.getElementById('abstract-content');
                if (abstractSection) {
                    abstractSection.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    }

    // Intersection Observer for Reveal Animations
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, observerOptions);

    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

});
