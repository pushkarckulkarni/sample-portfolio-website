/* ==========================================================================
   SAMPLE PORTFOLIO — SITE JS
   Vanilla, no dependencies, no build step. ~7kb unminified.
   Every module is guarded: if its markup isn't on the page, it no-ops.
   ========================================================================== */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };


  /* ======================================================================
     1. HEADER — shadow on scroll + hide-on-scroll-down / show-on-scroll-up
     ====================================================================== */
  (function header() {
    var el = $('.site-header');
    if (!el) return;

    var last = window.pageYOffset;
    var threshold = 8;            // ignore sub-pixel jitter
    var hideAfter = 240;          // don't hide until past the fold-ish
    var ticking = false;

    function update() {
      var y = window.pageYOffset;
      el.classList.toggle('is-scrolled', y > 4);

      // Never hide while the mobile menu is open
      if (document.body.classList.contains('is-locked')) {
        el.classList.remove('is-hidden');
      } else if (Math.abs(y - last) > threshold) {
        el.classList.toggle('is-hidden', y > last && y > hideAfter);
        last = y;
      }
      ticking = false;
    }

    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; window.requestAnimationFrame(update); }
    }, { passive: true });

    update();
  })();


  /* ======================================================================
     2. MOBILE MENU
     Traps focus, locks body scroll, closes on Escape / link click / resize.
     ====================================================================== */
  (function mobileMenu() {
    var toggle = $('.nav-toggle');
    var menu   = $('.mobile-menu');
    if (!toggle || !menu) return;

    // Stagger index for the reveal animation
    $$('.mobile-menu__link', menu).forEach(function (l, i) {
      l.style.setProperty('--i', i);
    });

    function open() {
      menu.classList.add('is-open');
      toggle.classList.add('is-open');
      toggle.setAttribute('aria-expanded', 'true');
      document.body.classList.add('is-locked');
      var first = $('a, button', menu);
      if (first) setTimeout(function () { first.focus(); }, 200);
    }
    function close() {
      menu.classList.remove('is-open');
      toggle.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('is-locked');
    }
    function isOpen() { return menu.classList.contains('is-open'); }

    toggle.addEventListener('click', function () { isOpen() ? close() : open(); });

    menu.addEventListener('click', function (e) {
      if (e.target.closest('a')) close();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen()) { close(); toggle.focus(); }
      if (e.key === 'Tab' && isOpen()) {
        var f = $$('a, button', menu).filter(function (n) { return n.offsetParent; });
        if (!f.length) return;
        var first = f[0], lastF = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); lastF.focus(); }
        else if (!e.shiftKey && document.activeElement === lastF) { e.preventDefault(); first.focus(); }
      }
    });

    // Close if the viewport grows past the nav breakpoint
    var mq = window.matchMedia('(min-width: 900px)');
    function onMQ(e) { if (e.matches && isOpen()) close(); }
    if (mq.addEventListener) mq.addEventListener('change', onMQ);
    else if (mq.addListener) mq.addListener(onMQ);   // Safari < 14
  })();


  /* ======================================================================
     3. HERO SLIDER — crossfade, autoplay, dots, keyboard, swipe
     ====================================================================== */
  (function hero() {
    var root = $('.hero');
    if (!root) return;

    var slides = $$('.hero__slide', root);
    var dots   = $$('.hero__dot', root);
    if (slides.length < 2) return;

    var i = 0;
    var timer = null;
    var DELAY = parseInt(root.dataset.interval, 10) || 6000;

    function show(n) {
      i = (n + slides.length) % slides.length;
      slides.forEach(function (s, k) { s.classList.toggle('is-active', k === i); });
      dots.forEach(function (d, k) {
        d.classList.toggle('is-active', k === i);
        d.setAttribute('aria-current', k === i ? 'true' : 'false');
      });
    }
    function next() { show(i + 1); }
    function prev() { show(i - 1); }

    function play()  { if (!reduceMotion) { stop(); timer = setInterval(next, DELAY); } }
    function stop()  { if (timer) { clearInterval(timer); timer = null; } }
    function bump(fn) { fn(); play(); }   // restart the clock after manual input

    dots.forEach(function (d, k) { d.addEventListener('click', function () { bump(function(){show(k);}); }); });
    var pv = $('.hero__nav--prev', root), nx = $('.hero__nav--next', root);
    if (pv) pv.addEventListener('click', function () { bump(prev); });
    if (nx) nx.addEventListener('click', function () { bump(next); });

    // Keyboard when the hero has focus
    root.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') bump(next);
      if (e.key === 'ArrowLeft')  bump(prev);
    });

    // Touch swipe
    var x0 = null;
    root.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; stop(); }, { passive: true });
    root.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 45) (dx < 0 ? next : prev)();
      x0 = null; play();
    }, { passive: true });

    // Pause when off-screen or tab hidden — saves battery on mobile
    document.addEventListener('visibilitychange', function () {
      document.hidden ? stop() : play();
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        es[0].isIntersecting ? play() : stop();
      }, { threshold: 0.15 }).observe(root);
    }

    show(0);
    play();
  })();


  /* ======================================================================
     4. PROJECT FILTER — client-side category tabs, updates ?cat= in the URL
     Progressive enhancement: the tabs are real links, so this still works
     with JS off (server/static pages per category).
     ====================================================================== */
  (function filter() {
    var bar  = $('[data-filter-bar]');
    var grid = $('[data-filter-grid]');
    if (!bar || !grid) return;

    var cards = $$('.card', grid);

    function apply(cat, push) {
      cards.forEach(function (c) {
        var cats = (c.dataset.cats || '').split(/\s+/);
        c.classList.toggle('is-hidden', cat !== 'all' && cats.indexOf(cat) === -1);
      });
      $$('a', bar).forEach(function (a) {
        a.classList.toggle('is-active', (a.dataset.cat || 'all') === cat);
      });
      if (push && window.history.replaceState) {
        var q = cat === 'all' ? location.pathname : location.pathname + '?cat=' + cat;
        history.replaceState(null, '', q);
      }
      var n = cards.filter(function (c) { return !c.classList.contains('is-hidden'); }).length;
      var live = $('[data-filter-count]');
      if (live) live.textContent = n + (n === 1 ? ' project' : ' projects');
    }

    bar.addEventListener('click', function (e) {
      var a = e.target.closest('a[data-cat]');
      if (!a) return;
      e.preventDefault();
      apply(a.dataset.cat, true);
    });

    apply(new URLSearchParams(location.search).get('cat') || 'all', false);
  })();


  /* ======================================================================
     5. LIGHTBOX — for .figure__img and any [data-lightbox] image
     ====================================================================== */
  (function lightbox() {
    var imgs = $$('[data-lightbox]');
    if (!imgs.length) return;

    var box = document.createElement('div');
    box.className = 'lightbox';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', 'Image viewer');
    box.innerHTML =
      '<img class="lightbox__img" alt="">' +
      '<button class="lightbox__close" aria-label="Close">&times;</button>' +
      '<button class="lightbox__prev"  aria-label="Previous image">&#8249;</button>' +
      '<button class="lightbox__next"  aria-label="Next image">&#8250;</button>' +
      '<span class="lightbox__count"></span>';
    document.body.appendChild(box);

    var pic   = $('.lightbox__img', box);
    var count = $('.lightbox__count', box);
    var idx = 0, opener = null;

    function render() {
      var src = imgs[idx];
      pic.src = src.dataset.full || src.currentSrc || src.src;
      pic.alt = src.alt || '';
      count.textContent = (idx + 1) + ' / ' + imgs.length;
    }
    function open(n) {
      idx = n; opener = document.activeElement;
      render();
      box.classList.add('is-open');
      document.body.classList.add('is-locked');
      $('.lightbox__close', box).focus();
    }
    function close() {
      box.classList.remove('is-open');
      document.body.classList.remove('is-locked');
      if (opener) opener.focus();
    }
    function step(d) { idx = (idx + d + imgs.length) % imgs.length; render(); }

    imgs.forEach(function (im, n) {
      im.addEventListener('click', function () { open(n); });
      im.setAttribute('tabindex', '0');
      im.setAttribute('role', 'button');
      im.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(n); }
      });
    });

    $('.lightbox__close', box).addEventListener('click', close);
    $('.lightbox__prev',  box).addEventListener('click', function () { step(-1); });
    $('.lightbox__next',  box).addEventListener('click', function () { step(1); });
    box.addEventListener('click', function (e) { if (e.target === box) close(); });

    document.addEventListener('keydown', function (e) {
      if (!box.classList.contains('is-open')) return;
      if (e.key === 'Escape')     close();
      if (e.key === 'ArrowRight') step(1);
      if (e.key === 'ArrowLeft')  step(-1);
    });

    // Swipe on mobile
    var sx = null;
    box.addEventListener('touchstart', function (e) { sx = e.touches[0].clientX; }, { passive: true });
    box.addEventListener('touchend', function (e) {
      if (sx === null) return;
      var dx = e.changedTouches[0].clientX - sx;
      if (Math.abs(dx) > 45) step(dx < 0 ? 1 : -1);
      sx = null;
    }, { passive: true });
  })();


  /* ======================================================================
     6. SCROLL REVEAL
     ====================================================================== */
  (function reveal() {
    var els = $$('[data-reveal]');
    if (!els.length) return;
    if (!('IntersectionObserver' in window) || reduceMotion) {
      els.forEach(function (e) { e.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    els.forEach(function (e) { io.observe(e); });
  })();


  /* ======================================================================
     7. ABOUT — scroll-spy so the sub-nav highlights the section in view
     ====================================================================== */
  (function scrollSpy() {
    var links = $$('[data-spy] a[href^="#"]');
    if (!links.length || !('IntersectionObserver' in window)) return;

    var map = {};
    var targets = links.map(function (a) {
      var t = document.getElementById(a.getAttribute('href').slice(1));
      if (t) map[t.id] = a;
      return t;
    }).filter(Boolean);

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (a) { a.classList.remove('is-active'); });
        if (map[en.target.id]) map[en.target.id].classList.add('is-active');
      });
    }, { rootMargin: '-45% 0px -50% 0px' });

    targets.forEach(function (t) { io.observe(t); });
  })();


  /* ======================================================================
     8. BACK TO TOP
     ====================================================================== */
  (function toTop() {
    var btn = $('.to-top');
    if (!btn) return;
    var ticking = false;
    function upd() {
      btn.classList.toggle('is-visible', window.pageYOffset > window.innerHeight * 0.6);
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(upd); }
    }, { passive: true });
    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
    upd();
  })();


  /* ======================================================================
     9. LAZY IMAGE FADE
     ====================================================================== */
  (function lazyFade() {
    $$('img[loading="lazy"]').forEach(function (im) {
      if (im.complete) im.classList.add('is-loaded');
      else im.addEventListener('load', function () { im.classList.add('is-loaded'); });
    });
  })();


  /* ======================================================================
     10. LOAD MORE — reveals the next batch of hidden grid items
     ====================================================================== */
  (function loadMore() {
    var btn = $('[data-load-more]');
    if (!btn) return;
    var step = parseInt(btn.dataset.loadMore, 10) || 12;
    var grid = document.getElementById(btn.dataset.target);
    if (!grid) return;

    // Nothing batched yet? Disable so the control never lies about there
    // being more work. Add data-batch-hidden to cards past the first page
    // (and the matching CSS rule) when the real catalogue exceeds one page.
    function sync() {
      var n = $$('.card[data-batch-hidden]', grid).length;
      if (n === 0) btn.setAttribute('disabled', '');
      else btn.removeAttribute('disabled');
    }

    btn.addEventListener('click', function () {
      $$('.card[data-batch-hidden]', grid)
        .slice(0, step)
        .forEach(function (c) { c.removeAttribute('data-batch-hidden'); });
      sync();
    });

    sync();
  })();

})();
