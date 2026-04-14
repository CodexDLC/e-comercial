# Product Catalog & Inventory 📦

This module handles everything related to products, categories, and stock management.

## 🗄️ Data Model
- **Product**: Core model storing beer details (Name, ABV, IBU, Price, Stock).
- **Category**: Hierarchical organization of products.
- **Stock**: Real-time inventory tracking.

## ⚙️ Key Patterns
- **Import Catalog**: `features/products/services/import_catalog.py` handles bulk updates from external data sources.
- **Selectors**: Filter products by category, rating, or availability.

## 📦 Stock Validation
The inventory is strictly checked during the checkout process and when adding items to the cart. We ensure that a user cannot purchase more items than are currently available in the warehouse.

## 🎨 UI Interaction
- **Filtering**: HTMX-powered category filtering for a fast browsing experience.
- **Search**: Full-text search across the product database.
