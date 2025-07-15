"""
Adapter Pattern - Backend Implementation

This module demonstrates the Adapter pattern in the context of backend development,
specifically for integrating different payment gateway systems with a unified interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal
import json


# 1. USE CASES
"""
Backend Use Cases for Adapter Pattern:

1. Payment Gateway Integration
   - Adapt different payment providers (Stripe, PayPal, Square)
   - Standardize payment processing interface
   - Handle different API formats and responses

2. Database Abstraction
   - Adapt different database drivers
   - Provide unified query interface
   - Handle different connection methods

3. External API Integration
   - Adapt third-party APIs
   - Standardize API calls and responses
   - Handle different authentication methods

4. Legacy System Integration
   - Adapt old system interfaces
   - Provide modern API interface
   - Handle data format conversion

When to Use:
- When you need to use existing classes with incompatible interfaces
- When you want to create reusable classes that cooperate with unrelated classes
- When you need to standardize third-party integrations

When Not to Use:
- When you can modify the source interface directly
- When the adaptation would be too complex
- When you don't need to reuse the adapter
"""


# 2. EXAMPLES
"""
Example Scenarios:

1. Payment Processing:
   ```python
   stripe_payment = StripeAdapter()
   result = stripe_payment.process_payment(amount=100.00, currency="USD")
   
   paypal_payment = PayPalAdapter()
   result = paypal_payment.process_payment(amount=100.00, currency="USD")
   ```

2. Database Operations:
   ```python
   mongo_db = MongoDBAdapter()
   result = mongo_db.query("users", {"active": True})
   
   postgres_db = PostgreSQLAdapter()
   result = postgres_db.query("users", {"active": True})
   ```

3. API Integration:
   ```python
   weather_api = WeatherAPIAdapter()
   weather = weather_api.get_data({"city": "New York"})
   
   maps_api = GoogleMapsAdapter()
   location = maps_api.get_data({"address": "123 Main St"})
   ```
"""


# 3. IMPLEMENTATION

@dataclass
class PaymentDetails:
    """Payment transaction details."""
    amount: Decimal
    currency: str
    card_number: str
    expiry_month: int
    expiry_year: int
    cvv: str
    description: Optional[str] = None


class PaymentGateway(ABC):
    """Target interface for payment processing."""
    
    @abstractmethod
    def process_payment(self, payment: PaymentDetails) -> Dict[str, Any]:
        """Process a payment transaction."""
        pass
    
    @abstractmethod
    def refund_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Refund a payment transaction."""
        pass
    
    @abstractmethod
    def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction details."""
        pass


# Third-party payment service interfaces
class StripeService:
    """Simulated Stripe payment service."""
    
    def charge(self, amount: int, currency: str, source: Dict[str, Any],
              description: Optional[str] = None) -> Dict[str, Any]:
        """Create a charge on Stripe."""
        # Simulate Stripe API call
        return {
            "id": "ch_stripe_123",
            "amount": amount,
            "currency": currency,
            "status": "succeeded",
            "created": int(datetime.now().timestamp())
        }
    
    def refund(self, charge_id: str) -> Dict[str, Any]:
        """Refund a charge on Stripe."""
        return {
            "id": f"re_stripe_{charge_id}",
            "charge": charge_id,
            "amount": 0,  # Refunded amount
            "status": "succeeded"
        }
    
    def retrieve_charge(self, charge_id: str) -> Dict[str, Any]:
        """Retrieve a charge from Stripe."""
        return {
            "id": charge_id,
            "amount": 0,  # Original amount
            "currency": "usd",
            "status": "succeeded"
        }


class PayPalService:
    """Simulated PayPal payment service."""
    
    def create_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a payment on PayPal."""
        return {
            "id": "PAY-paypal_123",
            "state": "approved",
            "transactions": [{
                "amount": {
                    "total": str(data["amount"]),
                    "currency": data["currency"]
                }
            }]
        }
    
    def refund_transaction(self, transaction_id: str,
                         data: Dict[str, Any]) -> Dict[str, Any]:
        """Refund a PayPal transaction."""
        return {
            "id": f"REF-paypal_{transaction_id}",
            "state": "completed",
            "amount": {
                "total": "0.00",
                "currency": "USD"
            }
        }
    
    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Get payment details from PayPal."""
        return {
            "id": payment_id,
            "state": "approved",
            "transactions": [{
                "amount": {
                    "total": "0.00",
                    "currency": "USD"
                }
            }]
        }


# Adapters for payment services
class StripeAdapter(PaymentGateway):
    """Adapter for Stripe payment service."""
    
    def __init__(self):
        self.stripe = StripeService()
    
    def process_payment(self, payment: PaymentDetails) -> Dict[str, Any]:
        """Process payment through Stripe."""
        try:
            # Convert PaymentDetails to Stripe format
            stripe_payment = {
                "amount": int(payment.amount * 100),  # Stripe uses cents
                "currency": payment.currency.lower(),
                "source": {
                    "number": payment.card_number,
                    "exp_month": payment.expiry_month,
                    "exp_year": payment.expiry_year,
                    "cvc": payment.cvv
                }
            }
            
            if payment.description:
                stripe_payment["description"] = payment.description
            
            result = self.stripe.charge(**stripe_payment)
            
            # Convert Stripe response to standard format
            return {
                "transaction_id": result["id"],
                "amount": Decimal(result["amount"]) / 100,
                "currency": result["currency"],
                "status": "success" if result["status"] == "succeeded" else "failed",
                "timestamp": datetime.fromtimestamp(result["created"]),
                "provider": "stripe"
            }
        
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "provider": "stripe"
            }
    
    def refund_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Refund payment through Stripe."""
        try:
            result = self.stripe.refund(transaction_id)
            
            return {
                "refund_id": result["id"],
                "transaction_id": result["charge"],
                "status": "success" if result["status"] == "succeeded" else "failed",
                "provider": "stripe"
            }
        
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "provider": "stripe"
            }
    
    def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction details from Stripe."""
        try:
            result = self.stripe.retrieve_charge(transaction_id)
            
            return {
                "transaction_id": result["id"],
                "amount": Decimal(result["amount"]) / 100,
                "currency": result["currency"],
                "status": "success" if result["status"] == "succeeded" else "failed",
                "provider": "stripe"
            }
        
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "provider": "stripe"
            }


class PayPalAdapter(PaymentGateway):
    """Adapter for PayPal payment service."""
    
    def __init__(self):
        self.paypal = PayPalService()
    
    def process_payment(self, payment: PaymentDetails) -> Dict[str, Any]:
        """Process payment through PayPal."""
        try:
            # Convert PaymentDetails to PayPal format
            paypal_payment = {
                "amount": float(payment.amount),
                "currency": payment.currency,
                "payment_method": {
                    "card": {
                        "number": payment.card_number,
                        "expire_month": payment.expiry_month,
                        "expire_year": payment.expiry_year,
                        "cvv2": payment.cvv
                    }
                }
            }
            
            if payment.description:
                paypal_payment["description"] = payment.description
            
            result = self.paypal.create_payment(paypal_payment)
            
            # Convert PayPal response to standard format
            return {
                "transaction_id": result["id"],
                "amount": Decimal(result["transactions"][0]["amount"]["total"]),
                "currency": result["transactions"][0]["amount"]["currency"],
                "status": "success" if result["state"] == "approved" else "failed",
                "timestamp": datetime.now(),
                "provider": "paypal"
            }
        
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "provider": "paypal"
            }
    
    def refund_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Refund payment through PayPal."""
        try:
            result = self.paypal.refund_transaction(
                transaction_id,
                {"amount": {"total": "0.00", "currency": "USD"}}
            )
            
            return {
                "refund_id": result["id"],
                "transaction_id": transaction_id,
                "status": "success" if result["state"] == "completed" else "failed",
                "provider": "paypal"
            }
        
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "provider": "paypal"
            }
    
    def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction details from PayPal."""
        try:
            result = self.paypal.get_payment_details(transaction_id)
            
            return {
                "transaction_id": result["id"],
                "amount": Decimal(result["transactions"][0]["amount"]["total"]),
                "currency": result["transactions"][0]["amount"]["currency"],
                "status": "success" if result["state"] == "approved" else "failed",
                "provider": "paypal"
            }
        
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "provider": "paypal"
            }


# Usage Example
def main():
    # Create payment details
    payment = PaymentDetails(
        amount=Decimal("99.99"),
        currency="USD",
        card_number="4242424242424242",
        expiry_month=12,
        expiry_year=2024,
        cvv="123",
        description="Test payment"
    )
    
    # Process payment with Stripe
    stripe_adapter = StripeAdapter()
    try:
        print("Processing payment with Stripe...")
        stripe_result = stripe_adapter.process_payment(payment)
        print("Stripe Result:", json.dumps(
            {k: str(v) for k, v in stripe_result.items()},
            indent=2
        ))
        
        if stripe_result["status"] == "success":
            # Get transaction details
            transaction = stripe_adapter.get_transaction(stripe_result["transaction_id"])
            print("\nStripe Transaction:", json.dumps(
                {k: str(v) for k, v in transaction.items()},
                indent=2
            ))
            
            # Refund payment
            refund = stripe_adapter.refund_payment(stripe_result["transaction_id"])
            print("\nStripe Refund:", json.dumps(
                {k: str(v) for k, v in refund.items()},
                indent=2
            ))
    
    except Exception as e:
        print(f"Error processing Stripe payment: {e}")
    
    # Process payment with PayPal
    paypal_adapter = PayPalAdapter()
    try:
        print("\nProcessing payment with PayPal...")
        paypal_result = paypal_adapter.process_payment(payment)
        print("PayPal Result:", json.dumps(
            {k: str(v) for k, v in paypal_result.items()},
            indent=2
        ))
        
        if paypal_result["status"] == "success":
            # Get transaction details
            transaction = paypal_adapter.get_transaction(paypal_result["transaction_id"])
            print("\nPayPal Transaction:", json.dumps(
                {k: str(v) for k, v in transaction.items()},
                indent=2
            ))
            
            # Refund payment
            refund = paypal_adapter.refund_payment(paypal_result["transaction_id"])
            print("\nPayPal Refund:", json.dumps(
                {k: str(v) for k, v in refund.items()},
                indent=2
            ))
    
    except Exception as e:
        print(f"Error processing PayPal payment: {e}")


if __name__ == "__main__":
    main() 