/**
 * YpeTec - JavaScript Principal
 * Funcoes utilitarias para templates Django
 */

// =========================
// Utilitarios
// =========================

/**
 * Mascara para CPF: 000.000.000-00
 */
function maskCPF(el) {
    let v = el.value.replace(/\D/g, '').slice(0, 11);
    if (v.length > 9) {
        el.value = v.replace(/(\d{3})(\d{3})(\d{3})(\d{0,2})/, '$1.$2.$3-$4');
    } else if (v.length > 6) {
        el.value = v.replace(/(\d{3})(\d{3})(\d{0,3})/, '$1.$2.$3');
    } else if (v.length > 3) {
        el.value = v.replace(/(\d{3})(\d{0,3})/, '$1.$2');
    } else {
        el.value = v;
    }
}

/**
 * Mascara para data: DD/MM/AAAA
 */
function maskDateBR(el) {
    let v = el.value.replace(/\D/g, '').slice(0, 8);
    if (v.length >= 5) {
        el.value = v.replace(/(\d{2})(\d{2})(\d{0,4})/, '$1/$2/$3');
    } else if (v.length >= 3) {
        el.value = v.replace(/(\d{2})(\d{0,2})/, '$1/$2');
    } else {
        el.value = v;
    }
}

/**
 * Valida se e uma data BR valida
 */
function isValidDateBR(str) {
    const m = str.match(/^(0[1-9]|[12]\d|3[01])\/(0[1-9]|1[0-2])\/(\d{4})$/);
    if (!m) return false;

    const dd = Number(m[1]);
    const mm = Number(m[2]);
    const yyyy = Number(m[3]);

    if (yyyy < 1900 || yyyy > 9999) return false;

    const d = new Date(yyyy, mm - 1, dd);
    return (
        d.getFullYear() === yyyy &&
        d.getMonth() + 1 === mm &&
        d.getDate() === dd
    );
}

/**
 * Converte DD/MM/AAAA para YYYY-MM-DD
 */
function brToISO(str) {
    const [dd, mm, yyyy] = str.split('/');
    return `${yyyy}-${mm}-${dd}`;
}

/**
 * Converte YYYY-MM-DD para DD/MM/AAAA
 */
function isoToBR(str) {
    if (!str) return '';
    const [yyyy, mm, dd] = str.split('T')[0].split('-');
    return `${dd}/${mm}/${yyyy}`;
}

// =========================
// Confirmacoes
// =========================

/**
 * Confirmacao antes de acoes destrutivas
 */
function confirmAction(message) {
    return confirm(message || 'Tem certeza que deseja continuar?');
}

/**
 * Bind para botoes com data-confirm
 */
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[data-confirm]').forEach(function(el) {
        el.addEventListener('click', function(e) {
            if (!confirmAction(el.dataset.confirm)) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Auto-hide alerts after 5 seconds
    document.querySelectorAll('.alert-dismissible').forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // Bind mascaras
    document.querySelectorAll('[data-mask="cpf"]').forEach(function(el) {
        el.addEventListener('input', function() { maskCPF(el); });
    });

    document.querySelectorAll('[data-mask="date-br"]').forEach(function(el) {
        el.addEventListener('input', function() { maskDateBR(el); });
    });
});

// =========================
// CSRF Token para fetch
// =========================

/**
 * Retorna o CSRF token do cookie
 */
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Fetch com CSRF token
 */
async function fetchWithCSRF(url, options = {}) {
    const defaults = {
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
    };

    const merged = {
        ...defaults,
        ...options,
        headers: {
            ...defaults.headers,
            ...(options.headers || {}),
        },
    };

    return fetch(url, merged);
}

// Expoe funcoes globalmente
window.maskCPF = maskCPF;
window.maskDateBR = maskDateBR;
window.isValidDateBR = isValidDateBR;
window.brToISO = brToISO;
window.isoToBR = isoToBR;
window.confirmAction = confirmAction;
window.getCsrfToken = getCsrfToken;
window.fetchWithCSRF = fetchWithCSRF;
