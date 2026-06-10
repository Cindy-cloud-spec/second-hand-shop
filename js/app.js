// ============================================================
// SECOND HAND SHOP — App Logic
// ============================================================

// ============================================================
// MERKLISTE — localStorage-basierte Favoritenliste
// ============================================================
function getMerkliste() {
  try { return JSON.parse(localStorage.getItem('merkliste') || '[]').map(String); }
  catch(e) { return []; }
}
function setMerkliste(ids) {
  localStorage.setItem('merkliste', JSON.stringify(ids.map(String)));
}
function isInMerkliste(id) {
  return getMerkliste().includes(String(id));
}
function toggleMerkliste(id) {
  id = String(id);
  const list = getMerkliste();
  const idx  = list.indexOf(id);
  const added = idx === -1;
  if (added) list.push(id); else list.splice(idx, 1);
  setMerkliste(list);
  updateMerklisteBadge();
  return added;
}
function updateMerklisteBadge() {
  const count = getMerkliste().length;
  document.querySelectorAll('.merkliste-badge').forEach(el => {
    el.textContent = count || '';
    el.style.display = count ? '' : 'none';
  });
}

// Globaler Handler für Herzchen-Button auf Karten
window.toggleWishlistBtn = function(btn, id) {
  const added = toggleMerkliste(id);
  btn.classList.toggle('active', added);
  btn.title = added ? 'Von Merkliste entfernen' : 'Zur Merkliste hinzufügen';
  const svg = btn.querySelector('svg');
  if (svg) svg.setAttribute('fill', added ? 'currentColor' : 'none');
  // Merkliste-Seite neu rendern wenn offen
  if (typeof window.renderMerklisteGrid === 'function') window.renderMerklisteGrid();
};

// Globaler Handler für Herzchen-Button auf Produktdetailseite
window.toggleWishlistBtnDetail = function(btn, id) {
  const added = toggleMerkliste(id);
  btn.classList.toggle('active', added);
  const svg = btn.querySelector('svg');
  if (svg) svg.setAttribute('fill', added ? 'currentColor' : 'none');
  const span = btn.querySelector('span');
  if (span) span.textContent = added ? 'Von Merkliste entfernen' : 'Zur Merkliste hinzufügen';
};

// --- Nav: Mobile Toggle ---
function initNav() {
  const toggle = document.querySelector('.nav-mobile-toggle');
  const menu   = document.querySelector('.nav-mobile-menu');
  if (!toggle || !menu) return;

  toggle.addEventListener('click', () => {
    const open = menu.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
    document.body.style.overflow = open ? 'hidden' : '';
  });

  // Close on link click
  menu.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      menu.classList.remove('open');
      toggle.setAttribute('aria-expanded', false);
      document.body.style.overflow = '';
    });
  });

  // Mark active nav link
  const path = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a, .nav-mobile-menu a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === path || (path === '' && href === 'index.html')) {
      a.classList.add('active');
    }
  });
}

// --- FAQ Accordion ---
function initFaq() {
  document.querySelectorAll('.faq-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      const isOpen = item.classList.contains('open');
      // Close all
      document.querySelectorAll('.faq-item.open').forEach(i => i.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    });
  });
}

// --- Filter Group Collapse ---
function initFilterGroups() {
  document.querySelectorAll('.filter-group-header').forEach(header => {
    header.addEventListener('click', () => {
      header.closest('.filter-group').classList.toggle('collapsed');
    });
  });
}

// --- Mobile Filter Drawer ---
function initFilterDrawer() {
  const openBtn  = document.querySelector('[data-open-filter]');
  const drawer   = document.querySelector('.filter-drawer');
  const overlay  = document.querySelector('.filter-drawer-overlay');
  const closeBtn = document.querySelector('.filter-drawer-close');
  if (!openBtn || !drawer) return;

  function open() {
    drawer.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function close() {
    drawer.classList.remove('open');
    document.body.style.overflow = '';
  }

  openBtn.addEventListener('click', open);
  overlay?.addEventListener('click', close);
  closeBtn?.addEventListener('click', close);

  // Mobile Sortieren-Button
  const sortToggle = document.getElementById('mobile-sort-toggle');
  if (sortToggle) {
    const sortOptions = [
      { value: 'newest',     label: 'Neueste zuerst' },
      { value: 'price-asc',  label: 'Preis aufsteigend' },
      { value: 'price-desc', label: 'Preis absteigend' },
      { value: 'oldest',     label: 'Älteste zuerst' },
    ];

    // Kleines Dropdown-Menü erstellen
    const menu = document.createElement('div');
    menu.className = 'sort-mobile-menu';
    menu.style.cssText = 'display:none;position:absolute;top:100%;left:0;background:var(--color-bg);border:1px solid var(--color-border);border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.12);z-index:100;min-width:180px;overflow:hidden;margin-top:6px;';
    sortOptions.forEach(opt => {
      const btn = document.createElement('button');
      btn.textContent = opt.label;
      btn.dataset.value = opt.value;
      btn.style.cssText = 'display:block;width:100%;padding:12px 16px;text-align:left;font-size:0.875rem;background:none;border:none;cursor:pointer;color:var(--color-text);';
      btn.addEventListener('mouseenter', () => btn.style.background = 'var(--color-bg-alt)');
      btn.addEventListener('mouseleave', () => btn.style.background = 'none');
      btn.addEventListener('click', () => {
        const sortSelect = document.getElementById('sort-select');
        if (sortSelect) { sortSelect.value = opt.value; sortSelect.dispatchEvent(new Event('change')); }
        sortToggle.textContent = opt.label;
        menu.style.display = 'none';
        sortToggle.classList.remove('active');
      });
      menu.appendChild(btn);
    });

    sortToggle.parentElement.style.position = 'relative';
    sortToggle.parentElement.appendChild(menu);

    sortToggle.addEventListener('click', e => {
      e.stopPropagation();
      const open = menu.style.display === 'block';
      menu.style.display = open ? 'none' : 'block';
      sortToggle.classList.toggle('active', !open);
    });
    document.addEventListener('click', () => {
      menu.style.display = 'none';
      sortToggle.classList.remove('active');
    });
  }
}

// --- Notification Toast ---
function showNotification(msg, duration = 3000) {
  let el = document.querySelector('.notification');
  if (!el) {
    el = document.createElement('div');
    el.className = 'notification';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.classList.add('visible');
  clearTimeout(el._timeout);
  el._timeout = setTimeout(() => el.classList.remove('visible'), duration);
}

// ============================================================
// CATALOG PAGE LOGIC
// ============================================================
function initCatalog() {
  const grid = document.getElementById('product-grid');
  if (!grid || typeof products === 'undefined') return;

  // State
  let state = {
    search: '',
    sort: 'newest',
    filters: {
      kategorie:     [],
      unterkategorie:[],
      größe:         [],
      marke:         [],
      farbe:         [],
      zustand:       [],
      saison:        [],
      stil:          [],
      verfügbarkeit: [],
      preisMin:      '',
      preisMax:      ''
    }
  };

  // URL-Parameter als initialen Filter setzen (z.B. ?kategorie=Schuhe)
  const urlParams = new URLSearchParams(window.location.search);
  const urlKategorie = urlParams.get('kategorie');
  if (urlKategorie) state.filters.kategorie = [urlKategorie];

  // Populate filter checkboxes from product data
  buildFilterOptions();

  // Wire up controls
  const searchInput = document.getElementById('search-input');
  const sortSelect  = document.getElementById('sort-select');

  searchInput?.addEventListener('input', e => {
    state.search = e.target.value.trim().toLowerCase();
    render();
  });

  sortSelect?.addEventListener('change', e => {
    state.sort = e.target.value;
    render();
  });

  // Checkbox filters (both sidebar and drawer)
  document.querySelectorAll('.filter-checkbox').forEach(cb => {
    cb.addEventListener('change', () => {
      const field = cb.dataset.field;
      const val   = cb.dataset.value;
      const arr   = state.filters[field];
      if (!arr) return;

      if (cb.checked) {
        if (!arr.includes(val)) arr.push(val);
      } else {
        const idx = arr.indexOf(val);
        if (idx > -1) arr.splice(idx, 1);
      }
      syncCheckboxes(field, val, cb.checked);
      render();
    });
  });

  // Price range
  document.getElementById('price-min')?.addEventListener('input', e => {
    state.filters.preisMin = e.target.value;
    render();
  });
  document.getElementById('price-max')?.addEventListener('input', e => {
    state.filters.preisMax = e.target.value;
    render();
  });

  // Reset filters
  document.querySelectorAll('[data-reset-filters]').forEach(btn => {
    btn.addEventListener('click', () => {
      state.filters = {
        kategorie:[], unterkategorie:[], größe:[], marke:[],
        farbe:[], zustand:[], saison:[], stil:[], verfügbarkeit:[],
        preisMin:'', preisMax:''
      };
      document.querySelectorAll('.filter-checkbox').forEach(cb => cb.checked = false);
      document.getElementById('price-min') && (document.getElementById('price-min').value = '');
      document.getElementById('price-max') && (document.getElementById('price-max').value = '');
      state.search = '';
      if (searchInput) searchInput.value = '';
      render();
    });
  });

  function syncCheckboxes(field, val, checked) {
    document.querySelectorAll(`.filter-checkbox[data-field="${field}"][data-value="${val}"]`).forEach(cb => {
      cb.checked = checked;
    });
  }

  function buildFilterOptions() {
    const fields = ['kategorie','unterkategorie','größe','marke','farbe','zustand','saison','stil','verfügbarkeit'];
    fields.forEach(field => {
      const values = getUniqueValues(field);
      const containers = document.querySelectorAll(`[data-filter-field="${field}"]`);
      containers.forEach(container => {
        container.innerHTML = values.map(v => `
          <label class="filter-option">
            <input type="checkbox" class="filter-checkbox" data-field="${field}" data-value="${v}">
            <span>${v}</span>
          </label>`
        ).join('');
      });
    });

    // Re-attach events after building
    document.querySelectorAll('.filter-checkbox').forEach(cb => {
      cb.addEventListener('change', () => {
        const field = cb.dataset.field;
        const val   = cb.dataset.value;
        const arr   = state.filters[field];
        if (!arr) return;
        if (cb.checked) { if (!arr.includes(val)) arr.push(val); }
        else { const i = arr.indexOf(val); if (i > -1) arr.splice(i, 1); }
        syncCheckboxes(field, val, cb.checked);
        render();
      });
    });
  }

  function getFiltered() {
    return products.filter(p => {
      // Search
      if (state.search) {
        const hay = [p.titel,p.marke,p.farbe,p.kategorie,p.unterkategorie,
          p.beschreibung,p.material,p.stil,p.größe].join(' ').toLowerCase();
        if (!hay.includes(state.search)) return false;
      }
      // Checkbox filters
      const f = state.filters;
      if (f.kategorie.length     && !f.kategorie.includes(p.kategorie))         return false;
      if (f.unterkategorie.length && !f.unterkategorie.includes(p.unterkategorie)) return false;
      if (f.größe.length         && !f.größe.includes(p.größe))                 return false;
      if (f.marke.length         && !f.marke.includes(p.marke))                 return false;
      if (f.farbe.length         && !f.farbe.includes(p.farbe))                 return false;
      if (f.zustand.length       && !f.zustand.includes(p.zustand))             return false;
      if (f.saison.length        && !f.saison.includes(p.saison))               return false;
      if (f.stil.length          && !f.stil.includes(p.stil))                   return false;
      if (f.verfügbarkeit.length && !f.verfügbarkeit.includes(p.verfügbarkeit)) return false;
      if (f.preisMin !== '' && p.preis < Number(f.preisMin)) return false;
      if (f.preisMax !== '' && p.preis > Number(f.preisMax)) return false;
      return true;
    });
  }

  function getSorted(arr) {
    return [...arr].sort((a, b) => {
      switch (state.sort) {
        case 'price-asc':  return a.preis - b.preis;
        case 'price-desc': return b.preis - a.preis;
        case 'newest':     return new Date(b.erstellt_am) - new Date(a.erstellt_am);
        case 'oldest':     return new Date(a.erstellt_am) - new Date(b.erstellt_am);
        default:           return 0;
      }
    });
  }

  function render() {
    const filtered = getSorted(getFiltered());
    const resultsEl = document.getElementById('results-count');
    if (resultsEl) {
      resultsEl.textContent = `${filtered.length} ${filtered.length === 1 ? 'Artikel' : 'Artikel'}`;
    }

    if (filtered.length === 0) {
      grid.innerHTML = `
        <div class="empty-state" style="grid-column:1/-1">
          <p>Keine Artikel gefunden.</p>
          <button class="btn btn-secondary btn-sm" data-reset-filters>Filter zurücksetzen</button>
        </div>`;
      document.querySelector('[data-reset-filters]')?.addEventListener('click', () => {
        state.filters = {
          kategorie:[], unterkategorie:[], größe:[], marke:[],
          farbe:[], zustand:[], saison:[], stil:[], verfügbarkeit:[],
          preisMin:'', preisMax:''
        };
        document.querySelectorAll('.filter-checkbox').forEach(cb => cb.checked = false);
        state.search = '';
        if (searchInput) searchInput.value = '';
        render();
      });
      return;
    }

    grid.innerHTML = filtered.map(p => renderCard(p)).join('');
  }

  render();
}

function renderCard(p) {
  const statusClass = `status-${p.verfügbarkeit}`;
  const statusLabel = { verfügbar: 'Verfügbar', reserviert: 'Reserviert', verkauft: 'Verkauft' }[p.verfügbarkeit] || p.verfügbarkeit;
  const soldClass   = p.verfügbarkeit === 'verkauft' ? 'is-sold' : '';

  const imgHTML = (p.bilder && p.bilder.length)
    ? `<img src="${p.bilder[0]}" alt="${p.titel}" loading="lazy" onerror="this.parentElement.innerHTML='<div class=&quot;product-card-image-placeholder&quot;>${p.unterkategorie}</div>'">`
    : `<div class="product-card-image-placeholder">${p.unterkategorie}</div>`;

  const origPrice = p.ursprünglicher_preis
    ? `<span class="original-price">${p.ursprünglicher_preis} €</span>` : '';

  const inList = isInMerkliste(p.id);
  const heartFill = inList ? 'currentColor' : 'none';
  const heartStroke = inList ? 'var(--color-cta)' : 'rgba(255,255,255,0.95)';
  const wishlistBtn = `
    <button class="wishlist-btn${inList ? ' active' : ''}"
      onclick="event.stopPropagation();toggleWishlistBtn(this,${p.id})"
      title="${inList ? 'Von Merkliste entfernen' : 'Zur Merkliste hinzufügen'}"
      aria-label="${inList ? 'Von Merkliste entfernen' : 'Zur Merkliste hinzufügen'}">
      <svg viewBox="0 0 24 24" fill="${heartFill}" stroke="${heartStroke}" stroke-width="1.8">
        <path stroke-linecap="round" stroke-linejoin="round"
          d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.27 2 8.5 2 5.41 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.08C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.41 22 8.5c0 3.77-3.4 6.86-8.55 11.53L12 21.35z"/>
      </svg>
    </button>`;

  const mängelBadge = (p.mängel && p.mängel?.toLowerCase() !== 'keine')
    ? `<span class="product-card-maengel">⚠ Mängel</span>` : '';

  return `
    <a href="product.html?id=${p.id}" class="product-card ${soldClass}" aria-label="${p.titel} – ${p.preis} €">
      <div class="product-card-image">
        ${imgHTML}
        <span class="product-card-status ${statusClass}">${statusLabel}</span>
        ${mängelBadge}
        ${wishlistBtn}
      </div>
      <div class="product-card-body">
        <div class="product-card-title">${p.titel}</div>
        <div class="product-card-meta">
          <span>Gr. ${p.größe}</span>
          <span>${p.zustand}</span>
        </div>
        <div class="product-card-price">${p.preis} €${origPrice}</div>
      </div>
    </a>`;
}

// ============================================================
// PRODUCT DETAIL PAGE LOGIC
// ============================================================
function initProductDetail() {
  const container = document.getElementById('product-detail-root');
  if (!container || typeof products === 'undefined') return;

  const params = new URLSearchParams(window.location.search);
  const id     = params.get('id');
  const p      = getProductById(id);

  if (!p) {
    container.innerHTML = `
      <div class="empty-state" style="padding:80px 0;text-align:center">
        <p>Artikel nicht gefunden.</p>
        <a href="catalog.html" class="btn btn-secondary btn-sm">Zurück zum Katalog</a>
      </div>`;
    return;
  }

  document.title = `${p.titel} – Second Hand`;

  const statusLabel = { verfügbar:'Verfügbar', reserviert:'Reserviert', verkauft:'Verkauft' }[p.verfügbarkeit];
  const statusClass = `status-${p.verfügbarkeit}`;

  const mainImg = (p.bilder && p.bilder.length) ? p.bilder[0] : '';
  const thumbsHTML = (p.bilder && p.bilder.length > 1) ? p.bilder.map((src, i) => `
    <button class="gallery-thumb ${i===0?'active':''}" data-index="${i}" onclick="switchImage(${i})" aria-label="Bild ${i+1}">
      <img src="${src}" alt="${p.titel} – Bild ${i+1}" onerror="this.style.display='none'">
    </button>`
  ).join('') : '';

  const origPrice = p.ursprünglicher_preis
    ? `<span class="price-original">${p.ursprünglicher_preis} €</span>` : '';

  const mängelText = p.mängel && p.mängel?.toLowerCase() !== 'keine'
    ? `<div class="product-info-notice">⚠ Hinweise zu Mängeln: ${p.mängel}</div>` : '';

  const buyDisabled = p.verfügbarkeit !== 'verfügbar' ? 'disabled style="opacity:0.5;cursor:not-allowed"' : '';

  container.innerHTML = `
    <div class="product-detail-breadcrumb">
      <a href="catalog.html">Alle Artikel</a>
      <span class="product-detail-breadcrumb-sep">/</span>
      <a href="catalog.html">${p.kategorie}</a>
      <span class="product-detail-breadcrumb-sep">/</span>
      <span>${p.titel}</span>
    </div>

    <div class="product-detail-grid">
      <div class="product-gallery">
        <div class="gallery-main" id="gallery-main" onclick="openLightbox(window._galleryIndex||0)" title="Bild vergrößern">
          ${mainImg
            ? `<img src="${mainImg}" alt="${p.titel}" id="gallery-main-img" onerror="this.outerHTML='<div class=\\'hero-image-placeholder\\'>${p.unterkategorie}</div>'">`
            : `<div class="hero-image-placeholder">${p.unterkategorie}</div>`}
          <span class="gallery-zoom-hint">Vergrößern</span>
        </div>
        ${thumbsHTML ? `<div class="gallery-thumbs">${thumbsHTML}</div>` : ''}
      </div>

      <div class="product-info">
        <div class="product-info-status ${statusClass}">
          <span class="status-dot"></span>
          ${statusLabel}
        </div>

        <h1 class="product-info-title">${p.titel}</h1>
        ${p.marke && p.marke !== 'Unbekannt'
          ? `<div class="product-info-brand">${p.marke}</div>` : ''}

        <div class="product-info-price">
          <span class="price-current">${p.preis} €</span>
          ${origPrice}
        </div>

        <div class="product-info-divider"></div>

        <div class="spec-table">
          <span class="spec-label">Größe</span>
          <span class="spec-value">${p.größe}</span>
          <span class="spec-label">Farbe</span>
          <span class="spec-value">${p.farbe}</span>
          <span class="spec-label">Material</span>
          <span class="spec-value">${p.material}</span>
          <span class="spec-label">Zustand</span>
          <span class="spec-value">${p.zustand}</span>
          <span class="spec-label">Saison</span>
          <span class="spec-value">${p.saison}</span>
          ${p.maße && p.maße.trim() ? `<span class="spec-label">Maße</span><span class="spec-value">${p.maße}</span>` : ''}
          ${p.stil ? `<span class="spec-label">Stil</span><span class="spec-value">${p.stil}</span>` : ''}
        </div>

        <div class="product-info-divider"></div>

        <p class="product-info-description">${p.beschreibung}</p>
        ${p.besonderheiten ? `<p class="product-info-description"><strong style="font-weight:500;color:var(--color-text)">Besonderheiten:</strong> ${p.besonderheiten}</p>` : ''}
        ${mängelText}

        <div class="product-info-actions">
          <a href="contact.html?artikel=${encodeURIComponent(p.titel)}" class="btn btn-primary btn-full" ${buyDisabled}>
            Kaufanfrage senden
          </a>
          <button onclick="toggleWishlistBtnDetail(this,${p.id})"
            class="btn btn-secondary btn-full wishlist-btn-full${isInMerkliste(p.id) ? ' active' : ''}">
            <svg viewBox="0 0 24 24" fill="${isInMerkliste(p.id) ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="1.8" width="16" height="16">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.27 2 8.5 2 5.41 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.08C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.41 22 8.5c0 3.77-3.4 6.86-8.55 11.53L12 21.35z"/>
            </svg>
            <span>${isInMerkliste(p.id) ? 'Von Merkliste entfernen' : 'Zur Merkliste hinzufügen'}</span>
          </button>
          <a href="contact.html?artikel=${encodeURIComponent(p.titel)}&frage=1" class="btn btn-secondary btn-full">
            Frage zum Artikel stellen
          </a>
        </div>

        <div class="shipping-info">
          <div class="shipping-info-item">
            <span class="shipping-info-label">Versand</span>
            <span class="shipping-info-value">Möglich, Versandkosten trägt die Käuferin / der Käufer. Versand per Hermes oder DHL.</span>
          </div>
          <div class="shipping-info-item">
            <span class="shipping-info-label">Abholung</span>
            <span class="shipping-info-value">Persönliche Abholung in Osnabrück möglich – nach Absprache.</span>
          </div>
          <div class="shipping-info-item">
            <span class="shipping-info-label">Zahlung</span>
            <span class="shipping-info-value">PayPal (Freunde & Familie), Überweisung oder bar bei Abholung.</span>
          </div>
        </div>

        <p class="product-info-notice">
          Privatverkauf – keine Rücknahme oder Gewährleistung, soweit gesetzlich zulässig.
          Alle Angaben nach bestem Wissen und Gewissen.
        </p>
      </div>
    </div>`;

  // Gallery: Index tracken, Bild wechseln, Lightbox öffnen
  window._galleryIndex = 0;

  window.switchImage = function(index) {
    const img    = document.getElementById('gallery-main-img');
    const thumbs = document.querySelectorAll('.gallery-thumb');
    if (!img || !p.bilder[index]) return;
    img.src = p.bilder[index];
    window._galleryIndex = index;
    thumbs.forEach((t, i) => t.classList.toggle('active', i === index));
  };

  // Lightbox initialisieren
  if (p.bilder && p.bilder.length) {
    // Mängel-Bilder: per Konvention das letzte Bild, wenn Mängel vorhanden
    const mängelStart = (p.mängel && p.mängel?.toLowerCase() !== 'keine' && p.bilder.length > 1)
      ? p.bilder.length - 1 : -1;
    initLightbox(p.bilder, mängelStart);
  }
}

// ============================================================
// CONTACT FORM — mit Mehrfachauswahl per Chips
// ============================================================
function initContact() {
  const form     = document.getElementById('contact-form');
  const success  = document.getElementById('form-success');
  if (!form) return;

  const params      = new URLSearchParams(window.location.search);
  const artikelParam = params.get('artikel');
  const frage        = params.get('frage');

  const chipsWrap    = document.getElementById('artikel-chips');
  const dropdown     = document.getElementById('artikel-dropdown');
  const hiddenInput  = document.getElementById('artikel');
  const msgField     = form.querySelector('[name="nachricht"]');

  // --- Ausgewählte Artikel (Set verhindert Duplikate) ---
  const selected = new Set();

  // --- Dropdown mit verfügbaren Artikeln befüllen ---
  if (typeof products !== 'undefined' && dropdown) {
    products
      .filter(p => p.verfügbarkeit !== 'verkauft')
      .forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.titel;
        opt.textContent = `${p.titel} – ${p.preis} €`;
        dropdown.appendChild(opt);
      });
  }

  // --- Chip hinzufügen ---
  function addChip(titel) {
    if (!titel || selected.has(titel)) return;
    selected.add(titel);

    const chip = document.createElement('span');
    chip.className = 'artikel-chip';
    chip.innerHTML = `
      ${titel}
      <button type="button" class="artikel-chip-remove" aria-label="${titel} entfernen" data-titel="${titel}">✕</button>
    `;
    chip.querySelector('.artikel-chip-remove').addEventListener('click', () => {
      selected.delete(titel);
      chip.remove();
      updateHidden();
      updateMessage();
    });
    chipsWrap.appendChild(chip);
    updateHidden();
    updateMessage();
  }

  // --- Verstecktes Feld & Nachricht synchronisieren ---
  function updateHidden() {
    if (hiddenInput) hiddenInput.value = [...selected].join(', ');
  }

  function updateMessage() {
    if (!msgField) return;
    const list = [...selected];
    if (list.length === 0) {
      msgField.value = '';
      return;
    }
    if (frage) {
      const titel = list[0];
      msgField.value = `Ich hätte eine Frage zum Artikel „${titel}":\n\n`;
    } else if (list.length === 1) {
      msgField.value = `Ich interessiere mich für den Artikel „${list[0]}" und möchte gerne eine Kaufanfrage stellen.\n\n`;
    } else {
      const aufzählung = list.map(t => `„${t}"`).join(', ');
      msgField.value = `Ich interessiere mich für folgende Artikel und möchte gerne eine Kaufanfrage stellen:\n${aufzählung}\n\n`;
    }
  }

  // --- Dropdown-Auswahl ---
  if (dropdown) {
    dropdown.addEventListener('change', () => {
      const val = dropdown.value;
      if (val) {
        addChip(val);
        dropdown.value = ''; // Zurücksetzen
      }
    });
  }

  // --- Vorab aus URL befüllen (unterstützt mehrere ?artikel= Parameter, z.B. von Merkliste) ---
  params.getAll('artikel').forEach(titel => addChip(decodeURIComponent(titel)));

  // --- Formular absenden ---
  form.addEventListener('submit', e => {
    e.preventDefault();
    const data = new FormData(form);
    fetch('https://formspree.io/f/mgobzrzr', { method: 'POST',
      headers: { 'Accept': 'application/json' }, body: data })
      .then(() => {
        form.style.display = 'none';
        success.classList.add('visible');
        window.scrollTo({ top: success.offsetTop - 80, behavior: 'smooth' });
      })
      .catch(() => {
        form.style.display = 'none';
        success.classList.add('visible');
        window.scrollTo({ top: success.offsetTop - 80, behavior: 'smooth' });
      });
  });
}

// ============================================================
// LIGHTBOX
// ============================================================
function initLightbox(images, mängelStart) {
  // Einmal in den Body einfügen
  if (!document.getElementById('lightbox')) {
    document.body.insertAdjacentHTML('beforeend', `
      <div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Bildvergrößerung">
        <button class="lightbox-close" id="lightbox-close" aria-label="Schließen">✕</button>
        <button class="lightbox-nav lightbox-prev" id="lightbox-prev" aria-label="Vorheriges Bild">&#8249;</button>
        <img class="lightbox-img" id="lightbox-img" alt="">
        <span class="lightbox-maengel-label" id="lightbox-maengel" style="display:none">⚠ Mängelfoto</span>
        <button class="lightbox-nav lightbox-next" id="lightbox-next" aria-label="Nächstes Bild">&#8250;</button>
        <p class="lightbox-counter" id="lightbox-counter"></p>
      </div>`);
  }

  const lb       = document.getElementById('lightbox');
  const lbImg    = document.getElementById('lightbox-img');
  const lbClose  = document.getElementById('lightbox-close');
  const lbPrev   = document.getElementById('lightbox-prev');
  const lbNext   = document.getElementById('lightbox-next');
  const lbCount  = document.getElementById('lightbox-counter');
  const lbMaengel = document.getElementById('lightbox-maengel');
  let current = 0;

  function show(i) {
    current = Math.max(0, Math.min(i, images.length - 1));
    lbImg.src = images[current];
    lbImg.alt = `Bild ${current + 1} von ${images.length}`;
    lbCount.textContent = images.length > 1 ? `${current + 1} / ${images.length}` : '';
    lbPrev.disabled = current === 0;
    lbNext.disabled = current === images.length - 1;
    lbMaengel.style.display = (mängelStart !== -1 && current >= mängelStart) ? '' : 'none';
  }

  window.openLightbox = function(index) {
    show(index != null ? index : window._galleryIndex || 0);
    lb.classList.add('open');
    document.body.style.overflow = 'hidden';
    lbImg.focus && lbImg.focus();
  };

  lbClose.onclick = closeLb;
  lb.onclick = (e) => { if (e.target === lb) closeLb(); };
  lbPrev.onclick = (e) => { e.stopPropagation(); show(current - 1); };
  lbNext.onclick = (e) => { e.stopPropagation(); show(current + 1); };

  function closeLb() {
    lb.classList.remove('open');
    document.body.style.overflow = '';
  }

  // Tastatur: Esc / Pfeiltasten
  document.addEventListener('keydown', (e) => {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape')      closeLb();
    if (e.key === 'ArrowLeft')   show(current - 1);
    if (e.key === 'ArrowRight')  show(current + 1);
  });

  // Thumbnails auf Produktseite: Mängel-Label anzeigen
  if (mängelStart !== -1) {
    document.querySelectorAll('.gallery-thumb').forEach((thumb, i) => {
      if (i >= mängelStart) {
        thumb.style.position = 'relative';
        thumb.insertAdjacentHTML('beforeend',
          `<span class="gallery-thumb-maengel">Mängel</span>`);
      }
    });
  }

  // Keine Nav-Buttons bei Einzelbild
  if (images.length <= 1) {
    lbPrev.style.display = 'none';
    lbNext.style.display = 'none';
  } else {
    lbPrev.style.display = '';
    lbNext.style.display = '';
  }
}

// ============================================================
// MERKLISTE SEITE
// ============================================================
function initMerkliste() {
  const grid = document.getElementById('merkliste-grid');
  if (!grid) return;

  window.renderMerklisteGrid = function() {
    const ids   = getMerkliste();
    const saved = ids.map(id => getProductById(id)).filter(Boolean);
    const empty   = document.getElementById('merkliste-empty');
    const allBtn  = document.getElementById('merkliste-alle-btn');
    const counter = document.getElementById('merkliste-counter');

    if (saved.length === 0) {
      grid.innerHTML = '';
      if (empty)   empty.style.display   = '';
      if (allBtn)  allBtn.style.display  = 'none';
    } else {
      if (empty)  empty.style.display = 'none';
      if (counter) counter.textContent = `${saved.length} Artikel`;

      // Alle anfragen: alle Titel als Params übergeben
      if (allBtn) {
        const q = saved.map(p => 'artikel=' + encodeURIComponent(p.titel)).join('&');
        allBtn.href = 'contact.html?' + q;
        allBtn.style.display = '';
      }

      grid.innerHTML = saved.map(p => renderCard(p)).join('');
    }
    updateMerklisteBadge();
  };

  renderMerklisteGrid();
}

// --- Init on DOM ready ---
document.addEventListener('DOMContentLoaded', () => {
  initNav();
  updateMerklisteBadge();
  initFaq();
  initFilterGroups();
  initFilterDrawer();
  initCatalog();
  initProductDetail();
  initContact();
  initMerkliste();
});
