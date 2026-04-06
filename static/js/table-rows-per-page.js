(function () {
    function isInsidePrintContext(table) {
        return !!(table.closest('.print-container') || document.body.classList.contains('print-page'));
    }

    function hasExistingRowsControl(table) {
        var container = table.closest('.table-responsive') || table.parentElement;
        if (!container) return false;
        return !!(container.querySelector('#rowsPerPage') || container.querySelector('#pageSizeSelect') || container.querySelector('[data-rows-per-page-control]'));
    }

    function getBodyRows(table) {
        var tbody = table.tBodies && table.tBodies.length ? table.tBodies[0] : null;
        if (!tbody) return [];
        return Array.from(tbody.rows);
    }

    function applyLimit(rows, limit) {
        rows.forEach(function (row, idx) {
            if (limit === 'all') {
                row.style.display = '';
                return;
            }
            row.style.display = (idx < limit) ? '' : 'none';
        });
    }

    function initTable(table) {
        if (!table || table.dataset.rowsPerPageInitialized === '1') return;
        if (table.dataset.disableRowsPerPage === '1') return;
        if (isInsidePrintContext(table)) return;
        if (table.closest('.modal')) return;

        var rows = getBodyRows(table);
        if (rows.length <= 10) return;
        if (hasExistingRowsControl(table)) return;

        var wrapper = document.createElement('div');
        wrapper.setAttribute('data-rows-per-page-control', '1');
        wrapper.className = 'd-flex justify-content-end align-items-center gap-2 mb-2';

        var label = document.createElement('label');
        label.className = 'text-muted small mb-0';
        label.textContent = 'Show:';

        var select = document.createElement('select');
        select.className = 'form-select form-select-sm';
        select.style.width = 'auto';

        var opts = [5, 10, 25, 50, 100, 'all'];
        opts.forEach(function (v) {
            var o = document.createElement('option');
            o.value = String(v);
            o.textContent = (v === 'all') ? 'All' : String(v);
            select.appendChild(o);
        });

        var defaultValue = '10';
        select.value = defaultValue;

        wrapper.appendChild(label);
        wrapper.appendChild(select);

        var insertBeforeEl = table;
        var container = table.closest('.table-responsive');
        if (container && container.parentElement) {
            container.parentElement.insertBefore(wrapper, container);
        } else if (table.parentElement) {
            table.parentElement.insertBefore(wrapper, insertBeforeEl);
        }

        function onChange() {
            var val = select.value;
            var limit = (val === 'all') ? 'all' : parseInt(val, 10);
            applyLimit(rows, limit);
        }

        select.addEventListener('change', onChange);
        onChange();

        table.dataset.rowsPerPageInitialized = '1';
    }

    function initAll() {
        var tables = Array.from(document.querySelectorAll('table.table'));
        tables.forEach(initTable);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAll);
    } else {
        initAll();
    }
})();
