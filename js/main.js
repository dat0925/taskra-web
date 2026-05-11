const APP_URL = 'https://app.taskra.jp';

document.addEventListener('DOMContentLoaded', () => {
  // Login buttons
  document.querySelectorAll('[data-action="login"]').forEach(el => {
    el.addEventListener('click', () => {
      window.location.href = APP_URL;
    });
  });

  // Mobile menu
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  const mobileClose = document.getElementById('mobileClose');

  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
      mobileMenu.classList.add('open');
      document.body.style.overflow = 'hidden';
    });

    mobileClose.addEventListener('click', closeMobileMenu);

    mobileMenu.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', closeMobileMenu);
    });
  }

  function closeMobileMenu() {
    mobileMenu.classList.remove('open');
    document.body.style.overflow = '';
  }

  // Scroll animation
  const observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
  );

  document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
});
