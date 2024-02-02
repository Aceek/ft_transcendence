
export function remove_url_parameter() {
    const newUrl = window.location.pathname;
    window.history.replaceState({}, document.title, newUrl);
}