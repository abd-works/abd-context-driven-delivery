// PROTOTYPE: stub — Increment 2 click-and-collect demo; no production services.

const IMG = {
  harness: [
    'https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=800&q=80',
    'https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=800&q=80',
    'https://images.unsplash.com/photo-1560807707-8cc77767d783?w=800&q=80',
  ],
  treats: [
    'https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=800&q=80',
    'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=800&q=80',
  ],
  filter: [
    'https://images.unsplash.com/photo-1522069169874-58d6611aa0a6?w=800&q=80',
  ],
};

const FIXTURES = {
  products: {
    'PET-HAR-001': {
      sku: 'PET-HAR-001',
      name: 'Premium Dog Harness',
      category: 'Walking gear',
      brand: 'WalkRight',
      price: 34.99,
      stock: 22,
      backorder: false,
      description: 'Padded adjustable harness for daily walks. Reflective stitching and quick-release buckle.',
      weight: '320g',
      dimensions: 'M — 45–65 cm',
      images: IMG.harness,
    },
    'PET-TRT-042': {
      sku: 'PET-TRT-042',
      name: 'Salmon Cat Treats',
      category: 'Treats',
      brand: 'PurrDelight',
      price: 4.99,
      stock: 48,
      backorder: false,
      description: 'Grain-free salmon bites — high protein, no artificial colours.',
      weight: '75g',
      dimensions: 'Pouch',
      images: IMG.treats,
    },
    'PET-FLT-099': {
      sku: 'PET-FLT-099',
      name: 'Exotic Fish Filter',
      category: 'Aquarium gear',
      brand: 'AquaFlow',
      price: 89.99,
      stock: 0,
      backorder: false,
      description: 'High-flow canister filter for freshwater tanks up to 200L.',
      weight: '1.2kg',
      dimensions: '28 × 18 × 12 cm',
      images: IMG.filter,
    },
  },
  stores: [
    {
      code: 'STR-001',
      name: 'PawPlace Camden',
      address: '42 High Street, London NW1 8QP',
      city: 'London',
      postcode: 'NW1 8QP',
      hours: 'Mon–Sat 9:00–18:00',
      distance: null,
      image: 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=200&q=80',
    },
    {
      code: 'STR-002',
      name: 'PawPlace Bristol',
      address: '15 Harbour Road, Bristol BS1 4DJ',
      city: 'Bristol',
      postcode: 'BS1 4DJ',
      hours: 'Mon–Sat 9:00–17:30',
      distance: null,
      image: 'https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=200&q=80',
    },
  ],
};

const DEMO = {
  productSku: 'PET-HAR-001',
  galleryIndex: 0,
  paymentUnavailable: false,
  collectionElapsed: false,
};

function productThumb(sku) {
  const p = FIXTURES.products[sku];
  return p?.images?.[0] ?? '';
}

const STORAGE = {
  cart: 'pawplace-cart-v2',
  checkout: 'pawplace-checkout-v2',
  staff: 'pawplace-staff-queue-v2',
};

function money(n) {
  return `£${n.toFixed(2)}`;
}

function loadCart() {
  try {
    return JSON.parse(sessionStorage.getItem(STORAGE.cart) || '[]');
  } catch {
    return [];
  }
}

function saveCart(items) {
  sessionStorage.setItem(STORAGE.cart, JSON.stringify(items));
}

function loadCheckout() {
  try {
    return JSON.parse(sessionStorage.getItem(STORAGE.checkout) || '{}');
  } catch {
    return {};
  }
}

function saveCheckout(data) {
  sessionStorage.setItem(STORAGE.checkout, JSON.stringify(data));
}

function cartBadgeCount(items) {
  return items.reduce((sum, i) => sum + i.quantity, 0);
}

function cartSubtotal(items) {
  return items.reduce((sum, i) => sum + i.quantity * i.unitPrice, 0);
}

function formatLinePrice(qty, unit) {
  return money(qty * unit);
}

function showToast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.hidden = false;
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => { el.hidden = true; }, 4000);
}

function showScreen(id) {
  document.querySelectorAll('.screen').forEach((s) => {
    s.hidden = s.id !== id;
  });
  const isStaff = id === 'screen-staff-queue' || id === 'screen-staff-order';
  document.querySelector('.site-header')?.toggleAttribute('hidden', isStaff);
  document.getElementById('promo-strip')?.toggleAttribute('hidden', isStaff);
  document.getElementById('site-footer')?.toggleAttribute('hidden', isStaff);
  window.location.hash = id.replace('screen-', '');
  renderAll();
}

function getProduct() {
  return FIXTURES.products[DEMO.productSku] || FIXTURES.products['PET-HAR-001'];
}

function addToCart(sku, qty = 1) {
  const p = FIXTURES.products[sku];
  if (!p || p.stock < 1) return;
  const items = loadCart();
  const existing = items.find((i) => i.sku === sku);
  if (existing) {
    const next = existing.quantity + qty;
    if (next > p.stock) return { error: `Only ${p.stock} available` };
    existing.quantity = next;
    existing.linePrice = existing.quantity * existing.unitPrice;
  } else {
    if (qty > p.stock) return { error: `Only ${p.stock} available` };
    items.push({
      sku,
      name: p.name,
      quantity: qty,
      unitPrice: p.price,
      linePrice: qty * p.price,
      maxStock: p.stock,
    });
  }
  saveCart(items);
  return { ok: true };
}

function updateCartQty(sku, qty) {
  const items = loadCart();
  const line = items.find((i) => i.sku === sku);
  if (!line) return;
  if (qty < 0) return { error: 'Quantity must be zero or more' };
  if (qty === 0) {
    saveCart(items.filter((i) => i.sku !== sku));
    return { ok: true };
  }
  if (qty > line.maxStock) return { error: `Only ${line.maxStock} available` };
  line.quantity = qty;
  line.linePrice = qty * line.unitPrice;
  saveCart(items);
  return { ok: true };
}

function removeCartItem(sku) {
  saveCart(loadCart().filter((i) => i.sku !== sku));
}

function resetSession() {
  sessionStorage.removeItem(STORAGE.cart);
  sessionStorage.removeItem(STORAGE.checkout);
  initStaffQueue();
  showToast('Session reset — cart cleared');
  showScreen('screen-product-page');
}

function updateNavBadge() {
  const count = cartBadgeCount(loadCart());
  const badge = document.getElementById('nav-cart-count');
  if (badge) badge.textContent = String(count);
}

function renderGallery(p) {
  const idx = Math.min(DEMO.galleryIndex, p.images.length - 1);
  const mainImg = document.getElementById('gallery-main-img');
  if (mainImg) {
    mainImg.src = p.images[idx];
    mainImg.alt = `${p.name} — image ${idx + 1}`;
  }
  const thumbs = document.getElementById('gallery-thumbs');
  if (thumbs) {
    thumbs.innerHTML = p.images
      .map(
        (url, i) => `<button type="button" class="gallery-thumb${i === idx ? ' active' : ''}" data-gallery-idx="${i}" aria-label="View image ${i + 1}">
          <img src="${url.replace('w=800', 'w=160')}" alt="">
        </button>`,
      )
      .join('');
  }
}

function renderProductPage() {
  const p = getProduct();
  const inStock = p.stock > 0;
  document.getElementById('product-name').textContent = p.name;
  const name2 = document.getElementById('product-name-2');
  if (name2) name2.textContent = p.name;
  document.getElementById('product-category').textContent = p.category;
  const priceEl = document.getElementById('product-price');
  if (priceEl) priceEl.textContent = money(p.price);
  document.getElementById('product-description').textContent = p.description;
  document.getElementById('product-weight').textContent = p.weight;
  document.getElementById('product-dimensions').textContent = p.dimensions;
  renderGallery(p);

  const stockBody = document.getElementById('stock-by-store-body');
  stockBody.innerHTML = FIXTURES.stores
    .map(
      (s) => `<div class="stock-card">
        <div><strong>${s.name}</strong><br><span style="color:var(--brand-muted);font-size:0.85rem">${s.address}</span></div>
        <span class="stock-badge ${inStock ? 'stock-badge--in' : 'stock-badge--out'}">${inStock ? 'In stock' : 'Out of stock — check back soon'}</span>
        <span style="color:var(--brand-muted);font-size:0.85rem">${s.distance ?? '—'}</span>
      </div>`,
    )
    .join('');

  const addBtn = document.getElementById('btn-add-to-cart');
  const msg = document.getElementById('unavailability-message');
  if (inStock) {
    addBtn.disabled = false;
    addBtn.hidden = false;
    msg.hidden = true;
  } else {
    addBtn.disabled = true;
    addBtn.hidden = false;
    addBtn.textContent = 'Out of stock';
    msg.hidden = false;
    msg.textContent = 'Out of stock — check back soon';
  }
  if (inStock) addBtn.textContent = 'Add to cart';
}

function renderCartPage() {
  const items = loadCart();
  const subtotal = cartSubtotal(items);
  const empty = items.length === 0;
  document.getElementById('cart-subtotal').textContent = money(subtotal);
  document.getElementById('cart-item-count').textContent = String(cartBadgeCount(items));

  const emptyEl = document.getElementById('cart-empty');
  const listEl = document.getElementById('cart-list-wrap');
  const checkoutBtn = document.getElementById('btn-proceed-checkout');

  if (empty) {
    emptyEl.hidden = false;
    listEl.hidden = true;
    checkoutBtn.disabled = true;
    return;
  }
  emptyEl.hidden = true;
  listEl.hidden = false;
  checkoutBtn.disabled = false;

  const container = document.getElementById('cart-items-body');
  container.innerHTML = items
    .map(
      (i) => `<article class="cart-line" data-sku="${i.sku}">
        <img src="${productThumb(i.sku).replace('w=800', 'w=160')}" alt="">
        <div>
          <div class="cart-line__name">${i.name}</div>
          <div class="cart-line__price">${money(i.unitPrice)} each</div>
          <label class="sr-only" for="qty-${i.sku}">Quantity for ${i.name}</label>
          <input id="qty-${i.sku}" class="qty-input" type="number" min="0" value="${i.quantity}" data-qty-input="${i.sku}">
        </div>
        <div style="text-align:right">
          <div style="font-weight:700;margin-bottom:0.5rem">${money(i.linePrice)}</div>
          <button type="button" class="btn btn-ghost" data-remove="${i.sku}">Remove</button>
        </div>
      </article>`,
    )
    .join('');

  document.getElementById('cart-validation').textContent = '';
}

function renderPickupStore() {
  const checkout = loadCheckout();
  const postcode = document.getElementById('pickup-postcode')?.value || checkout.postcode || '';
  const stores = FIXTURES.stores.map((s) => ({ ...s }));
  let prompt = '';
  if (postcode.trim().toUpperCase().startsWith('NW')) {
    stores[0].distance = '0.8 mi';
    stores[1].distance = '118 mi';
    stores.sort((a, b) => parseFloat(a.distance) - parseFloat(b.distance));
  } else if (!postcode.trim()) {
    prompt = 'Enter a postcode or share location for distance-sorted results';
  }

  const promptEl = document.getElementById('distance-prompt');
  if (prompt) {
    promptEl.textContent = prompt;
    promptEl.hidden = false;
  } else {
    promptEl.hidden = true;
  }
  const container = document.getElementById('pickup-stores-body');
  container.innerHTML = stores
    .map(
      (s) => {
        const selected = checkout.pickupStore?.code === s.code;
        return `<article class="store-card${selected ? ' is-selected' : ''}">
          <img class="store-card__img" src="${s.image}" alt="">
          <div>
            <h3>${s.name}</h3>
            <p>${s.address}</p>
            <p>${s.hours}${s.distance ? ` · ${s.distance}` : ''}</p>
          </div>
          <button type="button" class="btn ${selected ? 'btn-secondary' : 'btn-primary'}" data-select-store="${s.code}">
            ${selected ? 'Selected' : 'Select pickup store'}
          </button>
        </article>`;
      },
    )
    .join('');

  if (checkout.pickupStore) {
    document.getElementById('summary-pickup-name').textContent = checkout.pickupStore.name;
    document.getElementById('summary-pickup-address').textContent = checkout.pickupStore.address;
    document.getElementById('summary-collecting').textContent = `Collecting from ${checkout.pickupStore.name}`;
  } else {
    document.getElementById('summary-collecting').textContent = '';
  }
  document.getElementById('summary-cart-total').textContent = money(cartSubtotal(loadCart()));
}

function renderBilling() {
  const checkout = loadCheckout();
  const c = checkout.pickupStore;
  if (c) {
    document.getElementById('billing-pickup-summary').textContent = `${c.name} — ${c.address}`;
  }
  document.getElementById('billing-cart-total').textContent = money(cartSubtotal(loadCart()));
}

function renderPayment() {
  const checkout = loadCheckout();
  document.getElementById('review-billing').textContent =
    checkout.billingPreview || '—';
  document.getElementById('review-guest').textContent =
    checkout.guestEmail ? `${checkout.guestFirst} ${checkout.guestLast} <${checkout.guestEmail}>` : '—';
  document.getElementById('review-total').textContent = money(cartSubtotal(loadCart()));
  document.getElementById('payment-error').hidden = true;
  document.getElementById('payment-unavailable').hidden = true;
}

function renderConfirmation() {
  const checkout = loadCheckout();
  const items = loadCart();
  document.getElementById('confirm-order-number').textContent = checkout.orderNumber || 'ORD-2001';
  document.getElementById('confirm-total').textContent = money(cartSubtotal(items));
  document.getElementById('confirm-pickup').textContent = checkout.pickupStore
    ? `${checkout.pickupStore.name} — ${checkout.pickupStore.address} (${checkout.pickupStore.hours})`
    : '—';
  const container = document.getElementById('confirm-lines');
  container.innerHTML = items
    .map(
      (i) => `<article class="confirm-line">
        <img src="${productThumb(i.sku).replace('w=800', 'w=160')}" alt="">
        <div>
          <div style="font-weight:600">${i.name}</div>
          <div style="color:var(--brand-muted);font-size:0.85rem">Qty ${i.quantity}</div>
        </div>
        <strong>${money(i.linePrice)}</strong>
      </article>`,
    )
    .join('');
}

function initStaffQueue() {
  const defaultQueue = [
    {
      orderNumber: 'ORD-2001',
      date: '2025-05-06',
      status: 'confirmed',
      guestEmail: 'sarah.jones@example.com',
      store: 'STR-001',
      lines: [
        { name: 'Premium Dog Harness', sku: 'PET-HAR-001', qty: 1, total: 34.99 },
        { name: 'Salmon Cat Treats', sku: 'PET-TRT-042', qty: 2, total: 9.98 },
      ],
    },
    {
      orderNumber: 'ORD-2002',
      date: '2025-05-07',
      status: 'confirmed',
      guestEmail: 'tom.brown@example.com',
      store: 'STR-001',
      lines: [{ name: 'Exotic Fish Filter', sku: 'PET-FLT-099', qty: 1, total: 89.99, stockWarn: true }],
    },
  ];
  sessionStorage.setItem(STORAGE.staff, JSON.stringify(defaultQueue));
}

function loadStaffQueue() {
  try {
    return JSON.parse(sessionStorage.getItem(STORAGE.staff) || '[]');
  } catch {
    return [];
  }
}

function saveStaffQueue(q) {
  sessionStorage.setItem(STORAGE.staff, JSON.stringify(q));
}

function renderStaffQueue() {
  const q = loadStaffQueue().filter((o) => o.status !== 'collected');
  const heading = document.getElementById('queue-heading');
  const empty = document.getElementById('queue-empty');
  const table = document.getElementById('queue-table-wrap');

  if (q.length === 0) {
    heading.textContent = 'All orders fulfilled';
    empty.hidden = false;
    table.hidden = true;
    return;
  }
  heading.textContent = 'click-and-collect queue';
  empty.hidden = true;
  table.hidden = false;

  const sorted = [...q].sort((a, b) => a.date.localeCompare(b.date));
  const tbody = document.getElementById('queue-body');
  tbody.innerHTML = sorted
    .map(
      (o, idx) => `<tr>
        <td>${idx + 1}</td>
        <td><a href="#" data-goto-order="${o.orderNumber}">${o.orderNumber}</a></td>
        <td>${o.lines.map((l) => `${l.name} ×${l.qty}`).join(', ')}</td>
        <td>${o.guestEmail}</td>
        <td><span class="status-pill">${o.status}</span></td>
      </tr>`,
    )
    .join('');
}

function renderStaffOrder(orderNumber) {
  const order = loadStaffQueue().find((o) => o.orderNumber === orderNumber);
  const panel = document.getElementById('staff-order-panel');
  if (!order) {
    panel.innerHTML = '<p>Order not found.</p>';
    return;
  }
  let outreach = '';
  if (DEMO.collectionElapsed && order.status === 'ready for pickup') {
    outreach = '<p class="message-info">Contact customer — collection window elapsed</p>';
  }

  const lineCards = order.lines
    .map((l) => {
      const thumb = productThumb(l.sku);
      const warn = l.stockWarn
        ? '<span class="stock-warn">Out of stock at this store</span>'
        : '';
      return `<article class="cart-line" style="margin-bottom:0.5rem">
        ${thumb ? `<img src="${thumb.replace('w=800', 'w=160')}" alt="">` : '<div style="width:72px"></div>'}
        <div>
          <div class="cart-line__name">${l.name}</div>
          <div class="cart-line__price">Qty ${l.qty}</div>
          ${warn}
        </div>
        <strong>${money(l.total)}</strong>
      </article>`;
    })
    .join('');

  const statusClass = order.status === 'ready for pickup' ? 'status-pill status-pill--ready' : 'status-pill';

  panel.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;margin-bottom:1.25rem">
      <div>
        <p style="margin:0 0 0.25rem;color:var(--brand-muted);font-size:0.85rem">Order</p>
        <h2 style="margin:0;font-size:1.35rem">${order.orderNumber}</h2>
      </div>
      <span class="${statusClass}">${order.status}</span>
    </div>
    <p style="margin:0 0 1.25rem"><strong>Guest:</strong> ${order.guestEmail}</p>
    ${outreach}
    <h3 style="font-size:0.95rem;margin:0 0 0.75rem">Line items</h3>
    ${lineCards}
    <div style="margin-top:1.25rem;display:flex;gap:0.5rem;flex-wrap:wrap">
      ${order.status === 'confirmed' ? '<button type="button" class="btn btn-primary" id="btn-mark-prepared">Mark prepared</button>' : ''}
      ${order.status === 'ready for pickup' ? '<button type="button" class="btn btn-primary" id="btn-confirm-handoff">Confirm handoff</button>' : ''}
      <button type="button" class="btn btn-ghost" id="btn-back-queue">Back to queue</button>
    </div>`;

  document.getElementById('btn-back-queue')?.addEventListener('click', () => showScreen('screen-staff-queue'));
  document.getElementById('btn-mark-prepared')?.addEventListener('click', () => {
    order.status = 'ready for pickup';
    saveStaffQueue(loadStaffQueue());
    showToast('Pickup Fulfillment: ready for pickup');
    renderStaffOrder(orderNumber);
  });
  document.getElementById('btn-confirm-handoff')?.addEventListener('click', () => {
    order.status = 'collected';
    saveStaffQueue(loadStaffQueue());
    showToast('Order collected');
    showScreen('screen-staff-queue');
  });
}

function renderAll() {
  updateNavBadge();
  renderProductPage();
  renderCartPage();
  renderPickupStore();
  renderBilling();
  renderPayment();
  renderConfirmation();
  renderStaffQueue();
  const checkout = loadCheckout();
  if (checkout.viewOrder) renderStaffOrder(checkout.viewOrder);
}

function validateGuestAndBilling() {
  const email = document.getElementById('guest-email').value.trim();
  const first = document.getElementById('guest-first').value.trim();
  const last = document.getElementById('guest-last').value.trim();
  const err = document.getElementById('guest-email-error');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    err.textContent = 'Please enter a valid email address';
    err.hidden = false;
    return false;
  }
  err.hidden = true;

  const a1 = document.getElementById('bill-line1').value.trim();
  const city = document.getElementById('bill-city').value.trim();
  const postcode = document.getElementById('bill-postcode').value.trim();
  const country = document.getElementById('bill-country').value.trim();
  document.getElementById('bill-line1-error').hidden = !!a1;
  document.getElementById('bill-line1-error').textContent = a1 ? '' : 'Address line 1 is required';
  document.getElementById('bill-postcode-error').hidden = !!postcode;
  document.getElementById('bill-postcode-error').textContent = postcode ? '' : 'Postcode is required';
  if (!a1 || !postcode || !city || !country) return false;

  const checkout = loadCheckout();
  checkout.guestEmail = email;
  checkout.guestFirst = first;
  checkout.guestLast = last;
  checkout.billingPreview = `${a1}, ${document.getElementById('bill-line2').value || ''}, ${city}, ${document.getElementById('bill-county').value}, ${postcode}`;
  saveCheckout(checkout);
  // PROTOTYPE: stub — billing not persisted after checkout
  console.log('PROTOTYPE: billing address copied to order only; not persisted for guest');
  return true;
}

function validateCard() {
  const num = document.getElementById('card-number').value.replace(/\s/g, '');
  const exp = document.getElementById('card-expiry').value.trim();
  const cvv = document.getElementById('card-cvv').value.trim();
  const err = document.getElementById('payment-error');
  const unavail = document.getElementById('payment-unavailable');
  err.hidden = true;
  unavail.hidden = true;

  if (DEMO.paymentUnavailable) {
    unavail.textContent = 'Payment service temporarily unavailable — please try again shortly';
    unavail.hidden = false;
    return false;
  }

  const [mm, yy] = exp.split('/').map((x) => x.trim());
  if (!cvv) {
    err.textContent = 'CVV is required';
    err.hidden = false;
    return false;
  }
  if (yy && parseInt(yy, 10) < 25) {
    err.textContent = 'Card expiry date is in the past';
    err.hidden = false;
    return false;
  }
  if (num.startsWith('4000000000000002')) {
    err.innerHTML = 'Your card was declined — please check your details or try another card<br><button type="button" class="btn" id="btn-try-another">Try another card</button>';
    err.hidden = false;
    document.getElementById('btn-try-another')?.addEventListener('click', () => {
      err.hidden = true;
    });
    return false;
  }
  return true;
}

function processPayment() {
  if (!validateCard()) return;
  const overlay = document.getElementById('processing-overlay');
  overlay.hidden = false;
  setTimeout(() => {
    overlay.hidden = true;
    const checkout = loadCheckout();
    checkout.orderNumber = 'ORD-2001';
    saveCheckout(checkout);
    // PROTOTYPE: stub email
    console.log('PROTOTYPE: Confirmation Email', {
      subject: `Your PawPlace Order ${checkout.orderNumber} is confirmed`,
      to: checkout.guestEmail,
    });
    showToast(`Confirmation Email sent to ${checkout.guestEmail}`);
    showScreen('screen-order-confirmation');
  }, 1200);
}

function wireEvents() {
  document.querySelectorAll('[data-nav]').forEach((el) => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      showScreen(el.getAttribute('data-nav'));
    });
  });

  document.getElementById('btn-add-to-cart')?.addEventListener('click', () => {
    const p = getProduct();
    const res = addToCart(p.sku, 1);
    if (res?.error) showToast(res.error);
    else showToast(`${p.name} added — visible item count indicator updated`);
    renderAll();
  });

  document.getElementById('cart-items-body')?.addEventListener('change', (e) => {
    const input = e.target.closest('[data-qty-input]');
    if (!input) return;
    const sku = input.getAttribute('data-qty-input');
    const qty = parseInt(input.value, 10);
    const res = updateCartQty(sku, qty);
    const val = document.getElementById('cart-validation');
    if (res?.error) {
      val.textContent = res.error;
      renderCartPage();
      return;
    }
    val.textContent = '';
    renderAll();
  });

  document.getElementById('cart-items-body')?.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-remove]');
    if (!btn) return;
    removeCartItem(btn.getAttribute('data-remove'));
    renderAll();
  });

  document.getElementById('btn-proceed-checkout')?.addEventListener('click', () => {
    if (loadCart().length) showScreen('screen-pickup-store');
  });

  document.getElementById('pickup-stores-body')?.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-select-store]');
    if (!btn) return;
    const code = btn.getAttribute('data-select-store');
    const store = FIXTURES.stores.find((s) => s.code === code);
    const checkout = loadCheckout();
    checkout.pickupStore = store;
    saveCheckout(checkout);
    showToast(`Collecting from ${store.name}`);
    renderPickupStore();
  });

  document.getElementById('pickup-postcode')?.addEventListener('input', () => {
    const checkout = loadCheckout();
    checkout.postcode = document.getElementById('pickup-postcode').value;
    saveCheckout(checkout);
    renderPickupStore();
  });

  document.getElementById('btn-continue-billing')?.addEventListener('click', () => {
    const checkout = loadCheckout();
    if (!checkout.pickupStore) {
      showToast('Select a pickup store first');
      return;
    }
    showScreen('screen-billing');
  });

  document.getElementById('btn-continue-payment')?.addEventListener('click', () => {
    if (validateGuestAndBilling()) showScreen('screen-payment');
  });

  document.getElementById('btn-place-order')?.addEventListener('click', processPayment);

  document.getElementById('dismiss-account-prompt')?.addEventListener('click', () => {
    document.getElementById('account-prompt').hidden = true;
  });

  document.getElementById('queue-body')?.addEventListener('click', (e) => {
    const a = e.target.closest('[data-goto-order]');
    if (!a) return;
    e.preventDefault();
    const checkout = loadCheckout();
    checkout.viewOrder = a.getAttribute('data-goto-order');
    saveCheckout(checkout);
    showScreen('screen-staff-order');
    renderStaffOrder(checkout.viewOrder);
  });

  document.getElementById('gallery-thumbs')?.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-gallery-idx]');
    if (!btn) return;
    DEMO.galleryIndex = parseInt(btn.getAttribute('data-gallery-idx'), 10);
    renderGallery(getProduct());
  });

  document.getElementById('demo-panel-toggle')?.addEventListener('click', () => {
    const panel = document.getElementById('demo-panel');
    const collapsed = panel.getAttribute('data-collapsed') === 'true';
    panel.setAttribute('data-collapsed', collapsed ? 'false' : 'true');
    document.getElementById('demo-panel-toggle').textContent = collapsed
      ? '▾ Prototype demo controls'
      : '▸ Prototype demo controls';
  });

  document.getElementById('demo-product')?.addEventListener('change', (e) => {
    DEMO.productSku = e.target.value;
    DEMO.galleryIndex = 0;
    renderProductPage();
  });

  document.getElementById('demo-payment-unavail')?.addEventListener('change', (e) => {
    DEMO.paymentUnavailable = e.target.checked;
  });

  document.getElementById('demo-collection-elapsed')?.addEventListener('change', (e) => {
    DEMO.collectionElapsed = e.target.checked;
    const checkout = loadCheckout();
    if (checkout.viewOrder) renderStaffOrder(checkout.viewOrder);
  });

  document.getElementById('demo-reset-session')?.addEventListener('click', resetSession);

  document.getElementById('demo-seed-cart')?.addEventListener('click', () => {
    saveCart([]);
    addToCart('PET-HAR-001', 1);
    addToCart('PET-TRT-042', 1);
    showToast('Cart seeded with harness + treats (£39.98)');
    renderAll();
  });
}

function boot() {
  if (!sessionStorage.getItem(STORAGE.staff)) initStaffQueue();
  wireEvents();
  const hash = window.location.hash.replace('#', '');
  const screen = hash ? `screen-${hash}` : 'screen-product-page';
  if (document.getElementById(screen)) showScreen(screen);
  else showScreen('screen-product-page');
}

document.addEventListener('DOMContentLoaded', boot);
