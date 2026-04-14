# Project Architecture 🏗

Hop and Barley follows a modular architecture designed for scalability and maintainability, leveraging the `codex-django` ecosystem.

## Component Layout

- **`core/`**: Central configuration, including settings, main URLs, logging, and infrastructure integrations (Redis).
- **`features/`**: Domain-specific business logic. Each feature is self-contained with its own models, services, selectors, and API views.
- **`system/`**: Shared services, common logic, and the role-based **Cabinet System**.
- **`cabinet/`**: UI layouts and components for Staff and Client dashboards.

## Core Design Patterns

### 1. Service/Selector Pattern
To keep logic out of models and views, we use a strict separation:
- **Selectors**: Responsible for data retrieval and complex filtering. They return QuerySets or dictionaries and never mutate data.
- **Services**: Responsible for business logic and data mutation. Every state change (creating an order, updating stock) must go through a Service.

### 2. Cabinet System
The project uses the `codex-django` cabinet module for modular UI management:
- **`declare()`**: Used in `cabinet.py` to register modules, topbar entries, and sidebar items for specific spaces (`staff` vs `client`).
- **Dashboard Widgets**: Role-based widgets (KPIs, charts, lists) are registered via the cabinet system.

## Data Flow
1. **Request**: Hits a Django View or DRF ViewSet.
2. **Logic**: The view calls a **Service** for mutations or a **Selector** for data.
3. **Response**: Data is passed to a template (using HTMX/Alpine.js for interactivity) or serialized into JSON.
