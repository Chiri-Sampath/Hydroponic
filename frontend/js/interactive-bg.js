/**
 * AgriSmart AI — Ambient Arctic Light & Luminous Atmosphere
 * ======================================================================================
 * Renders a serene, elegant, fluid ambient light field matching the Clean Arctic Glass design.
 * Features:
 *  - Soft, large floating luminous light orbs (pure white, soft ice blue, arctic azure).
 *  - Smooth radial gradient diffusions creating a tranquil, non-disturbing glow.
 *  - Interactive cursor light aura that smoothly responds to mouse and touch movement.
 *  - Gentle translucent water/light ripples on tap or click.
 *  - 100% free of distracting geometric lines, constellation webs, or dark dots.
 *  - GPU-accelerated requestAnimationFrame with tab visibility auto-pause.
 */

(function () {
  'use strict';

  // Prevent multiple initializations
  if (window.__AgriSmartBgInitialized) return;
  window.__AgriSmartBgInitialized = true;

  function initInteractiveBackground() {
    // Check if canvas already exists
    let canvas = document.getElementById('interactive-ambient-canvas');
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.id = 'interactive-ambient-canvas';
      canvas.style.position = 'fixed';
      canvas.style.top = '0';
      canvas.style.left = '0';
      canvas.style.width = '100vw';
      canvas.style.height = '100vh';
      canvas.style.pointerEvents = 'none';
      canvas.style.zIndex = '-2';
      canvas.style.opacity = '0.95';
      document.body.prepend(canvas);
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = 0;
    let height = 0;
    let dpr = Math.min(window.devicePixelRatio || 1, 2);
    let animationFrameId = null;
    let isTabActive = true;

    // Mouse & Touch Tracking State
    const mouse = {
      x: -1000,
      y: -1000,
      currentX: -1000,
      currentY: -1000,
      radius: 220,
      active: false,
    };

    // Click / Tap Luminous Ripple Pool
    const ripples = [];

    function addRipple(x, y) {
      ripples.push({
        x: x,
        y: y,
        radius: 10,
        maxRadius: 240,
        opacity: 0.6,
        speed: 3.2,
      });
    }

    // Soft Ambient Luminous Light Orbs
    const orbPalette = [
      { r: 255, g: 255, b: 255, baseAlpha: 0.28 }, // Pure Glacier White Glow
      { r: 225, g: 240, b: 255, baseAlpha: 0.24 }, // Ice White
      { r: 180, g: 215, b: 250, baseAlpha: 0.20 }, // Pale Arctic Periwinkle
      { r: 130, g: 185, b: 240, baseAlpha: 0.16 }, // Soft Azure
      { r: 240, g: 248, b: 255, baseAlpha: 0.22 }, // Light Frost
    ];

    let orbs = [];

    class LuminousOrb {
      constructor(index) {
        this.index = index;
        this.reset(true);
      }

      reset(init = false) {
        this.x = init ? Math.random() * width : (Math.random() > 0.5 ? -150 : width + 150);
        this.y = init ? Math.random() * height : Math.random() * height;
        this.radius = Math.random() * 160 + 140; // 140px to 300px soft radial radius
        this.palette = orbPalette[this.index % orbPalette.length];
        
        // Very slow, soothing drift
        const speed = Math.random() * 0.25 + 0.12;
        const angle = Math.random() * Math.PI * 2;
        this.vx = Math.cos(angle) * speed;
        this.vy = Math.sin(angle) * speed;

        // Subtle breathing effect
        this.pulseAngle = Math.random() * Math.PI * 2;
        this.pulseSpeed = Math.random() * 0.008 + 0.004;
        this.currentAlpha = this.palette.baseAlpha;
      }

      update() {
        this.pulseAngle += this.pulseSpeed;
        const pulse = Math.sin(this.pulseAngle);
        this.currentRadius = this.radius + pulse * 25;
        this.currentAlpha = Math.max(0.04, this.palette.baseAlpha + pulse * 0.06);

        // Smooth base movement
        this.x += this.vx;
        this.y += this.vy;

        // Boundary wrap
        if (this.x < -this.radius * 1.5) this.x = width + this.radius * 1.5;
        if (this.x > width + this.radius * 1.5) this.x = -this.radius * 1.5;
        if (this.y < -this.radius * 1.5) this.y = height + this.radius * 1.5;
        if (this.y > height + this.radius * 1.5) this.y = -this.radius * 1.5;

        // Gentle interactive mouse drift
        if (mouse.active) {
          const dx = this.x - mouse.currentX;
          const dy = this.y - mouse.currentY;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < mouse.radius + this.currentRadius && dist > 0) {
            const force = (1 - dist / (mouse.radius + this.currentRadius)) * 0.8;
            const angle = Math.atan2(dy, dx);
            this.x += Math.cos(angle) * force;
            this.y += Math.sin(angle) * force;
          }
        }
      }

      draw() {
        const gradient = ctx.createRadialGradient(
          this.x, this.y, 0,
          this.x, this.y, this.currentRadius
        );
        const { r, g, b } = this.palette;
        gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${this.currentAlpha})`);
        gradient.addColorStop(0.5, `rgba(${r}, ${g}, ${b}, ${this.currentAlpha * 0.45})`);
        gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);

        ctx.beginPath();
        ctx.arc(this.x, this.y, this.currentRadius, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
      }
    }

    function resize() {
      width = window.innerWidth;
      height = window.innerHeight;
      dpr = Math.min(window.devicePixelRatio || 1, 2);

      canvas.width = width * dpr;
      canvas.height = height * dpr;
      ctx.scale(dpr, dpr);

      // Spawn 8 to 12 gentle floating luminous orbs
      const count = window.innerWidth < 768 ? 6 : 9;
      orbs = [];
      for (let i = 0; i < count; i++) {
        orbs.push(new LuminousOrb(i));
      }
    }

    // Draw Smooth Cursor Light Aura
    function drawMouseLight() {
      if (!mouse.active || mouse.currentX < -500) return;

      // Smooth lerp mouse position
      mouse.currentX += (mouse.x - mouse.currentX) * 0.12;
      mouse.currentY += (mouse.y - mouse.currentY) * 0.12;

      const gradient = ctx.createRadialGradient(
        mouse.currentX, mouse.currentY, 0,
        mouse.currentX, mouse.currentY, mouse.radius
      );
      gradient.addColorStop(0, 'rgba(255, 255, 255, 0.28)');
      gradient.addColorStop(0.35, 'rgba(200, 230, 255, 0.18)');
      gradient.addColorStop(0.7, 'rgba(140, 195, 250, 0.08)');
      gradient.addColorStop(1, 'rgba(240, 246, 255, 0)');

      ctx.beginPath();
      ctx.arc(mouse.currentX, mouse.currentY, mouse.radius, 0, Math.PI * 2);
      ctx.fillStyle = gradient;
      ctx.fill();
    }

    // Draw and update active soft ripples
    function updateAndDrawRipples() {
      for (let i = ripples.length - 1; i >= 0; i--) {
        const r = ripples[i];
        r.radius += r.speed;
        r.opacity -= 0.012;

        if (r.opacity <= 0 || r.radius >= r.maxRadius) {
          ripples.splice(i, 1);
          continue;
        }

        const gradient = ctx.createRadialGradient(
          r.x, r.y, Math.max(0, r.radius - 30),
          r.x, r.y, r.radius
        );
        gradient.addColorStop(0, `rgba(255, 255, 255, 0)`);
        gradient.addColorStop(0.7, `rgba(255, 255, 255, ${r.opacity * 0.4})`);
        gradient.addColorStop(1, `rgba(180, 220, 255, ${r.opacity * 0.2})`);

        ctx.beginPath();
        ctx.arc(r.x, r.y, r.radius, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(255, 255, 255, ${r.opacity * 0.5})`;
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    }

    // Animation Loop
    function render() {
      if (!isTabActive) {
        animationFrameId = requestAnimationFrame(render);
        return;
      }

      ctx.clearRect(0, 0, width, height);

      // Render tranquil ambient luminous orbs
      for (let i = 0; i < orbs.length; i++) {
        orbs[i].update();
        orbs[i].draw();
      }

      // Render interactive cursor light
      drawMouseLight();

      // Render gentle water/light ripples
      updateAndDrawRipples();

      animationFrameId = requestAnimationFrame(render);
    }

    // Event Listeners
    let resizeTimer = null;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(resize, 150);
    });

    window.addEventListener('mousemove', (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
      if (!mouse.active) {
        mouse.currentX = e.clientX;
        mouse.currentY = e.clientY;
      }
      mouse.active = true;
    });

    window.addEventListener('mouseleave', () => {
      mouse.active = false;
    });

    window.addEventListener('click', (e) => {
      addRipple(e.clientX, e.clientY);
    });

    // Touch support for mobile / tablets
    window.addEventListener('touchmove', (e) => {
      if (e.touches.length > 0) {
        mouse.x = e.touches[0].clientX;
        mouse.y = e.touches[0].clientY;
        if (!mouse.active) {
          mouse.currentX = mouse.x;
          mouse.currentY = mouse.y;
        }
        mouse.active = true;
      }
    }, { passive: true });

    window.addEventListener('touchend', () => {
      mouse.active = false;
    });

    window.addEventListener('touchstart', (e) => {
      if (e.touches.length > 0) {
        mouse.x = e.touches[0].clientX;
        mouse.y = e.touches[0].clientY;
        mouse.currentX = mouse.x;
        mouse.currentY = mouse.y;
        mouse.active = true;
        addRipple(e.touches[0].clientX, e.touches[0].clientY);
      }
    }, { passive: true });

    // Handle Tab Visibility (save CPU/battery)
    document.addEventListener('visibilitychange', () => {
      isTabActive = !document.hidden;
    });

    // Initialize
    resize();
    render();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initInteractiveBackground);
  } else {
    initInteractiveBackground();
  }
})();
