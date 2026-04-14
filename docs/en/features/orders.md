# Orders & Shopping Cart 🛒

The order module manages the customer's journey from adding items to the cart to final checkout.

## 🛒 Session-Based Cart
We use a session-based cart implementation located in `features/orders/cart.py`. This allows users to store items without being logged in.
- **Storage**: JSON-serialized data in the user's session.
- **Stock Guard**: The `Cart.add()` method automatically restricts quantities based on the product's available stock.

## 🧾 Order Processing
1. **Cart Creation**: Items added to the session cart.
2. **Checkout**: User provides delivery details and confirms the order.
3. **Service Logic**: `features/orders/services/order.py` handles the creation of the `Order` and `OrderItem` records.
4. **Stock Reservation**: Stock is decremented upon successful order creation.

## 📊 Client View
Clients can track their order history through their personal cabinet (`space="client"`), which is powered by the `codex-django` cabinet system.
