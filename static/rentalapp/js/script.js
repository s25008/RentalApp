(function () {
    const loader = document.getElementById('app-loader');
    if (!loader) return;

    const show = () => loader.classList.add('show');
    const hide = () => loader.classList.remove('show');

    document.addEventListener('submit', function (e) {
        const form = e.target;
        if (!form || form.tagName !== 'FORM') return;

        if (form.dataset.noLoader === 'true') return;

        const method = (form.getAttribute('method') || 'get').toLowerCase();

        const shouldShow =
            method === 'post' || (method === 'get' && form.dataset.loader === 'true');

        if (!shouldShow) return;

        if (typeof form.checkValidity === 'function' && !form.checkValidity()) return;

        const btn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (btn && !btn.disabled) {
            btn.disabled = true;
            if (btn.tagName === 'BUTTON') {
                btn.dataset.originalHtml = btn.innerHTML;
                btn.innerHTML =
                    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Przetwarzanie…';
            }
        }
        show();
    }, true);

    document.addEventListener('click', function (e) {
        if (e.defaultPrevented) return;

        if (e.button !== 0) return;
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;

        const a = e.target.closest('a[href]');
        if (!a) return;

        if (a.dataset.noLoader === 'true') return;

        if (a.dataset.loader === 'true') {
            if ((a.getAttribute('target') || '') !== '_blank') show();
            return;
        }

        const href = a.getAttribute('href') || '';
        const target = a.getAttribute('target') || '';
        const isHash = href.startsWith('#');
        const isJs = href.toLowerCase().startsWith('javascript:');
        const isBootstrapToggle = a.getAttribute('data-bs-toggle');
        const isDownload = a.hasAttribute('download');

        if (target === '_blank' || isHash || isJs || isBootstrapToggle || isDownload) return;

        show();
    }, true);

    if (window.jQuery) {
        try {
            jQuery(document).ajaxStart(show);
            jQuery(document).ajaxStop(hide);
            jQuery(document).ajaxError(hide);
        } catch (_) {
        }
    }

    window.addEventListener('beforeunload', function () {
        show();
    });

    window.addEventListener('pageshow', function (event) {
        if (event.persisted) hide();
    });
})();
