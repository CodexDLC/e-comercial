/* CODEX_DJANGO_CLI BLUEPRINT STATUS: MOVE_TO_CLI_BLUEPRINT. Reason: generated cabinet app asset source for codex-django-cli blueprints. */
/* @provides cabinet.app.entry
   @depends cabinet.core.htmx_csrf, cabinet.core.sidebar_sync, cabinet.widgets.client_lookup, cabinet.widgets.date_time_picker, cabinet.widgets.tabbed_assignment */
(function () {
    const MODAL_ID = 'cabinet-modal';
    const CONTENT_ID = 'cabinet-modal-content';

    function ensureModalRoot() {
        let modal = document.getElementById(MODAL_ID);
        if (modal) {
            return modal;
        }

        modal = document.createElement('div');
        modal.id = MODAL_ID;
        modal.className = 'modal fade';
        modal.tabIndex = -1;
        modal.setAttribute('aria-hidden', 'true');
        modal.innerHTML = [
            '<div class="modal-dialog modal-lg modal-dialog-centered">',
            `  <div class="modal-content" id="${CONTENT_ID}"></div>`,
            '</div>',
        ].join('');
        document.body.appendChild(modal);
        return modal;
    }

    function getModalContent() {
        return ensureModalRoot().querySelector(`#${CONTENT_ID}`);
    }

    function getBootstrapModal(modalElement) {
        if (!window.bootstrap || !window.bootstrap.Modal) {
            return null;
        }
        return window.bootstrap.Modal.getOrCreateInstance(modalElement);
    }

    function openModalWithHtml(html) {
        const modalElement = ensureModalRoot();
        const content = getModalContent();
        content.innerHTML = html;
        const instance = getBootstrapModal(modalElement);
        if (instance) {
            instance.show();
            return;
        }
        modalElement.classList.add('show');
        modalElement.style.display = 'block';
        document.body.classList.add('modal-open');
    }

    function closeModal() {
        const modalElement = document.getElementById(MODAL_ID);
        if (!modalElement) {
            return;
        }
        const instance = getBootstrapModal(modalElement);
        if (instance) {
            instance.hide();
        } else {
            modalElement.classList.remove('show');
            modalElement.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
        const content = modalElement.querySelector(`#${CONTENT_ID}`);
        if (content) {
            content.innerHTML = '';
        }
    }

    async function loadModal(url) {
        const response = await window.fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            credentials: 'same-origin',
        });
        if (!response.ok) {
            throw new Error(`Failed to load modal: ${response.status}`);
        }
        openModalWithHtml(await response.text());
    }

    document.body.addEventListener('open-modal', function (event) {
        const url = event.detail && event.detail.url;
        if (!url) {
            return;
        }
        event.preventDefault();
        loadModal(url).catch(function (error) {
            console.error(error);
        });
    });

    document.body.addEventListener('htmx:afterRequest', function (event) {
        const requestPath = event.detail && event.detail.pathInfo && event.detail.pathInfo.requestPath;
        if (!requestPath || !requestPath.includes('/cabinet/products/')) {
            return;
        }
        if (event.detail.successful && event.detail.xhr && event.detail.xhr.status === 204) {
            closeModal();
        }
    });

    document.body.addEventListener('hidden.bs.modal', function (event) {
        if (event.target && event.target.id === MODAL_ID) {
            const content = getModalContent();
            if (content) {
                content.innerHTML = '';
            }
        }
    });

    document.body.addEventListener('click', function (event) {
        if (event.target.matches(`#${MODAL_ID}`)) {
            closeModal();
        }
    });
})();
