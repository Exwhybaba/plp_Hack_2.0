document.addEventListener("DOMContentLoaded", function () {
  const section = document.querySelector(".section-1");

  const images = [
    "static/img/brown-chickens-farm.jpg",
    "static/img/b-cole-tZDQqzD3EqI-unsplash.jpg",
    "static/img/muhammad-qasim-ali-NddUYwQ_7xI-unsplash.jpg",
    "static/img/tattooed-roaster-hand-holds-metal-scoop-with-raw-fresh-green-coffee-beans-plastic-basket.jpg",
  ];

  // Preload images (good practice)
  images.forEach(src => {
    const img = new Image();
    img.src = src;
  });

  // Create two layer divs for crossfade
  const layerA = document.createElement("div");
  const layerB = document.createElement("div");
  layerA.className = "slide-layer visible";
  layerB.className = "slide-layer";
  // start with first image visible
  layerA.style.backgroundImage = `url('${images[0]}')`;
  section.appendChild(layerA);
  section.appendChild(layerB);

  let index = 0;
  let topIsA = true;
  const duration = 3000; // ms between slides

  setInterval(() => {
    const nextIndex = (index + 1) % images.length;
    const top = topIsA ? layerA : layerB;
    const bottom = topIsA ? layerB : layerA;

    // put next image on the bottom (currently hidden) layer
    bottom.style.backgroundImage = `url('${images[nextIndex]}')`;

    // force a reflow in some browsers to ensure transition runs
    // eslint-disable-next-line no-unused-expressions
    bottom.offsetHeight;

    // fade bottom in, fade top out
    bottom.classList.add("visible");
    top.classList.remove("visible");

    // flip the "top" pointer after the transition
    topIsA = !topIsA;
    index = nextIndex;
  }, duration);
});



// script.js - single clean modal + signup handler (client validation)
// Put this file in your project and make sure index.html loads it once at the end.

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const loginBtn = document.querySelector('.login-btn');
  const signupBtn = document.querySelector('.signup-btn');
  const loginModal = document.getElementById('login-modal');
  const signupModal = document.getElementById('signup-modal');
  const closeButtons = document.querySelectorAll('.modal .close');

  // Helpers
  function openModal(modal) {
    if (!modal) return;
    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');
    const input = modal.querySelector('input');
    if (input) input.focus();
  }
  function closeModal(modal) {
    if (!modal) return;
    modal.style.display = 'none';
    modal.setAttribute('aria-hidden', 'true');
  }

  // Wire open buttons (guard in case element missing)
  if (loginBtn && loginModal) {
    loginBtn.addEventListener('click', (e) => {
      e.preventDefault();
      openModal(loginModal);
    });
  }
  if (signupBtn && signupModal) {
    signupBtn.addEventListener('click', (e) => {
      e.preventDefault();
      openModal(signupModal);
    });
  }

  // Wire close buttons
  closeButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const modal = e.target.closest('.modal');
      closeModal(modal);
    });
  });

  // Click outside to close
  window.addEventListener('click', (e) => {
    if (e.target && e.target.classList && e.target.classList.contains('modal')) {
      closeModal(e.target);
    }
  });

  // ESC key closes open modal
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      [loginModal, signupModal].forEach(m => {
        if (m && m.style.display === 'flex') closeModal(m);
      });
    }
  });

  // Signup form validation and optional AJAX submit
  const signupForm = document.getElementById('signup-form');
  if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
      // client-side check (password match)
      const pw = signupForm.querySelector('[name="password"]').value;
      const cpw = signupForm.querySelector('[name="confirm_password"]').value;
      if (pw !== cpw) {
        e.preventDefault();
        alert('Passwords do not match — please check and try again.');
        signupForm.querySelector('[name="password"]').focus();
        return;
      }

      // ---- NORMAL SUBMIT (recommended for beginners) ----
      // If you have a server route at /signup this will POST the form normally.
      // If you want AJAX instead (no reload), uncomment the block below.

      /*
      e.preventDefault();
      const fd = new FormData(signupForm);
      const payload = Object.fromEntries(fd.entries());
      try {
        const resp = await fetch(signupForm.action || '/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const json = await resp.json();
        if (resp.ok) {
          alert(json.message || 'Signup successful');
          signupForm.reset();
          closeModal(signupModal);
        } else {
          alert(json.error || 'Signup failed. Check inputs or try a different username/email.');
        }
      } catch (err) {
        console.error(err);
        alert('Network/server error. See console for details.');
      }
      */
    });
  }
});
// End of script.js

// Mobile menu toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            
            // Change icon based on menu state
            const icon = menuToggle.querySelector('i');
            if (navMenu.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
        
        // Close menu when clicking on a link
        const navLinks = navMenu.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                const icon = menuToggle.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!event.target.closest('.navbar') && navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
                const icon = menuToggle.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }
});