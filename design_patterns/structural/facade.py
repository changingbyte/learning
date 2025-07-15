"""
Facade Pattern - Backend Implementation

This module demonstrates the Facade pattern in the context of backend development,
specifically for simplifying complex interactions between multiple services and
providing a unified interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging


# 1. USE CASES
"""
Backend Use Cases for Facade Pattern:

1. Service Integration
   - Simplify complex service interactions
   - Coordinate multiple service calls
   - Handle service dependencies

2. Data Aggregation
   - Combine data from multiple sources
   - Transform data formats
   - Handle data relationships

3. Transaction Management
   - Coordinate multiple operations
   - Handle transaction boundaries
   - Manage rollbacks

4. System Operations
   - Simplify complex workflows
   - Handle system configurations
   - Manage resource allocation

When to Use:
- When you need to simplify complex subsystem interactions
- When you want to provide a unified interface
- When you need to decouple client code from subsystems

When Not to Use:
- When subsystems are simple
- When you need fine-grained control
- When you don't want to add another abstraction layer
"""


# 2. EXAMPLES
"""
Example Scenarios:

1. Order Processing:
   ```python
   order_facade = OrderProcessingFacade()
   result = order_facade.process_order(order_data)
   # Internally handles:
   # - Inventory check
   # - Payment processing
   # - Order creation
   # - Notification sending
   ```

2. User Management:
   ```python
   user_facade = UserManagementFacade()
   user = user_facade.create_user(user_data)
   # Internally handles:
   # - User creation
   # - Role assignment
   # - Email verification
   # - Profile setup
   ```

3. Report Generation:
   ```python
   report_facade = ReportingFacade()
   report = report_facade.generate_report(criteria)
   # Internally handles:
   # - Data collection
   # - Data processing
   # - Report formatting
   # - Report delivery
   ```
"""


# 3. IMPLEMENTATION

# Data Models
@dataclass
class Product:
    """Product information."""
    id: str
    name: str
    price: float
    quantity: int


@dataclass
class Order:
    """Order information."""
    id: str
    user_id: str
    products: List[Product]
    total_amount: float
    status: str
    created_at: datetime


@dataclass
class Payment:
    """Payment information."""
    id: str
    order_id: str
    amount: float
    status: str
    payment_method: str


@dataclass
class Notification:
    """Notification information."""
    id: str
    recipient_id: str
    type: str
    message: str
    status: str


# Subsystem Components
class InventoryService:
    """Handles inventory management."""
    
    def check_availability(self, products: List[Product]) -> bool:
        """Check if products are available in required quantities."""
        print("Checking inventory availability...")
        # Simulate inventory check
        return all(product.quantity > 0 for product in products)
    
    def reserve_products(self, products: List[Product]) -> bool:
        """Reserve products for order."""
        print("Reserving products...")
        # Simulate product reservation
        return True
    
    def release_products(self, products: List[Product]) -> bool:
        """Release reserved products."""
        print("Releasing product reservation...")
        # Simulate releasing reservation
        return True


class PaymentService:
    """Handles payment processing."""
    
    def process_payment(self, order: Order, payment_method: str) -> Payment:
        """Process payment for order."""
        print(f"Processing payment for order {order.id}...")
        # Simulate payment processing
        return Payment(
            id=f"PAY_{order.id}",
            order_id=order.id,
            amount=order.total_amount,
            status="completed",
            payment_method=payment_method
        )
    
    def refund_payment(self, payment: Payment) -> bool:
        """Refund payment."""
        print(f"Refunding payment {payment.id}...")
        # Simulate payment refund
        return True


class OrderService:
    """Handles order management."""
    
    def create_order(self, user_id: str, products: List[Product]) -> Order:
        """Create a new order."""
        print("Creating order...")
        # Calculate total amount
        total_amount = sum(product.price * product.quantity for product in products)
        
        # Create order
        return Order(
            id=f"ORD_{datetime.now().timestamp()}",
            user_id=user_id,
            products=products,
            total_amount=total_amount,
            status="created",
            created_at=datetime.now()
        )
    
    def update_order_status(self, order: Order, status: str) -> bool:
        """Update order status."""
        print(f"Updating order {order.id} status to {status}...")
        order.status = status
        return True


class NotificationService:
    """Handles notification sending."""
    
    def send_notification(self, user_id: str, notification_type: str,
                        message: str) -> Notification:
        """Send notification to user."""
        print(f"Sending {notification_type} notification to user {user_id}...")
        return Notification(
            id=f"NOTIF_{datetime.now().timestamp()}",
            recipient_id=user_id,
            type=notification_type,
            message=message,
            status="sent"
        )


# Facade
class OrderProcessingFacade:
    """Facade for order processing workflow."""
    
    def __init__(self):
        self.inventory_service = InventoryService()
        self.payment_service = PaymentService()
        self.order_service = OrderService()
        self.notification_service = NotificationService()
        self.logger = logging.getLogger(__name__)
    
    def process_order(self, user_id: str, products: List[Product],
                     payment_method: str) -> Dict[str, Any]:
        """Process an order from start to finish."""
        try:
            # Step 1: Check inventory
            if not self.inventory_service.check_availability(products):
                return {
                    "success": False,
                    "error": "Products not available",
                    "step": "inventory_check"
                }
            
            # Step 2: Reserve products
            if not self.inventory_service.reserve_products(products):
                return {
                    "success": False,
                    "error": "Failed to reserve products",
                    "step": "product_reservation"
                }
            
            try:
                # Step 3: Create order
                order = self.order_service.create_order(user_id, products)
                
                # Step 4: Process payment
                payment = self.payment_service.process_payment(order, payment_method)
                
                if payment.status != "completed":
                    # Payment failed, release products
                    self.inventory_service.release_products(products)
                    self.order_service.update_order_status(order, "payment_failed")
                    return {
                        "success": False,
                        "error": "Payment failed",
                        "step": "payment_processing"
                    }
                
                # Step 5: Update order status
                self.order_service.update_order_status(order, "confirmed")
                
                # Step 6: Send notifications
                order_notification = self.notification_service.send_notification(
                    user_id,
                    "order_confirmation",
                    f"Your order {order.id} has been confirmed."
                )
                
                return {
                    "success": True,
                    "order": {
                        "id": order.id,
                        "status": order.status,
                        "total_amount": order.total_amount,
                        "created_at": order.created_at.isoformat()
                    },
                    "payment": {
                        "id": payment.id,
                        "status": payment.status
                    },
                    "notification": {
                        "id": order_notification.id,
                        "status": order_notification.status
                    }
                }
            
            except Exception as e:
                # If anything fails after reservation, release the products
                self.inventory_service.release_products(products)
                raise e
        
        except Exception as e:
            self.logger.error(f"Error processing order: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "step": "order_processing"
            }


# Usage Example
def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create facade
    order_facade = OrderProcessingFacade()
    
    # Create test products
    products = [
        Product(id="PROD1", name="Product 1", price=29.99, quantity=2),
        Product(id="PROD2", name="Product 2", price=49.99, quantity=1)
    ]
    
    try:
        # Process order
        print("\nProcessing order...")
        result = order_facade.process_order(
            user_id="USER123",
            products=products,
            payment_method="credit_card"
        )
        
        # Print result
        print("\nOrder Processing Result:")
        print(json.dumps(result, indent=2, default=str))
        
        # Process another order with insufficient inventory
        print("\nProcessing order with insufficient inventory...")
        products_unavailable = [
            Product(id="PROD3", name="Product 3", price=99.99, quantity=0)
        ]
        result = order_facade.process_order(
            user_id="USER123",
            products=products_unavailable,
            payment_method="credit_card"
        )
        
        # Print result
        print("\nOrder Processing Result (Insufficient Inventory):")
        print(json.dumps(result, indent=2, default=str))
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 