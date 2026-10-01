/**
 * AgriSmart AI — Auth & Route Guard Helper
 * =========================================
 * Manages client-side authentication state, protects private pages,
 * handles logout, and provides user context to frontend templates.
 */

const AuthGuard = (() => {
  /**
   * Protect a page by role.
   * If not logged in, redirects to login page.
   * If role is not allowed, redirects to appropriate dashboard or error.
   * @param {Array<string>} allowedRoles e.g. ['general_user', 'admin']
   */
  const requireAuth = (allowedRoles = ['general_user', 'buyer', 'admin']) => {
    const path = window.location.pathname;
    let targetLogin = 'login.html';
    let targetUserDash = 'dashboard.html';
    let targetAdminDash = '../admin/dashboard.html';
    let targetBuyerDash = '../buyer/dashboard.html';

    if (path.includes('/pages/admin/')) {
      targetLogin = '../user/login.html';
      targetUserDash = '../user/dashboard.html';
      targetAdminDash = 'dashboard.html';
      targetBuyerDash = '../buyer/dashboard.html';
    } else if (path.includes('/pages/buyer/')) {
      targetLogin = '../user/login.html';
      targetUserDash = '../user/dashboard.html';
      targetAdminDash = '../admin/dashboard.html';
      targetBuyerDash = 'dashboard.html';
    } else if (!path.includes('/pages/user/')) {
      targetLogin = 'pages/user/login.html';
      targetUserDash = 'pages/user/dashboard.html';
      targetAdminDash = 'pages/admin/dashboard.html';
      targetBuyerDash = 'pages/buyer/dashboard.html';
    }

    if (!AgriAPI.isLoggedIn()) {
      const currentPath = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.href = `${targetLogin}?next=${currentPath}`;
      return false;
    }

    const user = AgriAPI.getCurrentUser();
    if (!user) {
      AgriAPI.logout();
      return false;
    }

    if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
      alert(`Access denied. Your role (${user.role}) is not authorized to view this page.`);
      if (user.role === 'admin') {
        window.location.href = targetAdminDash;
      } else if (user.role === 'buyer') {
        window.location.href = targetBuyerDash;
      } else {
        window.location.href = targetUserDash;
      }
      return false;
    }

    initUserNavbar();
    return true;
  };

  /**
   * Update UI header/navbar with current logged-in user profile info and account dropdown/switcher
   */
  const initUserNavbar = () => {
    const user = AgriAPI.getCurrentUser();
    if (!user) return;

    // The canonical authority on admin privileges is user.role === 'admin'
    const isAdmin = Boolean(
      user && user.role && user.role.toLowerCase().trim() === 'admin'
    );

    // If role was revoked from admin, cleanse any residual admin role_display string
    if (!isAdmin && user && user.role_display && user.role_display.toLowerCase().includes('admin')) {
      user.role_display = user.role === 'buyer' ? 'Buyer' : 'General User';
      try {
        localStorage.setItem(AgriConfig.USER_KEY, JSON.stringify(user));
      } catch {}
    }

    const nameElements = document.querySelectorAll('.user-display-name');
    nameElements.forEach(el => {
      el.textContent = user.full_name || user.email.split('@')[0];
    });

    const roleBadges = document.querySelectorAll('.user-role-badge');
    roleBadges.forEach(el => {
      if (isAdmin) {
        const path = window.location.pathname;
        if (path.includes('/pages/admin/')) {
          el.textContent = 'Administrator';
        } else {
          el.textContent = '🛡️ Admin (Grower View)';
        }
      } else {
        el.textContent = user.role_display || (user.role === 'buyer' ? 'Buyer' : 'General User');
      }
    });

    const emailElements = document.querySelectorAll('.user-display-email, #adm-current-email');
    emailElements.forEach(el => {
      el.textContent = user.email;
    });

    const avatarElements = document.querySelectorAll('.user-avatar-initial');
    avatarElements.forEach(el => {
      const initial = (user.full_name || user.email)[0].toUpperCase();
      el.textContent = initial;
    });

    // Handle Quick Mode Switcher button in navbar across all pages
    const quickSwitchBtns = document.querySelectorAll('.admin-quick-switch-btn, #admin-quick-switch-btn');
    quickSwitchBtns.forEach(btn => {
      btn.style.setProperty('display', isAdmin ? 'inline-flex' : 'none', 'important');
    });

    // Handle Sidebar Admin Mode Switcher section
    const sidebarAdminSections = document.querySelectorAll('#sidebar-admin-section, .sidebar-admin-section');
    sidebarAdminSections.forEach(sec => {
      sec.style.setProperty('display', isAdmin ? 'block' : 'none', 'important');
    });

    // Handle Admin role switcher in profile dropdown
    const path = window.location.pathname;
    const isUserPage = !path.includes('/pages/admin/');

    const dropdowns = document.querySelectorAll('.account-dropdown, #account-dropdown-menu, #user-account-dropdown-menu');
    dropdowns.forEach(dd => {
      const header = dd.querySelector('.account-dropdown-header');
      
      // Inject Profile Details & Persona Button if not present
      if (header && !dd.querySelector('#profile-details-btn-item')) {
        const profBtn = document.createElement('button');
        profBtn.id = 'profile-details-btn-item';
        profBtn.className = 'account-dropdown-item font-semibold';
        profBtn.setAttribute('type', 'button');
        profBtn.setAttribute('style', 'display: flex; align-items: center; justify-content: space-between; gap: 8px; color: #1D4ED8; background: rgba(37, 99, 235, 0.08); border: 1px solid rgba(147, 197, 253, 0.5); border-radius: 10px; margin-bottom: 8px; padding: 8px 12px; font-size: 13px; cursor: pointer;');
        profBtn.innerHTML = `
          <div style="display: flex; align-items: center; gap: 8px;">
            <i data-lucide="user-cog" style="width: 15px; height: 15px; color: #2563EB;"></i>
            <span>Profile & Role Details</span>
          </div>
          <span class="glass-badge badge-primary" style="font-size: 10px; padding: 2px 6px;">Farmer / Buyer</span>
        `;
        profBtn.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          dd.classList.remove('show');
          openProfileModal();
        });
        header.insertAdjacentElement('afterend', profBtn);
      }

      const switchContainers = dd.querySelectorAll('#admin-switch-option-container, .admin-switch-container');
      const adminLinks = dd.querySelectorAll('a[href*="/admin/dashboard"], a[href*="../admin/dashboard"]');

      if (isUserPage) {
        if (isAdmin) {
          if (switchContainers.length === 0) {
            const refHeader = dd.querySelector('#profile-details-btn-item') || header;
            if (refHeader) {
              const div = document.createElement('div');
              div.id = 'admin-switch-option-container';
              div.className = 'admin-switch-container';
              div.innerHTML = `
                <a href="../admin/dashboard.html" class="account-dropdown-item font-semibold" style="background: #FEF2F2; border: 1px solid #FECACA; color: #DC2626; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; padding: 9px 12px; border-radius: 10px; text-decoration: none; font-size: 13px;">
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <i data-lucide="repeat" style="width: 15px; height: 15px; color: #DC2626;"></i>
                    <span>Switch to Admin Console</span>
                  </div>
                  <span class="glass-badge badge-danger" style="font-size: 10px; padding: 2px 6px;">Admin Mode</span>
                </a>
                <div class="account-dropdown-divider" style="height: 1px; background: #E2E8F0; margin: 6px 0;"></div>
              `;
              refHeader.insertAdjacentElement('afterend', div);
            }
          } else {
            switchContainers.forEach(sc => sc.style.setProperty('display', 'block', 'important'));
            adminLinks.forEach(l => l.style.setProperty('display', 'flex', 'important'));
          }
        } else {
          switchContainers.forEach(sc => sc.style.setProperty('display', 'none', 'important'));
          adminLinks.forEach(l => {
            const wrap = l.closest('#admin-switch-option-container, .admin-switch-container') || l;
            wrap.style.setProperty('display', 'none', 'important');
          });
        }
      }
    });

    const logoutButtons = document.querySelectorAll('.btn-logout');
    logoutButtons.forEach(btn => {
      if (!btn.__hasLogoutListener) {
        btn.__hasLogoutListener = true;
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          AgriAPI.logout();
        });
      }
    });

    if (window.lucide && typeof window.lucide.createIcons === 'function') {
      window.lucide.createIcons();
    }
  };

  /**
   * Directly toggle account menu dropdown
   */
  const toggleDropdown = (btn, event) => {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    const container = (btn && btn.closest) ? btn.closest('.account-menu-container') : document.querySelector('.account-menu-container');
    if (!container) return;
    const dropdown = container.querySelector('.account-dropdown, #account-dropdown-menu, #user-account-dropdown-menu');
    if (!dropdown) return;

    const willOpen = !dropdown.classList.contains('show');

    // Close all open dropdowns
    document.querySelectorAll('.account-dropdown, #account-dropdown-menu, #user-account-dropdown-menu').forEach(dd => {
      dd.classList.remove('show');
      dd.style.setProperty('display', 'none', 'important');
    });

    if (willOpen) {
      initUserNavbar();
      dropdown.classList.add('show');
      dropdown.style.setProperty('display', 'block', 'important');
    }

    if (window.lucide && typeof window.lucide.createIcons === 'function') {
      window.lucide.createIcons();
    }
  };

  /**
   * Profile & Persona Details Modal (Farmer vs Buyer)
   */
  const openProfileModal = () => {
    // Close open dropdowns
    document.querySelectorAll('.account-dropdown.show, #account-dropdown-menu.show, #user-account-dropdown-menu.show').forEach(dd => {
      dd.classList.remove('show');
    });

    let modal = document.getElementById('agrismart-profile-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'agrismart-profile-modal';
      modal.className = 'admin-modal-overlay';
      modal.style.cssText = 'position: fixed; inset: 0; background: rgba(15, 23, 42, 0.55); backdrop-filter: blur(8px); z-index: 9999; display: none; align-items: center; justify-content: center; padding: 20px;';
      modal.innerHTML = `
        <div class="admin-modal-box" style="width: 100%; max-width: 650px; background: rgba(255, 255, 255, 0.98); border: 1.5px solid rgba(255, 255, 255, 0.95); border-radius: 20px; box-shadow: 0 25px 60px rgba(15, 23, 42, 0.25); display: flex; flex-direction: column; overflow: hidden; max-height: 90vh;">
          <div class="admin-modal-header" style="padding: 18px 24px; border-bottom: 1px solid #E2E8F0; display: flex; align-items: center; justify-content: space-between; background: #F8FAFC;">
            <div>
              <div class="font-bold text-lg text-primary" style="color: #0F172A; display: flex; align-items: center; gap: 8px;">
                <i data-lucide="user-check" style="width: 20px; height: 20px; color: #2563EB;"></i>
                <span>Profile & Persona Settings</span>
              </div>
              <div class="text-xs text-muted">Manage your personal profile and configure whether you are a CEA Farmer or Commercial Buyer</div>
            </div>
            <button type="button" class="glass-modal-close" onclick="AuthGuard.closeProfileModal()" style="background: transparent; border: none; font-size: 20px; cursor: pointer; color: #64748B;">✕</button>
          </div>

          <div class="admin-modal-body" style="padding: 24px; overflow-y: auto; flex: 1;">
            <div id="profile-modal-alert" class="glass-alert mb-4" style="display: none; padding: 10px 14px; border-radius: 10px; font-size: 13px;"></div>

            <form id="profile-modal-form" onsubmit="AuthGuard.saveProfileModal(event)" style="display: flex; flex-direction: column; gap: 16px;">
              <!-- Account Basic Info -->
              <div class="grid grid-2 gap-3">
                <div class="glass-input-group" style="margin-bottom: 0;">
                  <label class="glass-label" style="font-size: 13px; font-weight: 600;">Email Address</label>
                  <input id="prof-modal-email" type="email" class="glass-input" readonly disabled style="background: #F1F5F9; color: #64748B; cursor: not-allowed;">
                </div>
                <div class="glass-input-group" style="margin-bottom: 0;">
                  <label class="glass-label" style="font-size: 13px; font-weight: 600;">Full Name <span style="color:#DC2626;">*</span></label>
                  <input id="prof-modal-name" type="text" class="glass-input" placeholder="e.g. Ramesh Kumar" required style="background: #FFF;">
                </div>
              </div>

              <div class="grid grid-2 gap-3">
                <div class="glass-input-group" style="margin-bottom: 0;">
                  <label class="glass-label" style="font-size: 13px; font-weight: 600;">Contact Phone</label>
                  <input id="prof-modal-phone" type="tel" class="glass-input" placeholder="+91 98765 43210" style="background: #FFF;">
                </div>
                <div class="glass-input-group" style="margin-bottom: 0;">
                  <label class="glass-label" style="font-size: 13px; font-weight: 600;">Location / City</label>
                  <input id="prof-modal-location" type="text" class="glass-input" placeholder="e.g. Bengaluru, Karnataka" style="background: #FFF;">
                </div>
              </div>

              <!-- Persona Selection Cards -->
              <div>
                <label class="glass-label" style="font-size: 13px; font-weight: 700; margin-bottom: 8px; display: block;">
                  Select Your Primary Platform Role / Persona: <span style="color:#DC2626;">*</span>
                </label>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                  <!-- Farmer Card -->
                  <div id="persona-card-farmer" onclick="AuthGuard.selectPersona('farmer')" style="cursor: pointer; border: 2px solid #10B981; background: #ECFDF5; padding: 14px; border-radius: 12px; transition: all 0.2s ease;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                      <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #065F46; font-size: 14px;">
                        <span>🌱 CEA Grower / Farmer</span>
                      </div>
                      <input type="radio" name="prof_persona" id="radio-persona-farmer" value="farmer" checked style="accent-color: #059669; width: 16px; height: 16px;">
                    </div>
                    <div style="font-size: 12px; color: #047857; line-height: 1.4;">
                      Produces crops using Hydroponics, Vertical Farming, Algaculture, or Mushroom cultivation facilities.
                    </div>
                  </div>

                  <!-- Buyer Card -->
                  <div id="persona-card-buyer" onclick="AuthGuard.selectPersona('buyer')" style="cursor: pointer; border: 1.5px solid #CBD5E1; background: #FFFFFF; padding: 14px; border-radius: 12px; transition: all 0.2s ease;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                      <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #1E293B; font-size: 14px;">
                        <span>🛒 Commercial Buyer</span>
                      </div>
                      <input type="radio" name="prof_persona" id="radio-persona-buyer" value="buyer" style="accent-color: #2563EB; width: 16px; height: 16px;">
                    </div>
                    <div style="font-size: 12px; color: #64748B; line-height: 1.4;">
                      Procures fresh produce for Supermarkets, HORECA restaurants, Wholesale, Export, or Food Processing.
                    </div>
                  </div>
                </div>
              </div>

              <!-- Farmer Specific Fields -->
              <div id="farmer-fields-container" style="display: flex; flex-direction: column; gap: 12px; background: #F8FAFC; padding: 14px; border-radius: 12px; border: 1px solid #E2E8F0;">
                <div class="text-xs font-bold text-primary" style="color: #059669; text-transform: uppercase; letter-spacing: 0.05em;">Farmer & Facility Details</div>
                <div class="grid grid-2 gap-3">
                  <div class="glass-input-group" style="margin-bottom: 0;">
                    <label class="glass-label" style="font-size: 12px;">Farm / Facility Name</label>
                    <input id="prof-modal-farm-name" type="text" class="glass-input" placeholder="e.g. GreenHorizon Hydroponics" style="background: #FFF;">
                  </div>
                  <div class="glass-input-group" style="margin-bottom: 0;">
                    <label class="glass-label" style="font-size: 12px;">Primary Cultivation Method</label>
                    <select id="prof-modal-farm-method" class="glass-input" style="background: #FFF;">
                      <option value="NFT Hydroponics">NFT Hydroponics (Leafy Greens & Herbs)</option>
                      <option value="Dutch Bucket">Dutch Bucket / Bato (Vine Crops & Tomato)</option>
                      <option value="Deep Water Culture">Deep Water Culture (DWC)</option>
                      <option value="Vertical CEA">Indoor Vertical CEA Rack Systems</option>
                      <option value="Algaculture">Algaculture / Photobioreactor (Spirulina/Chlorella)</option>
                      <option value="Mushroom Substrate">Mushroom / Fungi Controlled Substrate</option>
                    </select>
                  </div>
                </div>
                <div class="grid grid-2 gap-3">
                  <div class="glass-input-group" style="margin-bottom: 0;">
                    <label class="glass-label" style="font-size: 12px;">Cultivation Area (sq.m)</label>
                    <input id="prof-modal-farm-area" type="number" class="glass-input" placeholder="e.g. 500" style="background: #FFF;">
                  </div>
                  <div class="glass-input-group" style="margin-bottom: 0;">
                    <label class="glass-label" style="font-size: 12px;">Primary Crops Produced</label>
                    <input id="prof-modal-farm-crops" type="text" class="glass-input" placeholder="e.g. Lettuce, Basil, Spirulina" style="background: #FFF;">
                  </div>
                </div>
              </div>

              <!-- Buyer Specific Fields -->
              <div id="buyer-fields-container" style="display: none; flex-direction: column; gap: 12px; background: #F8FAFC; padding: 14px; border-radius: 12px; border: 1px solid #E2E8F0;">
                <div class="text-xs font-bold text-primary" style="color: #2563EB; text-transform: uppercase; letter-spacing: 0.05em;">Buyer & Procurement Details</div>
                <div class="grid grid-2 gap-3">
                  <div class="glass-input-group" style="margin-bottom: 0;">
                    <label class="glass-label" style="font-size: 12px;">Organization / Business Name</label>
                    <input id="prof-modal-buyer-org" type="text" class="glass-input" placeholder="e.g. Apex Fresh Produce Ltd." style="background: #FFF;">
                  </div>
                  <div class="glass-input-group" style="margin-bottom: 0;">
                    <label class="glass-label" style="font-size: 12px;">Business Type</label>
                    <select id="prof-modal-buyer-type" class="glass-input" style="background: #FFF;">
                      <option value="Supermarket / Retail Chain">Supermarket / Retail Chain</option>
                      <option value="Restaurant / HORECA">Restaurant / Hotel / HORECA</option>
                      <option value="Wholesale Distributor">Wholesale Distributor</option>
                      <option value="Food Processing">Food Processing & Value-Add</option>
                      <option value="Exporter">International Exporter</option>
                    </select>
                  </div>
                </div>
                <div class="grid grid-2 gap-3">
                  <div class="glass-input-group" style="margin-bottom: 0;">
                    <label class="glass-label" style="font-size: 12px;">Monthly Procurement Volume (kg)</label>
                    <input id="prof-modal-buyer-vol" type="number" class="glass-input" placeholder="e.g. 1500" style="background: #FFF;">
                  </div>
                  <div class="glass-input-group" style="margin-bottom: 0;">
                    <label class="glass-label" style="font-size: 12px;">Target Crops of Interest</label>
                    <input id="prof-modal-buyer-crops" type="text" class="glass-input" placeholder="e.g. Grade A Lettuce, Spinach, Spirulina" style="background: #FFF;">
                  </div>
                </div>
              </div>

              <!-- Action Buttons -->
              <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 8px;">
                <button type="button" class="glass-btn" onclick="AuthGuard.closeProfileModal()">Cancel</button>
                <button type="submit" id="btn-save-profile-modal" class="glass-btn glass-btn-primary" style="display: inline-flex; align-items: center; gap: 8px;">
                  <i data-lucide="check-circle" style="width: 16px; height: 16px;"></i>
                  <span>Save Profile Details</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      `;
      modal.addEventListener('click', (e) => {
        if (e.target === modal) closeProfileModal();
      });
      document.body.appendChild(modal);
    }

    // Populate current user data
    const user = AgriAPI.getCurrentUser() || {};
    document.getElementById('prof-modal-email').value = user.email || '';
    document.getElementById('prof-modal-name').value = user.full_name || '';
    document.getElementById('prof-modal-phone').value = user.phone || '';
    document.getElementById('prof-modal-location').value = user.location || user.city || '';

    // Farmer data
    document.getElementById('prof-modal-farm-name').value = user.facility_name || user.organization || '';
    if (user.facility_type) document.getElementById('prof-modal-farm-method').value = user.facility_type;
    document.getElementById('prof-modal-farm-area').value = user.facility_area_sqm || '';
    document.getElementById('prof-modal-farm-crops').value = user.target_crops || '';

    // Buyer data
    document.getElementById('prof-modal-buyer-org').value = user.organization || user.company_name || '';
    if (user.business_type) document.getElementById('prof-modal-buyer-type').value = user.business_type;
    document.getElementById('prof-modal-buyer-vol').value = user.monthly_volume_kg || '';
    document.getElementById('prof-modal-buyer-crops').value = user.target_crops || '';

    const currentPersona = user.persona || (user.role === 'buyer' ? 'buyer' : 'farmer');
    selectPersona(currentPersona);

    const alertBox = document.getElementById('profile-modal-alert');
    if (alertBox) alertBox.style.display = 'none';

    modal.style.display = 'flex';
    if (window.lucide && typeof window.lucide.createIcons === 'function') {
      window.lucide.createIcons();
    }
  };

  const closeProfileModal = () => {
    const modal = document.getElementById('agrismart-profile-modal');
    if (modal) modal.style.display = 'none';
  };

  const selectPersona = (type) => {
    const farmerCard = document.getElementById('persona-card-farmer');
    const buyerCard = document.getElementById('persona-card-buyer');
    const farmerFields = document.getElementById('farmer-fields-container');
    const buyerFields = document.getElementById('buyer-fields-container');
    const radioFarmer = document.getElementById('radio-persona-farmer');
    const radioBuyer = document.getElementById('radio-persona-buyer');

    if (type === 'buyer') {
      if (radioBuyer) radioBuyer.checked = true;
      if (radioFarmer) radioFarmer.checked = false;
      if (buyerCard) {
        buyerCard.style.border = '2px solid #2563EB';
        buyerCard.style.background = '#EFF6FF';
      }
      if (farmerCard) {
        farmerCard.style.border = '1.5px solid #CBD5E1';
        farmerCard.style.background = '#FFFFFF';
      }
      if (farmerFields) farmerFields.style.display = 'none';
      if (buyerFields) buyerFields.style.display = 'flex';
    } else {
      if (radioFarmer) radioFarmer.checked = true;
      if (radioBuyer) radioBuyer.checked = false;
      if (farmerCard) {
        farmerCard.style.border = '2px solid #10B981';
        farmerCard.style.background = '#ECFDF5';
      }
      if (buyerCard) {
        buyerCard.style.border = '1.5px solid #CBD5E1';
        buyerCard.style.background = '#FFFFFF';
      }
      if (farmerFields) farmerFields.style.display = 'flex';
      if (buyerFields) buyerFields.style.display = 'none';
    }
  };

  const saveProfileModal = async (e) => {
    if (e) e.preventDefault();
    const alertBox = document.getElementById('profile-modal-alert');
    const btn = document.getElementById('btn-save-profile-modal');

    const fullName = document.getElementById('prof-modal-name').value.trim();
    const phone = document.getElementById('prof-modal-phone').value.trim();
    const location = document.getElementById('prof-modal-location').value.trim();
    const persona = document.querySelector('input[name="prof_persona"]:checked')?.value || 'farmer';

    let organization = '';
    let facility_type = '';
    let facility_area_sqm = null;
    let target_crops = '';
    let monthly_volume_kg = null;
    let business_type = '';

    if (persona === 'farmer') {
      organization = document.getElementById('prof-modal-farm-name').value.trim();
      facility_type = document.getElementById('prof-modal-farm-method').value;
      facility_area_sqm = parseFloat(document.getElementById('prof-modal-farm-area').value) || null;
      target_crops = document.getElementById('prof-modal-farm-crops').value.trim();
    } else {
      organization = document.getElementById('prof-modal-buyer-org').value.trim();
      business_type = document.getElementById('prof-modal-buyer-type').value;
      monthly_volume_kg = parseFloat(document.getElementById('prof-modal-buyer-vol').value) || null;
      target_crops = document.getElementById('prof-modal-buyer-crops').value.trim();
    }

    const payload = {
      full_name: fullName,
      phone,
      location,
      organization,
      persona,
      facility_type,
      facility_area_sqm,
      target_crops,
      monthly_volume_kg,
      business_type,
      bio: persona === 'farmer'
        ? `Grower / Farmer: ${organization || 'CEA Facility'} (${facility_type || 'Hydroponics'})`
        : `Commercial Buyer: ${organization || 'Procurement'} (${business_type || 'Retail'})`
    };

    try {
      if (btn) btn.disabled = true;
      let res;
      if (AgriAPI.users && typeof AgriAPI.users.updateProfile === 'function') {
        res = await AgriAPI.users.updateProfile(payload);
      } else {
        const cur = AgriAPI.getCurrentUser() || {};
        const merged = { ...cur, ...payload };
        localStorage.setItem(AgriConfig.USER_KEY, JSON.stringify(merged));
        res = { success: true, data: merged };
      }

      if (alertBox) {
        alertBox.style.display = 'block';
        alertBox.className = 'glass-alert glass-alert-success mb-4';
        alertBox.style.background = '#ECFDF5';
        alertBox.style.border = '1px solid #6EE7B7';
        alertBox.style.color = '#065F46';
        alertBox.innerHTML = `<strong>✅ Profile Saved!</strong> Your details and role persona (${persona === 'farmer' ? 'Grower / Farmer' : 'Commercial Buyer'}) have been updated.`;
      }

      const curUser = AgriAPI.getCurrentUser() || {};
      const updatedUser = { ...curUser, ...payload };
      if (curUser.role !== 'admin') {
        updatedUser.role_display = persona === 'farmer' ? 'Grower / Farmer' : 'Buyer / Procurement';
      }
      localStorage.setItem(AgriConfig.USER_KEY, JSON.stringify(updatedUser));
      initUserNavbar();

      setTimeout(() => {
        closeProfileModal();
        if (btn) btn.disabled = false;
      }, 900);
    } catch (err) {
      if (alertBox) {
        alertBox.style.display = 'block';
        alertBox.className = 'glass-alert glass-alert-danger mb-4';
        alertBox.style.background = '#FEF2F2';
        alertBox.style.border = '1px solid #FCA5A5';
        alertBox.style.color = '#991B1B';
        alertBox.innerHTML = `<strong>Error:</strong> ${err.message || 'Failed to save profile'}`;
      }
      if (btn) btn.disabled = false;
    }
  };

  /**
   * Sync current user profile from server to guarantee freshest permissions.
   * If a user's admin access was revoked, immediately remove all admin switcher options.
   */
  const syncCurrentUser = async () => {
    try {
      if (typeof AgriAPI !== 'undefined' && AgriAPI.isLoggedIn()) {
        const res = await AgriAPI.auth.me();
        if (res && res.success && res.data) {
          const freshUser = res.data;
          localStorage.setItem(AgriConfig.USER_KEY, JSON.stringify(freshUser));
          initUserNavbar();

          // If the user's admin access was revoked while they are currently on an admin page, eject them to user dashboard
          const path = window.location.pathname;
          if (path.includes('/pages/admin/') && freshUser.role !== 'admin') {
            alert('Your administrator privileges have been updated. Redirecting to User Dashboard.');
            window.location.href = '../user/dashboard.html';
          }
        }
      }
    } catch {
      // Fallback silently if offline or token expired
    }
  };

  // Global click & keydown handlers for robust dropdown closing
  if (typeof document !== 'undefined') {
    document.addEventListener('click', (e) => {
      const isMenuBtn = e.target.closest('.navbar-user-btn, #btn-account-menu, #btn-user-account-menu');
      const isInsideDropdown = e.target.closest('.account-dropdown, #account-dropdown-menu, #user-account-dropdown-menu');

      if (isMenuBtn) {
        const container = isMenuBtn.closest('.account-menu-container');
        const dropdown = container ? container.querySelector('.account-dropdown, #account-dropdown-menu, #user-account-dropdown-menu') : null;

        if (dropdown) {
          const willOpen = !dropdown.classList.contains('show');

          // Close all open dropdowns first
          document.querySelectorAll('.account-dropdown, #account-dropdown-menu, #user-account-dropdown-menu').forEach(dd => {
            dd.classList.remove('show');
            dd.style.setProperty('display', 'none', 'important');
          });

          if (willOpen) {
            initUserNavbar();
            dropdown.classList.add('show');
            dropdown.style.setProperty('display', 'block', 'important');
            if (window.lucide && typeof window.lucide.createIcons === 'function') {
              window.lucide.createIcons();
            }
          }
        }
        return;
      }

      // If clicked outside dropdown and outside menu button, close all open dropdowns
      if (!isInsideDropdown) {
        document.querySelectorAll('.account-dropdown, #account-dropdown-menu, #user-account-dropdown-menu').forEach(dd => {
          dd.classList.remove('show');
          dd.style.setProperty('display', 'none', 'important');
        });
      }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.account-dropdown, #account-dropdown-menu, #user-account-dropdown-menu').forEach(dd => {
          dd.classList.remove('show');
          dd.style.setProperty('display', 'none', 'important');
        });
        closeProfileModal();
      }
    });

    initUserNavbar();
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        initUserNavbar();
        syncCurrentUser();
      });
    } else {
      syncCurrentUser();
    }
  }

  return {
    requireAuth,
    initUserNavbar,
    syncCurrentUser,
    toggleDropdown,
    openProfileModal,
    closeProfileModal,
    selectPersona,
    saveProfileModal,
  };
})();
