# Hop-and-Barley Project Guidelines

## Cabinet statics invariants (codex-django ≥ 0.4.3):
- Chart.js подключается только через `{% block cabinet_vendor_js %}`, не inline в шаблонах страниц.
- `cabinet_local.js` не перезаписывает библиотечные Alpine-компоненты.
- Данные в `chartWidget`/`donutWidget` передаются через `{% json_script %}` внутри scope виджета.
- Не ставить `document.getElementById(...)` внутри `x-data`-выражений.
