/**
 * AgriSmart AI — API Client & High-Resilience Data Layer
 * =======================================================
 * Handles JWT injection, token refresh, standard error envelopes,
 * and transparent local fallback for standalone & demo environments.
 */

const AgriAPI = (() => {
  // ── Pre-seeded Demo Users (Default test accounts) ──────────────
  const DEFAULT_ACCOUNTS = [
    {
      id: 1,
      email: 'admin@agrismart.ai',
      password: 'Admin@12345',
      role: 'admin',
      role_display: 'Administrator',
      full_name: 'Platform Administrator',
      status: 'active',
      email_verified: true,
    },
    {
      id: 2,
      email: 'admin@agrismart.local',
      password: 'Admin@AgriSmart2026!',
      role: 'admin',
      role_display: 'Administrator',
      full_name: 'Platform Administrator',
      status: 'active',
      email_verified: true,
    },
    {
      id: 3,
      email: 'farmer@agrismart.ai',
      password: 'Farmer@12345',
      role: 'general_user',
      role_display: 'General User',
      full_name: 'Ramesh Kumar',
      status: 'active',
      email_verified: true,
    },
    {
      id: 4,
      email: 'producer@agrismart.ai',
      password: 'Producer@12345',
      role: 'general_user',
      role_display: 'General User',
      full_name: 'Priya Sharma',
      status: 'active',
      email_verified: true,
    },
    {
      id: 5,
      email: 'demo@agrismart.ai',
      password: 'Demo@12345',
      role: 'general_user',
      role_display: 'General User',
      full_name: 'Demo Producer',
      status: 'active',
      email_verified: true,
    },
    {
      id: 6,
      email: 'buyer@agrismart.ai',
      password: 'Buyer@12345',
      role: 'buyer',
      role_display: 'Buyer',
      full_name: 'Anil Mehta',
      status: 'active',
      email_verified: true,
    },
  ];

  // ── Cultivation Datasets (Live user projects only — no artificial fillers) ──
  const DEFAULT_USER_PROJECTS = [];

  const getStoredProjects = () => {
    try {
      const stored = localStorage.getItem('agrismart_projects');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          return parsed.filter(p => p && p.status !== 'deleted' && !['farmer@agrismart.ai', 'producer@agrismart.ai'].includes(p.owner_email));
        }
      }
      return [];
    } catch {
      return [];
    }
  };

  const saveStoredProjects = (projects) => {
    localStorage.setItem('agrismart_projects', JSON.stringify(projects));
  };

  const DEFAULT_USER_RECOMMENDATIONS = [];

  const getStoredRecommendations = () => {
    try {
      const stored = localStorage.getItem('agrismart_recommendations');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          return parsed.filter(r => r && !['farmer@agrismart.ai', 'producer@agrismart.ai'].includes(r.owner_email));
        }
      }
      return [];
    } catch {
      return [];
    }
  };

  const saveStoredRecommendations = (recs) => {
    localStorage.setItem('agrismart_recommendations', JSON.stringify(recs));
  };

  const DEFAULT_USER_REPORTS = [];

  const getStoredLabReports = () => {
    try {
      const stored = localStorage.getItem('agrismart_lab_reports');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          return parsed.filter(r => r && !['farmer@agrismart.ai', 'producer@agrismart.ai'].includes(r.owner_email));
        }
      }
      return [];
    } catch {
      return [];
    }
  };

  const saveStoredLabReports = (reports) => {
    localStorage.setItem('agrismart_lab_reports', JSON.stringify(reports));
  };

  // ── Local Auth Helpers ─────────────────────────────────────────
  const getRegisteredUsers = () => {
    try {
      const stored = localStorage.getItem('agrismart_registered_users');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  };

  const saveRegisteredUsers = (users) => {
    localStorage.setItem('agrismart_registered_users', JSON.stringify(users));
  };

  const getAllKnownUsers = () => {
    const local = getRegisteredUsers();
    const map = new Map();
    DEFAULT_ACCOUNTS.forEach(u => map.set(u.email.toLowerCase(), { ...u }));
    local.forEach(u => map.set(u.email.toLowerCase(), { ...u }));
    return Array.from(map.values());
  };

  const getResetTokens = () => {
    try {
      const stored = localStorage.getItem('agrismart_reset_tokens');
      return stored ? JSON.parse(stored) : {};
    } catch {
      return {};
    }
  };

  const saveResetTokens = (tokens) => {
    localStorage.setItem('agrismart_reset_tokens', JSON.stringify(tokens));
  };

  // ── Token helpers ─────────────────────────────────────────────
  const getToken = () => localStorage.getItem(AgriConfig.TOKEN_KEY);
  const getRefreshToken = () => localStorage.getItem(AgriConfig.REFRESH_TOKEN_KEY);

  const clearSession = () => {
    localStorage.removeItem(AgriConfig.TOKEN_KEY);
    localStorage.removeItem(AgriConfig.REFRESH_TOKEN_KEY);
    localStorage.removeItem(AgriConfig.USER_KEY);
  };

  const redirectToLogin = () => {
    clearSession();
    const path = window.location.pathname;
    let targetLogin = 'login.html';
    if (path.includes('/pages/admin/') || path.includes('/pages/buyer/')) {
      targetLogin = '../user/login.html';
    } else if (path.includes('/pages/user/')) {
      targetLogin = 'login.html';
    } else {
      targetLogin = 'pages/user/login.html';
    }
    const current = encodeURIComponent(window.location.pathname + window.location.search);
    window.location.href = `${targetLogin}?next=${current}`;
  };

  // ── Token refresh ─────────────────────────────────────────────
  let refreshInProgress = null;

  const tryRefresh = async () => {
    if (refreshInProgress) return refreshInProgress;

    refreshInProgress = (async () => {
      const rt = getRefreshToken();
      if (!rt || rt.startsWith('mock_')) {
        clearSession();
        throw new Error('No valid refresh token');
      }

      try {
        const res = await fetch(`${AgriConfig.API_BASE}/auth/refresh`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${rt}` },
        });

        const data = await res.json();
        if (!res.ok || !data.success || !data.access_token) {
          clearSession();
          throw new Error(data.error || 'Refresh failed');
        }

        localStorage.setItem(AgriConfig.TOKEN_KEY, data.access_token);
        return data.access_token;
      } catch (e) {
        clearSession();
        throw e;
      }
    })().finally(() => { refreshInProgress = null; });

    return refreshInProgress;
  };

  // ── Local Fallback Handlers ────────────────────────────────────
  const handleLocalFallback = (endpoint, method, body) => {
    const ep = endpoint.toLowerCase();

    // 1. Login
    if (ep.endsWith('/auth/login') && method === 'POST') {
      const email = (body.email || '').toLowerCase().trim();
      const password = body.password || '';
      const allUsers = getAllKnownUsers();
      const user = allUsers.find(u => u.email.toLowerCase() === email);

      if (!user || user.password !== password) {
        const err = new Error('Invalid email or password.');
        err.status = 401;
        throw err;
      }

      const access_token = 'mock_jwt_access_' + user.id + '_' + Date.now();
      const refresh_token = 'mock_jwt_refresh_' + user.id + '_' + Date.now();
      const safeUser = {
        id: user.id,
        email: user.email,
        role: user.role,
        role_display: user.role_display || (user.role === 'admin' ? 'Administrator' : (user.role === 'buyer' ? 'Buyer' : 'General User')),
        full_name: user.full_name || 'AgriSmart User',
        status: user.status || 'active',
        email_verified: true,
      };

      return {
        success: true,
        message: 'Login successful (Local Mode)',
        access_token,
        refresh_token,
        user: safeUser,
      };
    }

    // 2. Register
    if (ep.endsWith('/auth/register') && method === 'POST') {
      const email = (body.email || '').toLowerCase().trim();
      const password = body.password || '';
      const full_name = (body.full_name || '').trim();
      const role = body.role || 'general_user';

      if (!email || !password || password.length < 8) {
        const err = new Error('Please provide a valid email and password (min 8 characters).');
        err.status = 422;
        throw err;
      }

      if (role === 'admin') {
        const err = new Error('Admin registration is not permitted via public API.');
        err.status = 400;
        throw err;
      }

      const allUsers = getAllKnownUsers();
      if (allUsers.some(u => u.email.toLowerCase() === email)) {
        const err = new Error('This email address is already registered.');
        err.status = 409;
        throw err;
      }

      const newUser = {
        id: Date.now(),
        email,
        password,
        role,
        role_display: role === 'buyer' ? 'Buyer' : 'General User',
        full_name: full_name || 'AgriSmart User',
        status: 'active',
        email_verified: true,
      };

      const registered = getRegisteredUsers();
      registered.push(newUser);
      saveRegisteredUsers(registered);

      const access_token = 'mock_jwt_access_' + newUser.id + '_' + Date.now();
      const refresh_token = 'mock_jwt_refresh_' + newUser.id + '_' + Date.now();
      const safeUser = {
        id: newUser.id,
        email: newUser.email,
        role: newUser.role,
        role_display: newUser.role_display,
        full_name: newUser.full_name,
        status: newUser.status,
        email_verified: true,
      };

      return {
        success: true,
        message: 'Registration successful',
        access_token,
        refresh_token,
        user: safeUser,
      };
    }

    // 3. Forgot Password
    if (ep.endsWith('/auth/forgot-password') && method === 'POST') {
      const email = (body.email || '').toLowerCase().trim();
      const resetToken = 'rst_' + Math.random().toString(36).substring(2, 10) + Date.now().toString(36);
      
      const tokens = getResetTokens();
      tokens[resetToken] = {
        email,
        expires: Date.now() + 3600000, // 1 hour
      };
      saveResetTokens(tokens);

      return {
        success: true,
        message: 'If the email is registered, a password reset link has been generated.',
        _demo_reset_token: resetToken,
      };
    }

    // 4. Reset Password
    if (ep.endsWith('/auth/reset-password') && method === 'POST') {
      const token = body.token || '';
      const new_password = body.new_password || '';

      if (!token || !new_password || new_password.length < 8) {
        const err = new Error('Invalid token or password too short (min. 8 characters).');
        err.status = 422;
        throw err;
      }

      const tokens = getResetTokens();
      const tokenData = tokens[token];

      // Update registered users or default accounts in local storage
      const registered = getRegisteredUsers();
      const emailToReset = tokenData ? tokenData.email : null;

      let found = false;
      registered.forEach(u => {
        if (!emailToReset || u.email.toLowerCase() === emailToReset.toLowerCase()) {
          u.password = new_password;
          found = true;
        }
      });

      if (!found && emailToReset) {
        // Create an entry in registered users to override default password
        const def = DEFAULT_ACCOUNTS.find(u => u.email.toLowerCase() === emailToReset.toLowerCase());
        if (def) {
          registered.push({ ...def, password: new_password });
        }
      }

      saveRegisteredUsers(registered);
      if (tokenData) {
        delete tokens[token];
        saveResetTokens(tokens);
      }

      return {
        success: true,
        message: 'Password has been successfully reset. You can now sign in with your new password.',
      };
    }

    // 5. Auth Me
    if (ep.endsWith('/auth/me')) {
      const stored = localStorage.getItem(AgriConfig.USER_KEY);
      let parsed = null;
      if (stored) {
        try { parsed = JSON.parse(stored); } catch {}
      }
      if (parsed && parsed.email) {
        // Look up the freshest role in registered users / default accounts
        const all = getAllKnownUsers();
        const found = all.find(u => u.email.toLowerCase() === parsed.email.toLowerCase());
        if (found) {
          parsed.role = found.role;
          parsed.role_display = found.role_display || (found.role === 'admin' ? 'Administrator' : 'General User');
          parsed.full_name = found.full_name || parsed.full_name;
        }
        return { success: true, data: parsed };
      }
      return { success: true, data: DEFAULT_ACCOUNTS[2] };
    }

    // 6. Cultivation Products (All 18 Crops)
    if (ep.includes('/cultivation/products')) {
      const crops = [
        { id: 1, common_name: 'Lettuce', method_name: 'Hydroponics (Soil-Free)', method_display: 'Vertical NFT Hydroponics', scientific_name: 'Lactuca sativa', ecosystem: 'hydroponics', typical_harvest_days_min: 28, typical_harvest_days_max: 35, yield_kg_per_sqm_cycle_min: 3.5, yield_kg_per_sqm_cycle_max: 5.0, image_url: 'https://images.unsplash.com/photo-1556801712-76c8eb07bbc9?auto=format&fit=crop&w=800&q=80' },
        { id: 2, common_name: 'Spinach', method_name: 'Hydroponics (Soil-Free)', method_display: 'NFT Hydroponics', scientific_name: 'Spinacia oleracea', ecosystem: 'hydroponics', typical_harvest_days_min: 25, typical_harvest_days_max: 30, yield_kg_per_sqm_cycle_min: 2.5, yield_kg_per_sqm_cycle_max: 4.0, image_url: 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=800&q=80' },
        { id: 3, common_name: 'Kale', method_name: 'Hydroponics (Soil-Free)', method_display: 'Deep Water Culture (DWC)', scientific_name: 'Brassica oleracea var. acephala', ecosystem: 'hydroponics', typical_harvest_days_min: 35, typical_harvest_days_max: 45, yield_kg_per_sqm_cycle_min: 3.0, yield_kg_per_sqm_cycle_max: 4.5, image_url: 'https://images.unsplash.com/photo-1524179091875-bf99a9a6af57?auto=format&fit=crop&w=800&q=80' },
        { id: 4, common_name: 'Basil', method_name: 'Hydroponics (Soil-Free)', method_display: 'NFT Herb Channels', scientific_name: 'Ocimum basilicum', ecosystem: 'hydroponics', typical_harvest_days_min: 28, typical_harvest_days_max: 35, yield_kg_per_sqm_cycle_min: 2.0, yield_kg_per_sqm_cycle_max: 3.5, image_url: 'https://images.unsplash.com/photo-1608686207856-001b95cf60ca?auto=format&fit=crop&w=800&q=80' },
        { id: 5, common_name: 'Mint', method_name: 'Hydroponics (Soil-Free)', method_display: 'NFT Hydroponics', scientific_name: 'Mentha spicata', ecosystem: 'hydroponics', typical_harvest_days_min: 25, typical_harvest_days_max: 30, yield_kg_per_sqm_cycle_min: 2.5, yield_kg_per_sqm_cycle_max: 4.0, image_url: 'https://images.unsplash.com/photo-1608686207856-001b95cf60ca?auto=format&fit=crop&w=800&q=80' },
        { id: 6, common_name: 'Coriander', method_name: 'Hydroponics (Soil-Free)', method_display: 'Ebb & Flow Tables', scientific_name: 'Coriandrum sativum', ecosystem: 'hydroponics', typical_harvest_days_min: 30, typical_harvest_days_max: 40, yield_kg_per_sqm_cycle_min: 2.0, yield_kg_per_sqm_cycle_max: 3.0, image_url: 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=800&q=80' },
        { id: 7, common_name: 'Tomato', method_name: 'Hydroponics (Soil-Free)', method_display: 'Dutch Bucket Bato System', scientific_name: 'Solanum lycopersicum', ecosystem: 'hydroponics', typical_harvest_days_min: 65, typical_harvest_days_max: 85, yield_kg_per_sqm_cycle_min: 8.0, yield_kg_per_sqm_cycle_max: 15.0, image_url: 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=800&q=80' },
        { id: 8, common_name: 'Cucumber', method_name: 'Hydroponics (Soil-Free)', method_display: 'Dutch Bucket / Vine Trellis', scientific_name: 'Cucumis sativus', ecosystem: 'hydroponics', typical_harvest_days_min: 45, typical_harvest_days_max: 55, yield_kg_per_sqm_cycle_min: 6.0, yield_kg_per_sqm_cycle_max: 12.0, image_url: 'https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?auto=format&fit=crop&w=800&q=80' },
        { id: 9, common_name: 'Bell Pepper', method_name: 'Hydroponics (Soil-Free)', method_display: 'Cocopeat Slab Drip System', scientific_name: 'Capsicum annuum', ecosystem: 'hydroponics', typical_harvest_days_min: 60, typical_harvest_days_max: 75, yield_kg_per_sqm_cycle_min: 5.0, yield_kg_per_sqm_cycle_max: 9.0, image_url: 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?auto=format&fit=crop&w=800&q=80' },
        { id: 10, common_name: 'Strawberry', method_name: 'Hydroponics (Soil-Free)', method_display: 'A-Frame Vertical NFT / Gutter', scientific_name: 'Fragaria × ananassa', ecosystem: 'hydroponics', typical_harvest_days_min: 60, typical_harvest_days_max: 90, yield_kg_per_sqm_cycle_min: 2.0, yield_kg_per_sqm_cycle_max: 4.0, image_url: 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?auto=format&fit=crop&w=800&q=80' },
        { id: 11, common_name: 'Microgreens', method_name: 'Hydroponics (Soil-Free)', method_display: 'Multi-Tier LED Vertical Rack', scientific_name: 'Mixed Brassica & Herbs', ecosystem: 'hydroponics', typical_harvest_days_min: 7, typical_harvest_days_max: 14, yield_kg_per_sqm_cycle_min: 1.5, yield_kg_per_sqm_cycle_max: 3.0, image_url: 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80' },
        { id: 12, common_name: 'Spirulina', method_name: 'Algaculture / Microalgae', method_display: 'Photobioreactor & Raceway Ponds', scientific_name: 'Arthrospira platensis', ecosystem: 'algaculture', typical_harvest_days_min: 10, typical_harvest_days_max: 15, yield_kg_per_sqm_cycle_min: 0.8, yield_kg_per_sqm_cycle_max: 1.8, image_url: 'https://images.unsplash.com/photo-1509358271058-acd22cc93898?auto=format&fit=crop&w=800&q=80' },
        { id: 13, common_name: 'Chlorella', method_name: 'Algaculture / Microalgae', method_display: 'Closed Tubular Photobioreactor', scientific_name: 'Chlorella vulgaris', ecosystem: 'algaculture', typical_harvest_days_min: 8, typical_harvest_days_max: 12, yield_kg_per_sqm_cycle_min: 0.6, yield_kg_per_sqm_cycle_max: 1.4, image_url: 'https://images.unsplash.com/photo-1509358271058-acd22cc93898?auto=format&fit=crop&w=800&q=80' },
        { id: 14, common_name: 'Oyster Mushroom', method_name: 'Fungi / Mushroom', method_display: 'Vertical Hanging Bag Cultivation', scientific_name: 'Pleurotus ostreatus', ecosystem: 'fungi', typical_harvest_days_min: 18, typical_harvest_days_max: 24, yield_kg_per_sqm_cycle_min: 10.0, yield_kg_per_sqm_cycle_max: 18.0, image_url: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80' },
        { id: 15, common_name: 'Button Mushroom', method_name: 'Fungi / Mushroom', method_display: 'Climate-Controlled Tray System', scientific_name: 'Agaricus bisporus', ecosystem: 'fungi', typical_harvest_days_min: 25, typical_harvest_days_max: 35, yield_kg_per_sqm_cycle_min: 12.0, yield_kg_per_sqm_cycle_max: 22.0, image_url: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80' },
        { id: 16, common_name: 'Milky Mushroom', method_name: 'Fungi / Mushroom', method_display: 'Humidified Indoor Polybag Beds', scientific_name: 'Calocybe indica', ecosystem: 'fungi', typical_harvest_days_min: 20, typical_harvest_days_max: 28, yield_kg_per_sqm_cycle_min: 8.0, yield_kg_per_sqm_cycle_max: 14.0, image_url: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80' },
        { id: 17, common_name: 'Shiitake', method_name: 'Fungi / Mushroom', method_display: 'Sterilized Hardwood Sawdust Block Racks', scientific_name: 'Lentinula edodes', ecosystem: 'fungi', typical_harvest_days_min: 35, typical_harvest_days_max: 50, yield_kg_per_sqm_cycle_min: 6.0, yield_kg_per_sqm_cycle_max: 11.0, image_url: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80' },
        { id: 18, common_name: "Lion's Mane", method_name: 'Fungi / Mushroom', method_display: 'Automated Grow Chamber Bag Racks', scientific_name: 'Hericium erinaceus', ecosystem: 'fungi', typical_harvest_days_min: 28, typical_harvest_days_max: 40, yield_kg_per_sqm_cycle_min: 5.0, yield_kg_per_sqm_cycle_max: 9.0, image_url: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80' },
      ];
      return { success: true, data: crops, meta: { count: crops.length } };
    }

    // 7. Buyer Requirements
    if (ep.endsWith('/buyer/requirements') && method === 'GET') {
      try {
        const stored = localStorage.getItem('agrismart_buyer_reqs');
        const reqs = stored ? JSON.parse(stored) : [
          { id: 1, product_id: 1, product_name: 'Lettuce', required_monthly_kg: 500, target_price_inr_per_kg: 120, quality_grade: 'Grade A Premium' },
          { id: 2, product_id: 12, product_name: 'Spirulina', required_monthly_kg: 150, target_price_inr_per_kg: 850, quality_grade: 'High-Purity Pharma Grade' },
          { id: 3, product_id: 14, product_name: 'Oyster Mushroom', required_monthly_kg: 300, target_price_inr_per_kg: 180, quality_grade: 'Fresh Export Grade' }
        ];
        return { success: true, data: reqs };
      } catch {
        return { success: true, data: [] };
      }
    }

    if (ep.endsWith('/buyer/requirements') && method === 'POST') {
      const stored = localStorage.getItem('agrismart_buyer_reqs');
      const reqs = stored ? JSON.parse(stored) : [];
      const cropNames = {
        1: 'Lettuce', 2: 'Spinach', 3: 'Kale', 4: 'Basil', 5: 'Mint', 6: 'Coriander',
        7: 'Tomato', 8: 'Cucumber', 9: 'Bell Pepper', 10: 'Strawberry', 11: 'Microgreens',
        12: 'Spirulina', 13: 'Chlorella', 14: 'Oyster Mushroom', 15: 'Button Mushroom',
        16: 'Milky Mushroom', 17: 'Shiitake', 18: "Lion's Mane"
      };
      const newReq = {
        id: Date.now(),
        product_id: body.product_id,
        product_name: cropNames[body.product_id] || `Crop #${body.product_id}`,
        required_monthly_kg: body.required_quantity_kg_per_month,
        target_price_inr_per_kg: body.target_price_inr_per_kg,
        quality_grade: body.quality_grade || 'Standard A',
      };
      reqs.unshift(newReq);
      localStorage.setItem('agrismart_buyer_reqs', JSON.stringify(reqs));
      return { success: true, message: 'Requirement posted successfully', data: newReq };
    }

    if (ep.includes('/buyer/requirements/') && method === 'DELETE') {
      const parts = ep.split('/');
      const id = parseInt(parts[parts.length - 1]);
      const stored = localStorage.getItem('agrismart_buyer_reqs');
      if (stored) {
        let reqs = JSON.parse(stored);
        reqs = reqs.filter(r => r.id !== id);
        localStorage.setItem('agrismart_buyer_reqs', JSON.stringify(reqs));
      }
      return { success: true, message: 'Requirement deleted' };
    }

    // 7b. User Profile Details & Persona
    if (ep.endsWith('/users/profile') && method === 'GET') {
      const user = getCurrentUser() || DEFAULT_ACCOUNTS[2];
      return {
        success: true,
        data: {
          id: user.id,
          email: user.email,
          role: user.role,
          role_display: user.role_display,
          full_name: user.full_name,
          phone: user.phone || '',
          organization: user.organization || '',
          bio: user.bio || '',
          persona: user.persona || (user.role === 'buyer' ? 'buyer' : 'farmer'),
          facility_type: user.facility_type || '',
          facility_area_sqm: user.facility_area_sqm || '',
          target_crops: user.target_crops || '',
          monthly_volume_kg: user.monthly_volume_kg || '',
          business_type: user.business_type || '',
        }
      };
    }

    if (ep.endsWith('/users/profile') && method === 'PUT') {
      const current = getCurrentUser() || {};
      const updated = {
        ...current,
        full_name: body.full_name !== undefined ? body.full_name : current.full_name,
        phone: body.phone !== undefined ? body.phone : current.phone,
        organization: body.organization !== undefined ? body.organization : current.organization,
        bio: body.bio !== undefined ? body.bio : current.bio,
        persona: body.persona !== undefined ? body.persona : current.persona,
        facility_type: body.facility_type !== undefined ? body.facility_type : current.facility_type,
        facility_area_sqm: body.facility_area_sqm !== undefined ? body.facility_area_sqm : current.facility_area_sqm,
        target_crops: body.target_crops !== undefined ? body.target_crops : current.target_crops,
        monthly_volume_kg: body.monthly_volume_kg !== undefined ? body.monthly_volume_kg : current.monthly_volume_kg,
        business_type: body.business_type !== undefined ? body.business_type : current.business_type,
      };

      localStorage.setItem(AgriConfig.USER_KEY, JSON.stringify(updated));

      const registered = getRegisteredUsers();
      const idx = registered.findIndex(u => (u.email && updated.email && u.email.toLowerCase() === updated.email.toLowerCase()) || u.id === updated.id);
      if (idx !== -1) {
        registered[idx] = { ...registered[idx], ...updated };
        saveRegisteredUsers(registered);
      }

      return {
        success: true,
        message: 'Profile details saved successfully',
        data: updated
      };
    }

    // 8. User Projects (Create, List, Get, Update, Delete)
    if (ep.endsWith('/users/projects') && method === 'GET') {
      const projects = getStoredProjects();
      const currentUser = getCurrentUser();
      const userProjects = currentUser
        ? projects.filter(p => p.user_id === currentUser.id || (p.owner_email && currentUser.email && p.owner_email.toLowerCase() === currentUser.email.toLowerCase()))
        : projects;
      return { success: true, data: userProjects };
    }

    if (ep.endsWith('/users/projects') && method === 'POST') {
      const projects = getStoredProjects();
      const currentUser = getCurrentUser() || { id: 3, email: 'farmer@agrismart.ai', full_name: 'Ramesh Kumar' };
      const newProj = {
        id: Date.now(),
        name: (body && body.name) ? body.name.trim() : 'Cultivation Facility',
        description: (body && body.description) ? body.description.trim() : '',
        user_id: currentUser.id,
        owner_email: currentUser.email,
        owner_name: currentUser.full_name || currentUser.email,
        status: 'active',
        location: '',
        area_sqm: null,
        batches_count: 0,
        created_at: new Date().toISOString()
      };
      projects.unshift(newProj);
      saveStoredProjects(projects);
      return { success: true, data: newProj };
    }

    if (ep.includes('/users/projects/') && method === 'GET') {
      const parts = ep.split('/');
      const id = parseInt(parts[parts.length - 1]);
      const projects = getStoredProjects();
      const proj = projects.find(p => p.id === id);
      if (!proj) {
        const err = new Error('Project not found');
        err.status = 404;
        throw err;
      }
      return { success: true, data: proj };
    }

    if (ep.includes('/users/projects/') && method === 'PUT') {
      const parts = ep.split('/');
      const id = parseInt(parts[parts.length - 1]);
      const projects = getStoredProjects();
      const idx = projects.findIndex(p => p.id === id);
      if (idx !== -1) {
        projects[idx] = { ...projects[idx], ...body, updated_at: new Date().toISOString() };
        saveStoredProjects(projects);
        return { success: true, data: projects[idx] };
      }
      const err = new Error('Project not found');
      err.status = 404;
      throw err;
    }

    if (ep.includes('/users/projects/') && method === 'DELETE') {
      const parts = ep.split('/');
      const id = parseInt(parts[parts.length - 1]);
      let projects = getStoredProjects();
      projects = projects.filter(p => p.id !== id);
      saveStoredProjects(projects);
      return { success: true, message: 'Project deleted successfully' };
    }

    // 9. Location & Geocoding
    if (ep.includes('/location/geocode')) {
      const q = (new URLSearchParams(ep.split('?')[1] || '').get('q') || 'Bengaluru').trim();
      return {
        success: true,
        data: {
          found: true,
          display_name: `${q}, India`,
          city: q,
          state: 'Karnataka',
          country: 'India',
          latitude: 12.9716,
          longitude: 77.5946,
        }
      };
    }

    if (ep.includes('/location/project/')) {
      const parts = ep.split('/');
      const id = parseInt(parts[parts.length - 1]);
      const projects = getStoredProjects();
      const idx = projects.findIndex(p => p.id === id);
      if (idx !== -1) {
        const locName = body.city || body.display_name || body.raw_input || 'India';
        projects[idx].location = locName;
        projects[idx].location_details = body;
        saveStoredProjects(projects);
        return { success: true, data: projects[idx] };
      }
      return { success: true };
    }

    // 10. Weather Coordinates
    if (ep.includes('/weather/coordinates') || ep.includes('/weather/project/')) {
      return {
        success: true,
        data: {
          current: {
            temperature_c: 24.5,
            humidity_pct: 62,
          },
          climate_profile: {
            solar_potential: 'Optimal High',
            avg_temp_c: 24.5,
            relative_humidity_pct: 62,
          }
        }
      };
    }

    // 11. AI Recommendations Run
    if (ep.includes('/recommendations/run/')) {
      const parts = ep.split('/');
      const projId = parseInt(parts[parts.length - 1]);
      const projects = getStoredProjects();
      const proj = projects.find(p => p.id === projId);

      if (proj && body && body.available_area_sqm) {
        proj.area_sqm = body.available_area_sqm;
        saveStoredProjects(projects);
      }

      const recs = getStoredRecommendations();
      const currentUser = getCurrentUser();

      const runData = {
        id: Date.now(),
        project_id: projId,
        project_name: proj ? proj.name : `Project #${projId}`,
        owner_email: proj ? proj.owner_email : (currentUser ? currentUser.email : 'producer@agrismart.ai'),
        objective_type: (body && body.objective_type) || 'maximum_profit',
        top_crop: 'Lettuce (Butterhead)',
        suitability_score: 94.8,
        status: 'complete',
        created_at: new Date().toISOString(),
        top_pick: {
          product_name: 'Lettuce (Butterhead)',
          method_display: 'Vertical NFT Hydroponics',
          scientific_name: 'Lactuca sativa',
          suitability_score: 94.8,
          estimated_yield_kg: 1420,
          estimated_revenue_inr: 284000,
          estimated_profit_inr: 198000,
          estimated_roi_pct: 79.2,
          feature_importance: [
            { feature_name: 'Climate Suitability', direction: 'positive', human_explanation: 'Ambient temperature matches ideal VPD range for leafy greens.' },
            { feature_name: 'Water Optimization', direction: 'positive', human_explanation: 'Closed loop recirculating system saves 90% water.' },
            { feature_name: 'Market Price Premium', direction: 'positive', human_explanation: 'High demand among local buyers for Grade A pesticide-free produce.' }
          ],
          component_scores: {
            weather: 95, water: 92, investment: 88, area: 96, labor: 90, yield: 94, economics: 91, nutrition: 85, risk: 93
          }
        },
        comparisons: [
          { top_product: 'Lettuce', alternative_product: 'Spinach', score_difference: 4.2, summary: 'Higher market price realization per square meter.' },
          { top_product: 'Lettuce', alternative_product: 'Bell Pepper', score_difference: 8.5, summary: 'Faster turnaround cycle (28 days vs 85 days).' }
        ],
        all_results: [
          { rank: 1, product_name: 'Lettuce (Butterhead)', method_display: 'Hydroponics (NFT)', feasible: true, suitability_score: 94.8, estimated_profit_inr: 198000, estimated_roi_pct: 79.2 },
          { rank: 2, product_name: 'Spinach', method_display: 'Hydroponics (DWC)', feasible: true, suitability_score: 90.6, estimated_profit_inr: 165000, estimated_roi_pct: 72.4 },
          { rank: 3, product_name: 'Basil', method_display: 'Hydroponics (NFT)', feasible: true, suitability_score: 88.4, estimated_profit_inr: 210000, estimated_roi_pct: 84.1 },
          { rank: 4, product_name: 'Spirulina', method_display: 'Algaculture Raceway', feasible: true, suitability_score: 86.2, estimated_profit_inr: 320000, estimated_roi_pct: 91.0 }
        ]
      };

      recs.unshift(runData);
      saveStoredRecommendations(recs);

      // Update project with latest recommendation
      if (proj) {
        proj.latest_recommendation = {
          run_id: runData.id,
          top_product: runData.top_crop,
          suitability_score: runData.suitability_score,
          date: runData.created_at
        };
        saveStoredProjects(projects);
      }

      return { success: true, data: runData };
    }

    if (ep.includes('/recommendations/project/') && ep.endsWith('/latest')) {
      const parts = ep.split('/');
      const projId = parseInt(parts[parts.length - 2]);
      const recs = getStoredRecommendations();
      const run = recs.find(r => r.project_id === projId);
      return { success: true, data: run || null };
    }

    // 12. Admin Dashboard Overview
    if (ep.includes('/admin/dashboard') && method === 'GET') {
      const all = getAllKnownUsers();
      const projects = getStoredProjects();
      const recs = getStoredRecommendations();
      const reports = getStoredLabReports();
      return {
        success: true,
        data: {
          metrics: {
            total_users: all.length,
            active_users: all.filter(u => u.status !== 'suspended').length,
            total_projects: projects.length,
            total_recommendations: recs.length,
            total_lab_reports: reports.length,
            total_laboratories: 6,
          },
          recent_activity: [
            { id: 1, action: 'admin.user.grant_admin', user_id: 1, target_type: 'User', created_at: new Date().toISOString(), ip: '127.0.0.1' },
            { id: 2, action: 'user.login', user_id: 1, target_type: 'Auth', created_at: new Date(Date.now() - 3600000).toISOString(), ip: '127.0.0.1' }
          ]
        }
      };
    }

    // 13. Admin Grant Admin Access (Checked before general /admin/users)
    if (ep.includes('/admin/users/grant-admin') && method === 'POST') {
      const email = (body.email || '').toLowerCase().trim();
      const full_name = (body.full_name || '').trim() || 'Platform Administrator';
      const initial_password = body.initial_password || 'Admin@12345';

      if (!email) {
        const err = new Error('Please provide a valid email address.');
        err.status = 422;
        throw err;
      }

      const registered = getRegisteredUsers();
      let user = registered.find(u => u.email.toLowerCase() === email);

      if (!user) {
        const def = DEFAULT_ACCOUNTS.find(u => u.email.toLowerCase() === email);
        if (def) {
          user = { ...def };
          registered.push(user);
        }
      }

      if (user) {
        user.role = 'admin';
        user.role_display = 'Administrator';
        if (full_name && full_name !== 'Platform Administrator') user.full_name = full_name;
        saveRegisteredUsers(registered);

        // If the promoted user is currently the active local user, update session immediately
        const current = getCurrentUser();
        if (current && ((current.email && current.email.toLowerCase() === email) || current.id === user.id)) {
          current.role = 'admin';
          current.role_display = 'Administrator';
          localStorage.setItem(AgriConfig.USER_KEY, JSON.stringify(current));
        }

        return {
          success: true,
          message: `Successfully granted Administrator privileges to ${email}.`,
          data: {
            id: user.id,
            email: user.email,
            role: 'admin',
            role_display: 'Administrator',
            full_name: user.full_name,
            status: user.status || 'active',
            is_new: false,
          }
        };
      } else {
        const newUser = {
          id: Date.now(),
          email,
          password: initial_password,
          role: 'admin',
          role_display: 'Administrator',
          full_name,
          status: 'active',
          email_verified: true,
          created_at: new Date().toISOString()
        };
        registered.push(newUser);
        saveRegisteredUsers(registered);

        // If the promoted user is currently the active local user, update session immediately
        const current = getCurrentUser();
        if (current && current.email && current.email.toLowerCase() === email) {
          current.role = 'admin';
          current.role_display = 'Administrator';
          localStorage.setItem(AgriConfig.USER_KEY, JSON.stringify(current));
        }

        return {
          success: true,
          message: `Created new Administrator account for ${email} (Temporary Password: ${initial_password}).`,
          data: {
            id: newUser.id,
            email: newUser.email,
            role: 'admin',
            role_display: 'Administrator',
            full_name: newUser.full_name,
            status: 'active',
            is_new: true,
            initial_password,
          }
        };
      }
    }

    // 14. Admin Revoke Admin Access (Strictly restricted to main admin)
    if (ep.includes('/admin/users/revoke-admin') && method === 'POST') {
      const current = getCurrentUser();
      const mainEmails = ['admin@agrismart.ai', 'admin@agrismart.local'];
      const isMainAdmin = current && current.email && (mainEmails.includes(current.email.toLowerCase()) || current.id === 1 || current.id === 2 || current.id === 9);

      if (!isMainAdmin) {
        const err = new Error('Only the Primary Administrator (Main Admin) has permission to remove administrator access.');
        err.status = 403;
        throw err;
      }

      const email = (body.email || '').toLowerCase().trim();
      const userId = body.user_id;

      if (current.email && current.email.toLowerCase() === email) {
        const err = new Error('Cannot remove your own administrator privileges.');
        err.status = 400;
        throw err;
      }

      if (mainEmails.includes(email)) {
        const err = new Error('Cannot remove the Primary Administrator account.');
        err.status = 400;
        throw err;
      }

      const registered = getRegisteredUsers();
      let user = registered.find(u => (u.email && u.email.toLowerCase() === email) || u.id === userId);
      if (user) {
        user.role = 'general_user';
        user.role_display = 'General User';
        saveRegisteredUsers(registered);
      } else {
        const def = DEFAULT_ACCOUNTS.find(u => (u.email && u.email.toLowerCase() === email) || u.id === userId);
        if (def && !mainEmails.includes(def.email.toLowerCase())) {
          def.role = 'general_user';
          def.role_display = 'General User';
        }
      }

      // If the revoked user is currently the active local user, update session immediately
      if (current && ((current.email && current.email.toLowerCase() === email) || current.id === userId)) {
        current.role = 'general_user';
        current.role_display = 'General User';
        localStorage.setItem(AgriConfig.USER_KEY, JSON.stringify(current));
      }

      return {
        success: true,
        message: `Successfully revoked administrator privileges from ${email || 'user'}. Account reverted to General User.`,
        data: { email, role: 'general_user' }
      };
    }

    // 15. Admin User Status Update
    if (ep.includes('/admin/users/') && ep.includes('/status') && method === 'PATCH') {
      const parts = ep.split('/');
      const userId = parseInt(parts[parts.indexOf('users') + 1]);
      const registered = getRegisteredUsers();
      let user = registered.find(u => u.id === userId);
      if (!user) {
        const def = DEFAULT_ACCOUNTS.find(u => u.id === userId);
        if (def) {
          user = { ...def };
          registered.push(user);
        }
      }
      if (user) {
        user.status = body.status;
        saveRegisteredUsers(registered);
      }
      return { success: true, message: `User status updated to ${body.status}` };
    }

    // 15. Admin Users List - Cross-linked with cultivation projects
    if (ep.includes('/admin/users') && method === 'GET') {
      const all = getAllKnownUsers();
      const allProjects = getStoredProjects();

      return {
        success: true,
        data: all.map(u => {
          const userProjects = allProjects.filter(p =>
            p.user_id === u.id || (p.owner_email && p.owner_email.toLowerCase() === u.email.toLowerCase())
          );
          return {
            id: u.id,
            email: u.email,
            role: u.role || 'general_user',
            role_display: u.role_display || (u.role === 'admin' ? 'Administrator' : (u.role === 'buyer' ? 'Buyer' : 'General User')),
            full_name: u.full_name || 'AgriSmart User',
            status: u.status || 'active',
            created_at: u.created_at || new Date().toISOString(),
            projects_count: userProjects.length,
            projects: userProjects
          };
        }),
        meta: { count: all.length }
      };
    }

    // 16. Admin Projects List - ONLY real projects created by registered users
    if (ep.includes('/admin/projects') && method === 'GET') {
      const projects = getStoredProjects();
      return { success: true, data: projects, meta: { count: projects.length } };
    }

    // 17. Admin AI Recommendation Runs List - ONLY real runs
    if (ep.includes('/admin/recommendations') && method === 'GET') {
      const runs = getStoredRecommendations();
      return { success: true, data: runs, meta: { count: runs.length } };
    }

    // 18. Admin Lab Reports List - ONLY real reports
    if (ep.includes('/admin/lab-reports') && method === 'GET') {
      const reports = getStoredLabReports();
      return { success: true, data: reports, meta: { count: reports.length } };
    }

    // Default generic mock success
    return { success: true, data: [] };
  };

  // ── Core request ──────────────────────────────────────────────
  const request = async (method, endpoint, body = null, options = {}) => {
    const url = `${AgriConfig.API_BASE}${endpoint}`;
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;

    const init = { method, headers };
    if (body && method !== 'GET') init.body = JSON.stringify(body);

    let res;
    try {
      res = await fetch(url, init);
    } catch (networkErr) {
      // Backend offline or unreachable — fallback to client-side auth & mock engine
      console.warn(`[AgriSmart API] Backend unreachable at ${url}. Engaging intelligent fallback.`, networkErr);
      return handleLocalFallback(endpoint, method, body);
    }

    // Auto-refresh on 401 or 422 token error
    const isAuthError = res.status === 401 || (res.status === 422 && token);
    if (isAuthError && !options._retried) {
      options._retried = true;
      if (token && token.startsWith('mock_')) {
        console.warn('[AgriSmart API] Mock token detected against live backend. Clearing session.');
        clearSession();
        delete headers.Authorization;
        try {
          res = await fetch(url, { ...init, headers, body: init.body });
        } catch {
          return handleLocalFallback(endpoint, method, body);
        }
      } else {
        try {
          const newToken = await tryRefresh();
          headers.Authorization = `Bearer ${newToken}`;
          res = await fetch(url, { ...init, headers, body: init.body });
        } catch {
          clearSession();
          delete headers.Authorization;
          const isPublicOrSafe = 
            endpoint.startsWith('/cultivation/') ||
            endpoint.startsWith('/market/') ||
            endpoint.startsWith('/labs') ||
            endpoint.startsWith('/health') ||
            endpoint.startsWith('/auth/me') ||
            endpoint.startsWith('/users/projects');

          if (isPublicOrSafe) {
            try {
              res = await fetch(url, { ...init, headers, body: init.body });
              if (!res.ok) {
                return handleLocalFallback(endpoint, method, body);
              }
            } catch {
              return handleLocalFallback(endpoint, method, body);
            }
          } else {
            redirectToLogin();
            throw new Error('Session expired — redirecting to login.');
          }
        }
      }
    }

    const data = await res.json().catch(() => ({ success: false, error: 'Invalid response from server' }));

    if (!res.ok) {
      const err = new Error(data.error || data.message || `HTTP ${res.status}`);
      err.status = res.status;
      err.data = data;
      throw err;
    }

    return data;
  };

  const get = (endpoint, opts) => request('GET', endpoint, null, opts);
  const post = (endpoint, body, opts) => request('POST', endpoint, body, opts);
  const put = (endpoint, body, opts) => request('PUT', endpoint, body, opts);
  const patch = (endpoint, body, opts) => request('PATCH', endpoint, body, opts);
  const del = (endpoint, opts) => request('DELETE', endpoint, null, opts);

  // ── File upload ────────────────────────────────────────────────
  const upload = async (endpoint, formData) => {
    const token = getToken();
    const headers = {};
    if (token) headers.Authorization = `Bearer ${token}`;

    try {
      const res = await fetch(`${AgriConfig.API_BASE}${endpoint}`, {
        method: 'POST',
        headers,
        body: formData,
      });
      const data = await res.json().catch(() => ({ success: false, error: 'Upload error' }));
      if (!res.ok) {
        const err = new Error(data.error || `HTTP ${res.status}`);
        err.status = res.status;
        throw err;
      }
      return data;
    } catch (err) {
      console.warn(`[AgriSmart API] Upload fallback triggered:`, err);
      return { success: true, message: 'File processed in demo mode' };
    }
  };

  // ── Namespaced API modules ──────────────────────────────────────

  const health = {
    check: () => get('/health'),
  };

  const auth = {
    register: (data) => post('/auth/register', data),
    login: (data) => post('/auth/login', data),
    logout: () => post('/auth/logout'),
    me: () => get('/auth/me'),
    refresh: () => post('/auth/refresh'),
    forgotPassword: (email) => post('/auth/forgot-password', { email }),
    resetPassword: (token, newPassword) =>
      post('/auth/reset-password', { token, new_password: newPassword }),
  };

  const users = {
    getProfile: () => get('/users/profile'),
    updateProfile: (data) => put('/users/profile', data),
    changePassword: (data) => post('/users/change-password', data),
  };

  const projects = {
    list: () => get('/users/projects'),
    create: (data) => post('/users/projects', data),
    get: (id) => get(`/users/projects/${id}`),
    update: (id, data) => put(`/users/projects/${id}`, data),
    delete: (id) => del(`/users/projects/${id}`),
  };

  const location = {
    geocode: (query) => get(`/location/geocode?q=${encodeURIComponent(query)}`),
    setProjectLocation: (projectId, data) => post(`/location/project/${projectId}`, data),
    getWeather: (projectId) => get(`/weather/project/${projectId}`),
  };

  const recommendations = {
    run: (projectId, data) => post(`/recommendations/run/${projectId}`, data),
    getLatest: (projectId) => get(`/recommendations/project/${projectId}/latest`),
    getAll: (projectId) => get(`/recommendations/project/${projectId}`),
    getExplanation: (runId, productId) =>
      get(`/recommendations/${runId}/explain/${productId}`),
  };

  const cultivation = {
    getMethods: () => get('/cultivation/methods'),
    getProducts: (methodId) => get(methodId ? `/cultivation/products?method_id=${encodeURIComponent(methodId)}` : '/cultivation/products'),
    getProduct: (id) => get(`/cultivation/products/${id}`),
  };

  const economics = {
    runScenario: (projectId, data) => post(`/economics/project/${projectId}/scenario`, data),
    getScenarios: (projectId) => get(`/economics/project/${projectId}/scenarios`),
    breakEven: (projectId, data) => post(`/economics/project/${projectId}/break-even`, data),
  };

  const quality = {
    getUserPassports: () => get('/quality/user/passports'),
    getBatches: (projectId) => get(`/quality/project/${projectId}/batches`),
    createBatch: (projectId, data) => post(`/quality/project/${projectId}/batches`, data),
    getBatch: (batchId) => get(`/quality/batches/${batchId}`),
    updateBatch: (batchId, data) => put(`/quality/batches/${batchId}`, data),
    uploadReport: (batchId, formData) => upload(`/quality/batches/${batchId}/report`, formData),
    getPassport: (batchId) => get(`/quality/batches/${batchId}/passport`),
    getPublicPassport: (token) => get(`/quality/passport/${token}`),
  };

  const labs = {
    search: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return get(qs ? `/labs?${qs}` : '/labs');
    },
    get: (id) => get(`/labs/${id}`),
  };

  const market = {
    getOverview: () => get('/market/overview'),
    getMarketData: (productId) => get(`/market/product/${productId}`),
    getSalesChannels: (productId) => get(`/market/product/${productId}/channels`),
  };

  const buyer = {
    getProfile: () => get('/buyer/profile'),
    updateProfile: (data) => put('/buyer/profile', data),
    getRequirements: () => get('/buyer/requirements'),
    addRequirement: (data) => post('/buyer/requirements', data),
    updateRequirement: (id, data) => put(`/buyer/requirements/${id}`, data),
    deleteRequirement: (id) => del(`/buyer/requirements/${id}`),
    getMatches: (requirementId) => get(`/buyer/matches/${requirementId}`),
    sendInquiry: (data) => post('/buyer/inquiries', data),
    getInquiries: () => get('/buyer/inquiries'),
  };

  const admin = {
    getDashboard: () => get('/admin/dashboard'),
    getUsers: () => get('/admin/users'),
    getProjects: () => get('/admin/projects'),
    getRecommendations: () => get('/admin/recommendations'),
    getLabReports: () => get('/admin/lab-reports'),
    grantAdmin: (data) => post('/admin/users/grant-admin', data),
    revokeAdmin: (data) => post('/admin/users/revoke-admin', typeof data === 'string' ? { email: data } : data),
    updateUserStatus: (userId, status) => patch(`/admin/users/${userId}/status`, { status }),
    // Lab management
    getLabs: () => get('/labs'),
    createLab: (data) => post('/admin/labs', data),
    updateLab: (id, data) => put(`/admin/labs/${id}`, data),
    // Market data
    addMarketObservation: (data) => post('/admin/market/observations', data),
    // Master data
    getProducts: () => get('/cultivation/products'),
    updateProduct: (id, data) => put(`/admin/cultivation/products/${id}`, data),
    // System settings
    getSettings: () => get('/admin/settings'),
    updateSetting: (key, value) => put(`/admin/settings/${key}`, { value }),
    // Audit logs
    getAuditLogs: (page = 1) => get(`/admin/audit?page=${page}`),
  };

  // ── Utility ────────────────────────────────────────────────────
  const getCurrentUser = () => {
    const stored = localStorage.getItem(AgriConfig.USER_KEY);
    if (!stored) return null;
    try { return JSON.parse(stored); }
    catch { return null; }
  };

  const isLoggedIn = () => !!getToken();

  const logout = () => {
    clearSession();
    auth.logout().catch(() => {}).finally(() => {
      const path = window.location.pathname;
      let targetLogin = 'login.html';
      if (path.includes('/pages/admin/') || path.includes('/pages/buyer/')) {
        targetLogin = '../user/login.html';
      } else if (path.includes('/pages/user/')) {
        targetLogin = 'login.html';
      } else {
        targetLogin = 'pages/user/login.html';
      }
      window.location.href = targetLogin;
    });
  };

  return {
    request, get, post, put, patch, del, upload,
    health, auth, users, projects, location,
    recommendations, cultivation, economics,
    quality, labs, market, buyer, admin,
    getCurrentUser, isLoggedIn, logout,
    DEFAULT_ACCOUNTS,
  };
})();
