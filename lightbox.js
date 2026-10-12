(() => {
  const style = document.createElement('style');
  style.textContent = `
    #andrey-lightbox { position:fixed; inset:0; z-index:99999; display:none; align-items:center; justify-content:center; background:rgba(0,0,0,.94); padding:60px 65px; box-sizing:border-box; }
    #andrey-lightbox.is-open { display:flex; }
    #andrey-lightbox img { display:block; max-width:100%; max-height:100%; width:auto; height:auto; object-fit:contain; box-shadow:0 12px 45px rgba(0,0,0,.35); }
    #andrey-lightbox button { position:absolute; border:0; background:rgba(255,255,255,.12); color:#fff; cursor:pointer; border-radius:50%; display:grid; place-items:center; width:44px; height:44px; font-size:28px; line-height:1; }
    #andrey-lightbox button:hover, #andrey-lightbox button:focus-visible { background:rgba(255,255,255,.28); outline:2px solid white; outline-offset:2px; }
    #andrey-lightbox-close { top:14px; right:16px; }
    #andrey-lightbox-prev { left:12px; top:50%; transform:translateY(-50%); }
    #andrey-lightbox-next { right:12px; top:50%; transform:translateY(-50%); }
    #andrey-lightbox-count { position:absolute; bottom:15px; left:0; right:0; color:#ddd; text-align:center; font:13px system-ui,sans-serif; pointer-events:none; }
    #gallery img { cursor:zoom-in; }
    @media(max-width:600px) { #andrey-lightbox { padding:65px 12px; } #andrey-lightbox-prev { left:6px; } #andrey-lightbox-next { right:6px; } #andrey-lightbox button { width:38px; height:38px; background:rgba(30,30,30,.6); } }
  `;
  document.head.appendChild(style);
  const overlay = document.createElement('div');
  overlay.id = 'andrey-lightbox';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  overlay.setAttribute('aria-label', 'Enlarged photo');
  overlay.innerHTML = '<button id="andrey-lightbox-close" aria-label="Close photo">×</button><button id="andrey-lightbox-prev" aria-label="Previous photo">‹</button><img alt=""><button id="andrey-lightbox-next" aria-label="Next photo">›</button><div id="andrey-lightbox-count"></div>';
  document.body.appendChild(overlay);
  const enlarged = overlay.querySelector('img');
  const count = overlay.querySelector('#andrey-lightbox-count');
  const prev = overlay.querySelector('#andrey-lightbox-prev');
  const next = overlay.querySelector('#andrey-lightbox-next');
  let index = 0;
  let previousFocus = null;
  const photos = () => [...document.querySelectorAll('#gallery img')].filter(img => img.getAttribute('src'));
  function show(i) {
    const list = photos();
    if (!list.length) return;
    index = (i + list.length) % list.length;
    enlarged.src = list[index].currentSrc || list[index].src;
    enlarged.alt = list[index].alt || 'Enlarged photograph';
    count.textContent = `${index + 1} / ${list.length}`;
    prev.hidden = next.hidden = list.length < 2;
  }
  function open(i) {
    previousFocus = document.activeElement;
    show(i);
    overlay.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    overlay.querySelector('#andrey-lightbox-close').focus();
  }
  function close() {
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
    enlarged.removeAttribute('src');
    if (previousFocus && previousFocus.focus) previousFocus.focus();
  }
  document.addEventListener('click', e => {
    const img = e.target.closest && e.target.closest('#gallery img');
    if (img) { e.preventDefault(); open(photos().indexOf(img)); }
  });
  overlay.addEventListener('click', e => { if (e.target === overlay) close(); });
  overlay.querySelector('#andrey-lightbox-close').addEventListener('click', close);
  prev.addEventListener('click', () => show(index - 1));
  next.addEventListener('click', () => show(index + 1));
  document.addEventListener('keydown', e => {
    if (!overlay.classList.contains('is-open')) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') show(index - 1);
    else if (e.key === 'ArrowRight') show(index + 1);
    else if (e.key === 'Tab') { e.preventDefault(); overlay.querySelector('#andrey-lightbox-close').focus(); }
  });
})();
