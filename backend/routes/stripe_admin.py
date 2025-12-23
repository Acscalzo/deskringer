"""
Admin routes for Stripe payment management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Customer
import stripe
import os

stripe.api_key = os.environ.get('STRIPE_API_KEY')

stripe_admin_bp = Blueprint('stripe_admin', __name__)


@stripe_admin_bp.route('/create-payment-link/<int:customer_id>', methods=['POST'])
@jwt_required()
def create_payment_link(customer_id):
    """
    Create a Stripe payment link for a customer
    This generates a link you can send to the customer for them to pay
    """
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    try:
        # Create or get Stripe customer
        if not customer.stripe_customer_id:
            # Create new Stripe customer
            stripe_customer = stripe.Customer.create(
                email=customer.email,
                name=customer.business_name,
                metadata={
                    'deskringer_customer_id': customer.id
                }
            )
            customer.stripe_customer_id = stripe_customer.id
            db.session.commit()

        # Get the Stripe price ID from environment
        price_id = os.environ.get('STRIPE_PRICE_ID')

        if not price_id:
            return jsonify({'error': 'Stripe price not configured'}), 500

        # Create payment link
        payment_link = stripe.PaymentLink.create(
            line_items=[{
                'price': price_id,
                'quantity': 1
            }],
            customer_creation='always' if not customer.stripe_customer_id else None,
            metadata={
                'deskringer_customer_id': customer.id
            }
        )

        return jsonify({
            'payment_link': payment_link.url,
            'stripe_customer_id': customer.stripe_customer_id
        }), 200

    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return jsonify({'error': str(e)}), 400


@stripe_admin_bp.route('/create-checkout-session/<int:customer_id>', methods=['POST'])
@jwt_required()
def create_checkout_session(customer_id):
    """
    Create a Stripe Checkout session for a customer
    Alternative to payment links - gives you more control
    """
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    try:
        # Create or get Stripe customer
        if not customer.stripe_customer_id:
            stripe_customer = stripe.Customer.create(
                email=customer.email,
                name=customer.business_name,
                metadata={
                    'deskringer_customer_id': customer.id
                }
            )
            customer.stripe_customer_id = stripe_customer.id
            db.session.commit()

        # Get the Stripe price ID from environment
        price_id = os.environ.get('STRIPE_PRICE_ID')

        if not price_id:
            return jsonify({'error': 'Stripe price not configured'}), 500

        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=customer.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1
            }],
            mode='subscription',
            success_url=os.environ.get('API_BASE_URL', '') + '/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=os.environ.get('API_BASE_URL', '') + '/cancel',
            metadata={
                'deskringer_customer_id': customer.id
            }
        )

        return jsonify({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }), 200

    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return jsonify({'error': str(e)}), 400


@stripe_admin_bp.route('/subscription-status/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_subscription_status(customer_id):
    """
    Get detailed subscription status from Stripe
    """
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    if not customer.stripe_subscription_id:
        return jsonify({
            'status': customer.subscription_status,
            'has_stripe_subscription': False
        }), 200

    try:
        # Get subscription from Stripe
        subscription = stripe.Subscription.retrieve(customer.stripe_subscription_id)

        return jsonify({
            'status': subscription.status,
            'current_period_end': subscription.current_period_end,
            'cancel_at_period_end': subscription.cancel_at_period_end,
            'has_stripe_subscription': True
        }), 200

    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return jsonify({'error': str(e)}), 400


@stripe_admin_bp.route('/cancel-subscription/<int:customer_id>', methods=['POST'])
@jwt_required()
def cancel_subscription(customer_id):
    """
    Cancel a customer's subscription
    """
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    if not customer.stripe_subscription_id:
        return jsonify({'error': 'No active subscription'}), 400

    try:
        # Cancel subscription at period end (so they get what they paid for)
        subscription = stripe.Subscription.modify(
            customer.stripe_subscription_id,
            cancel_at_period_end=True
        )

        customer.subscription_status = 'cancelling'
        db.session.commit()

        return jsonify({
            'message': 'Subscription will cancel at period end',
            'cancel_at': subscription.current_period_end
        }), 200

    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return jsonify({'error': str(e)}), 400
