/**
 * AgriSmart AI — Frosted Floating Navigation & Responsive Menu Controller
 * =========================================================================
 * Features:
 *  - Translucent floating navbar with dynamic elevation on scroll.
 *  - Smooth sliding pill active/hover indicator on navbar items.
 *  - IntersectionObserver & scroll-spy for single-page sections.
 *  - Responsive mobile drawer with frosted backdrop blur and hamburger icon morph.
 *  - Mobile sidebar drawer management with backdrop overlay.
 */

(function () {
  'use strict';

  if (window.__AgriSmartNavInitialized) return;
  window.__AgriSmartNavInitialized = true;

  function initNavigation() {
    const navbar = document.querySelector('.glass-navbar');
    if (!navbar) return;

    const sidebar = document.querySelector('.glass-sidebar');
    let sidebarOverlay = document.querySelector('.sidebar-overlay');

    // ── 1. Scroll Elevation State ─────────────────────────────────────
    function updateScrollState() {
      if (window.scrollY > 15) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    }
    window.addEventListener('scroll', updateScrollState, { passive: true });
    updateScrollState();

    // ── 2. Smooth Sliding Active Indicator ────────────────────────────
    const navLists = document.querySelectorAll('.navbar-nav');
    navLists.forEach((navList) => {
      // Ensure sliding pill exists
      let pill = navList.querySelector('.nav-sliding-pill');
      if (!pill) {
        pill = document.createElement('div');
        pill.className = 'nav-sliding-pill';
        navList.prepend(pill);
      }

      function updatePillPosition(targetLink) {
        if (!targetLink) {
          // Find currently active link
          const activeItem = navList.querySelector('.navbar-nav-item.active a, .navbar-nav-item a.active');
          if (activeItem && activeItem.offsetParent !== null) {
            targetLink = activeItem;
          } else {
            pill.style.opacity = '0';
            return;
          }
        }

        const navRect = navList.getBoundingClientRect();
        const linkRect = targetLink.getBoundingClientRect();

        const left = linkRect.left - navRect.left;
        const width = linkRect.width;

        pill.style.left = `${left}px`;
        pill.style.width = `${width}px`;
        pill.style.opacity = '1';
      }

      const links = navList.querySelectorAll('.navbar-nav-item a, .navbar-nav-item button');
      links.forEach((link) => {
        link.addEventListener('mouseenter', () => updatePillPosition(link));
        link.addEventListener('focus', () => updatePillPosition(link));
      });

      navList.addEventListener('mouseleave', () => updatePillPosition(null));

      // Initial position
      setTimeout(() => updatePillPosition(null), 100);
      window.addEventListener('resize', () => updatePillPosition(null));
    });

    // ── 3. Single-Page ScrollSpy & Section Navigation ─────────────────
    const sectionLinks = Array.from(document.querySelectorAll('.navbar-nav a[href^="#"]'));
    const sections = sectionLinks
      .map((link) => {
        const id = link.getAttribute('href').substring(1);
        const el = document.getElementById(id);
        return el ? { id, el, link } : null;
      })
      .filter(Boolean);

    function highlightActiveSection() {
      if (sections.length === 0) return;

      const scrollPos = window.scrollY + 140; // Offset for floating navbar
      let currentSection = null;

      for (let i = 0; i < sections.length; i++) {
        const item = sections[i];
        const top = item.el.offsetTop;
        const height = item.el.offsetHeight;

        if (scrollPos >= top && scrollPos < top + height) {
          currentSection = item;
          break;
        }
      }

      // If at bottom of page, activate last section
      if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 50) {
        currentSection = sections[sections.length - 1];
      }

      if (currentSection) {
        sections.forEach((s) => {
          const parent = s.link.closest('.navbar-nav-item');
          if (s === currentSection) {
            if (parent) parent.classList.add('active');
            s.link.classList.add('active');
          } else {
            if (parent) parent.classList.remove('active');
            s.link.classList.remove('active');
          }
        });

        navLists.forEach((navList) => {
          const pill = navList.querySelector('.nav-sliding-pill');
          if (pill) {
            const activeItem = navList.querySelector('.navbar-nav-item.active a');
            if (activeItem) {
              const navRect = navList.getBoundingClientRect();
              const linkRect = activeItem.getBoundingClientRect();
              pill.style.left = `${linkRect.left - navRect.left}px`;
              pill.style.width = `${linkRect.width}px`;
              pill.style.opacity = '1';
            }
          }
        });
      }
    }

    if (sections.length > 0) {
      window.addEventListener('scroll', highlightActiveSection, { passive: true });
      highlightActiveSection();
    }

    // ── 4. Responsive Mobile Navigation Drawer ────────────────────────
    let toggleBtn = navbar.querySelector('.navbar-toggle');
    if (!toggleBtn) {
      toggleBtn = document.createElement('button');
      toggleBtn.className = 'navbar-toggle';
      toggleBtn.setAttribute('aria-label', 'Toggle Navigation Menu');
      toggleBtn.innerHTML = `
        <div class="navbar-toggle-icon">
          <span></span>
          <span></span>
          <span></span>
        </div>
      `;
      navbar.appendChild(toggleBtn);
    }

    const desktopNavLinks = navbar.querySelectorAll('.navbar-nav a');
    let mobileDrawer = document.querySelector('.mobile-nav-drawer');
    let mobileBackdrop = document.querySelector('.mobile-nav-backdrop');

    if (!mobileDrawer && desktopNavLinks.length > 0) {
      mobileDrawer = document.createElement('div');
      mobileDrawer.className = 'mobile-nav-drawer';

      // Clone links from desktop navbar
      desktopNavLinks.forEach((link) => {
        const mobileLink = document.createElement('a');
        mobileLink.href = link.getAttribute('href');
        mobileLink.className = 'mobile-nav-link';
        mobileLink.innerHTML = link.innerHTML;
        if (link.classList.contains('active') || link.closest('.navbar-nav-item.active')) {
          mobileLink.classList.add('active');
        }
        mobileDrawer.appendChild(mobileLink);
      });

      // Actions / Auth buttons
      const actionGroup = navbar.querySelector('.flex.items-center.gap-3, .flex.items-center.gap-4');
      if (actionGroup) {
        const divider = document.createElement('div');
        divider.className = 'mobile-nav-divider';
        mobileDrawer.appendChild(divider);

        const clonedActions = actionGroup.cloneNode(true);
        clonedActions.className = 'flex flex-col gap-2 mt-1';
        mobileDrawer.appendChild(clonedActions);
      }

      document.body.appendChild(mobileDrawer);
    }

    if (!mobileBackdrop) {
      mobileBackdrop = document.createElement('div');
      mobileBackdrop.className = 'mobile-nav-backdrop';
      document.body.appendChild(mobileBackdrop);
    }

    function toggleMobileMenu(forceState) {
      // Case 1: Page has sidebar and no top navbar items (e.g. Dashboard)
      if (sidebar && desktopNavLinks.length === 0) {
        const isSidebarOpen = typeof forceState === 'boolean' ? forceState : !sidebar.classList.contains('open');
        if (isSidebarOpen) {
          toggleBtn.classList.add('active');
          sidebar.classList.add('open');
          if (sidebarOverlay) sidebarOverlay.classList.add('active');
        } else {
          toggleBtn.classList.remove('active');
          sidebar.classList.remove('open');
          if (sidebarOverlay) sidebarOverlay.classList.remove('active');
        }
        return;
      }

      // Case 2: Page with navbar links (e.g. Landing Page)
      if (mobileDrawer) {
        const isOpen = typeof forceState === 'boolean' ? forceState : !mobileDrawer.classList.contains('active');
        if (isOpen) {
          toggleBtn.classList.add('active');
          mobileDrawer.classList.add('active');
          mobileBackdrop.classList.add('active');
          document.body.style.overflow = 'hidden';
        } else {
          toggleBtn.classList.remove('active');
          mobileDrawer.classList.remove('active');
          mobileBackdrop.classList.remove('active');
          document.body.style.overflow = '';
        }
      }
    }

    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleMobileMenu();
    });

    mobileBackdrop.addEventListener('click', () => toggleMobileMenu(false));

    // Close on navigation click
    if (mobileDrawer) {
      mobileDrawer.querySelectorAll('a, button').forEach((el) => {
        el.addEventListener('click', () => {
          setTimeout(() => toggleMobileMenu(false), 120);
        });
      });
    }

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        toggleMobileMenu(false);
      }
    });

    // ── 5. Mobile Sidebar Management ──────────────────────────────────
    if (sidebar) {
      if (!sidebarOverlay) {
        sidebarOverlay = document.createElement('div');
        sidebarOverlay.className = 'sidebar-overlay';
        document.body.appendChild(sidebarOverlay);
      }

      sidebarOverlay.addEventListener('click', () => {
        toggleMobileMenu(false);
      });

      // Sync sidebar links to close on click in mobile
      sidebar.querySelectorAll('.sidebar-nav-item').forEach((item) => {
        item.addEventListener('click', () => {
          if (window.innerWidth < 768) {
            toggleMobileMenu(false);
          }
        });
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavigation);
  } else {
    initNavigation();
  }
})();
