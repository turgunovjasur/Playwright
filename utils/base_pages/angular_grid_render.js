// Each table owns its loading/render cycle, including when Angular replaces a table.
(() => {
    if (window.__smartupGridRendered) return;
    // Smartup renders an inner smt-table inside a single smt-data-table.
    const selector = 'smt-data-table, smt-table:not(smt-data-table smt-table)';
    const cycles = new WeakMap();
    let lastInteraction = 0;
    const responses = new Map();
    new PerformanceObserver(list => {
        for (const entry of list.getEntries()) {
            if (entry.initiatorType === 'fetch' || entry.initiatorType === 'xmlhttprequest') {
                responses.set(entry.name, entry);
            }
        }
    }).observe({type: 'resource', buffered: true});
    for (const event of ['click', 'keydown', 'input', 'change', 'submit', 'popstate', 'hashchange']) {
        window.addEventListener(event, () => { lastInteraction = performance.now(); }, {capture: true, passive: true});
    }
    const observe = grid => {
        // Toolbar and pagination keep display:none skeletons even when the
        // data rows are ready. The body declares its own loading state.
        const busy = Boolean(grid.querySelector('.smt-grid-body[aria-busy="true"]'));
        const cycle = cycles.get(grid);
        if (busy && !cycle?.busy) {
            cycles.set(grid, {busy: true, url: location.href});
        } else if (!busy && cycle?.busy) {
            cycle.busy = false;
            cycle.rendered = performance.now();
        }
    };
    new MutationObserver(records => {
        const grids = new Set();
        for (const record of records) {
            const parent = record.target.closest?.(selector);
            if (parent) grids.add(parent);
            // A route change may insert a whole, already loading table.
            if (!parent) {
                for (const node of record.addedNodes) {
                    if (node.matches?.(selector)) grids.add(node);
                    node.querySelectorAll?.(selector).forEach(grid => grids.add(grid));
                }
            }
        }
        grids.forEach(observe);
    }).observe(document, {subtree: true, childList: true, attributes: true, attributeFilter: ['aria-busy']});
    document.querySelectorAll(selector).forEach(observe);

    window.__smartupGridRendered = (grid, request) => {
        if (!grid.matches('smt-data-table, smt-table')) return false;
        grid = grid.closest(selector);
        const cycle = cycles.get(grid);
        // Multiple tables on one route can use different named queries.
        const main = grid.closest('main');
        const response = responses.get(request.url);
        return Boolean(response && main && main.querySelectorAll(selector).length === 1
            && cycle && !cycle.busy && cycle.url === location.href
            && response.startTime >= lastInteraction && response.responseEnd <= cycle.rendered
            && performance.timeOrigin + response.responseEnd >= request.startTime);
    };
})();
