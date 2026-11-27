(function () {
  var root = document.documentElement;

  // Theme toggle (dark/light), persisted
  document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem('n2-theme', next); } catch (e) {}
    });
  });

  // Mobile nav
  var nav = document.querySelector('.nav'), toggle = document.querySelector('.nav-toggle');
  if (nav && toggle) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.querySelectorAll('.nav-links a').forEach(function (a) {
      a.addEventListener('click', function () { nav.classList.remove('nav-open'); });
    });
  }

  // Portfolio filter
  var chips = document.querySelectorAll('button[data-filter]');
  var cards = document.querySelectorAll('.card[data-category]');
  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      var f = chip.dataset.filter;
      chips.forEach(function (c) { c.classList.toggle('active', c === chip); });
      cards.forEach(function (card) { card.hidden = !(f === 'all' || card.dataset.category === f); });
    });
  });

  // FAQ: one open at a time
  var items = document.querySelectorAll('.faq details');
  items.forEach(function (d) {
    d.addEventListener('toggle', function () {
      if (d.open) items.forEach(function (o) { if (o !== d) o.open = false; });
    });
  });

  // Dismiss messages; auto-hide success after a while
  document.querySelectorAll('.msg-x').forEach(function (b) {
    b.addEventListener('click', function () { b.closest('.msg').remove(); });
  });
  setTimeout(function () {
    document.querySelectorAll('.msg-success').forEach(function (m) { m.remove(); });
  }, 8000);

  // Subtle scroll reveal
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.12 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('in'); });
  }

  // Icons
  if (window.lucide) window.lucide.createIcons();
})();
