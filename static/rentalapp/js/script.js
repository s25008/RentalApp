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
        if (form.closest('[data-no-loader="true"]')) return;

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

    let autoHideTimer = null;

    document.addEventListener('click', function (e) {
        if (e.defaultPrevented) return;
        if (e.button !== 0) return;
        const el = e.target.closest('*');
        if (!el) return;
        if (el.closest('[data-no-loader="true"]')) return;

        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;

        const a = e.target.closest('a[href]');
        if (a) {
            const href = a.getAttribute('href') || '';
            const target = a.getAttribute('target') || '';
            const isHash = href.startsWith('#');
            const isJs = href.toLowerCase().startsWith('javascript:');
            const isBootstrapToggle = a.getAttribute('data-bs-toggle');

            if (target === '_blank' || isHash || isJs || isBootstrapToggle) return;
            show();
        } else {
            show();
        }


        clearTimeout(autoHideTimer);
        autoHideTimer = setTimeout(() => hide(), 1200);
    }, true);

    window.addEventListener('beforeunload', function () {
        show();
    });

    window.addEventListener('pageshow', function (event) {
        if (event.persisted) hide();
    });
})();
