/* ============================================
   ParfumAI — Coordinated Animation Engine
   Copyright (c) 2026 Ahmet Rıfai Kuyucu
   Tüm Hakları Saklıdır — All Rights Reserved.
   ============================================ */

const ParfumAnim = {
    // Configuration
    config: {
        revealThreshold: 0.12,
        staggerBaseDelay: 80,
        entryStaggerDelay: 100,
    },

    init: function() {
        this.initTooltips();
        this.initEntrySequence();
        this.initScrollReveal();
        this.initResultCards();
        this.initCounters();
        this.initNavbarActive();
    },

    // Bootstrap tooltips
    initTooltips: function() {
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function(el) {
            new bootstrap.Tooltip(el);
        });
    },

    // Coordinated entry animation: elements with .entry class animate in sequence
    initEntrySequence: function() {
        var entries = document.querySelectorAll('.entry');
        if (entries.length === 0) return;

        entries.forEach(function(el, i) {
            var delay = i * ParfumAnim.config.entryStaggerDelay;
            setTimeout(function() {
                el.classList.add('entered');
            }, delay + 100); // +100ms base for DOM settle
        });
    },

    // Scroll reveal: elements with .reveal class animate when visible
    initScrollReveal: function() {
        var revealEls = document.querySelectorAll('.reveal');
        if (revealEls.length === 0 || !('IntersectionObserver' in window)) return;

        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting && !entry.target.classList.contains('revealed')) {
                    entry.target.classList.add('revealed');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: ParfumAnim.config.revealThreshold,
            rootMargin: '0px 0px -40px 0px'
        });

        revealEls.forEach(function(el) { observer.observe(el); });
    },

    // Result cards: stagger with JS delays
    initResultCards: function() {
        var containers = document.querySelectorAll('.perfume-stagger');
        if (containers.length === 0) return;

        containers.forEach(function(container) {
            var cards = container.querySelectorAll('.result-card');
            if (cards.length === 0) return;

            // Observe the container, not individual cards
            if ('IntersectionObserver' in window) {
                var obs = new IntersectionObserver(function(entries) {
                    entries.forEach(function(entry) {
                        if (entry.isIntersecting) {
                            ParfumAnim.staggerCards(cards);
                            obs.unobserve(entry.target);
                        }
                    });
                }, { threshold: 0.1 });
                obs.observe(container);
            } else {
                // Fallback: show immediately
                cards.forEach(function(c) { c.classList.add('entered'); });
            }
        });
    },

    staggerCards: function(cards) {
        cards.forEach(function(card, i) {
            var delay = (i + 1) * 120;
            setTimeout(function() {
                card.classList.add('entered');
            }, delay);
        });
    },

    // Counters with ease-out animation
    initCounters: function() {
        var counters = document.querySelectorAll('[data-count]');
        if (counters.length === 0) return;

        if ('IntersectionObserver' in window) {
            var obs = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        ParfumAnim.animateCounter(entry.target);
                        obs.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });
            counters.forEach(function(c) { obs.observe(c); });
        } else {
            counters.forEach(function(c) { ParfumAnim.animateCounter(c); });
        }
    },

    animateCounter: function(el) {
        var target = parseInt(el.getAttribute('data-count'));
        if (isNaN(target)) return;
        var duration = 1200;
        var startTime = performance.now();

        function update(now) {
            var elapsed = now - startTime;
            var progress = Math.min(elapsed / duration, 1);
            // easeOutQuart
            var eased = 1 - Math.pow(1 - progress, 4);
            var current = Math.round(eased * target);
            el.textContent = current.toLocaleString('tr-TR');
            if (progress < 1) requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
    },

    // Navbar active state
    initNavbarActive: function() {
        var path = window.location.pathname;
        document.querySelectorAll('.navbar-neon .nav-link').forEach(function(link) {
            var href = link.getAttribute('href');
            if (href === path && path !== '/') {
                link.classList.add('active');
            }
        });
    }
};

// Bootstrap on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    ParfumAnim.init();
});

// Global notification helper
function showNotification(message, type) {
    var colors = {
        info: 'bg-primary',
        success: 'bg-success',
        warning: 'bg-warning text-dark',
        error: 'bg-danger'
    };

    var toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white ' + (colors[type] || 'bg-primary') + ' border-0 position-fixed';
    toast.style.cssText = 'bottom: 20px; right: 20px; z-index: 9999; min-width: 250px;';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = '<div class="d-flex"><div class="toast-body">' + message + '</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>';

    document.body.appendChild(toast);
    var bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    setTimeout(function() { toast.remove(); }, 3000);
}
