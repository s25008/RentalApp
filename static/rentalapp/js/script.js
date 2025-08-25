(function () {
  const loader = document.getElementById('app-loader');
  if (!loader) return;

  const show = () => loader.classList.add('show');
  const hide = () => loader.classList.remove('show');

  document.addEventListener('submit', function (e) {
    const form = e.target;
    if (!form || form.tagName !== 'FORM') return;
    const method = (form.getAttribute('method') || 'get').toLowerCase();
    if (method !== 'post') return;

    if (typeof form.checkValidity === 'function' && !form.checkValidity()) return;

    const btn = form.querySelector('button[type="submit"], input[type="submit"]');
    if (btn && !btn.dataset.loadingAttached) {
      btn.dataset.loadingAttached = '1';
      if (btn.tagName === 'BUTTON') {
        btn.dataset.originalHtml = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Przetwarzanie…';
      }
      btn.disabled = true;
    }

    show();
  }, true);

  document.addEventListener('click', function (e) {
    const el = e.target.closest('[data-loader="true"]');
    if (!el) return;
    if (el.tagName === 'A' && el.target === '_blank') return;
    show();
  }, true);

  window.addEventListener('pageshow', function (event) {
    if (event.persisted) hide();
  });
})();
