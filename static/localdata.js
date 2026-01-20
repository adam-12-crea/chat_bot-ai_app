// Simple localStorage helpers (no backend)
function getData(key, fallback) {
    try {
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : fallback;
    } catch (e) {
        console.warn('getData error', e);
        return fallback;
    }
}

function setData(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.warn('setData error', e);
    }
}

function removeData(key) {
    try {
        localStorage.removeItem(key);
    } catch (e) {
        console.warn('removeData error', e);
    }
}

