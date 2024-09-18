import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, timedelta
from .models import Payment, Orders
from customers.models import Customer
from gym_details.models import GymDetails
from user_auth.models import CustomUserRegistration
from rest_framework import status
from .serializers import PaymentSerializer
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Username of the user'
            ),
            'first_name': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='First name of the user'
            ),
            'last_name': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Last name of the user'
            ),
            'gym_id': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                description='UUID of the gym'
            ),
            'product_type': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Type of the product'
            ),
            'stripe_price_id': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Stripe price ID for the product'
            ),
            'user_id': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                description='UUID of the user'
            ),
            'promo_code': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Promo code to be applied'
            ),
            'product_id': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Product_id'
            ),
            'address': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Address'
            ),
            'phone_number': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Phone_number'
            ),
            'country': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Country'
            ),
            'pin_code': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Pin Code'
            ),
            'payment_type': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Payment_type'
            ),
            
        }
    ),
    responses={
        200: openapi.Response(
            description='Session ID and URLs',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'sessionId': openapi.Schema(type=openapi.TYPE_STRING, description='Checkout Session ID'),
                    'successUrl': openapi.Schema(type=openapi.TYPE_STRING, description='Success URL'),
                    'cancelUrl': openapi.Schema(type=openapi.TYPE_STRING, description='Cancel URL'),
                    'SessionUrl': openapi.Schema(type=openapi.TYPE_STRING, description='Session URL'),
                }
            )
        ),
        400: openapi.Response(description='Error'),
        500: openapi.Response(description='Server Error')
    }
)
@api_view(['POST'])
def create_checkout_session(request):
    plan_name = request.data.get('plan_name')
    username = request.data.get('username')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    gym_id = request.data.get('gym_id')
    product_type = request.data.get('product_type')
    product_id = request.data.get('product_id')
    address = request.data.get('address')
    phone_number = request.data.get('phone_number')
    country = request.data.get('country')
    pin_code = request.data.get('pin_code')
    stripe_price_id = request.data.get('stripe_price_id')
    user_id = request.data.get('user_id')
    promo_code = request.data.get('promo_code')
    payment_type = request.data.get('payment_type')

    if not stripe_price_id or not product_type:
        return Response({'error': 'Missing required fields: stripe_price_id or product_type'}, status=400)

    try:
        gym_details = GymDetails.objects.get(id=gym_id)
        if gym_details.promo_code_offers and promo_code:
            promo_code_data = stripe.Coupon.retrieve(promo_code)
            if promo_code_data:
                discount = {
                    'coupon': promo_code,
                }
            else:
                return Response({'error': 'Invalid promo code'}, status=400)
        else:
            discount = {}

        if payment_type == 'cod':
            # Create order for COD payment
            order = create_order(
                plan_name=plan_name,
                username=username,
                first_name=first_name,
                last_name=last_name,
                gym_id=gym_id,
                product_id=product_id,
                address=address,
                phone_number=phone_number,
                country=country,
                pin_code=pin_code,
                user_id=user_id,
                payment_type='cod'
            )

            # Return success URL in response
            success_url = request.build_absolute_uri(reverse('payment_success')) + f'?order_id={order.id}'
            return Response({
                'successUrl': success_url,
                'message': 'Order created successfully with COD payment type'
            })

        customer = stripe.Customer.create(
            email=request.data.get('email'),
            metadata={
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'gym_id': gym_id,
                'user_id': user_id,
                "plan_name": plan_name,
                "product_id": product_id,
                "pin_code": pin_code,
                "address": address,
                "phone_number": phone_number,
                "country": country,
                "payment_type": payment_type
            }
        )

        session_params = {
            'payment_method_types': ['card'],
            'line_items': [{
                'price': stripe_price_id,
                'quantity': 1,
            }],
            'mode': 'subscription' if product_type == 'subscription' else 'payment',
            'success_url': 'http://localhost:8000' + reverse('payment_success') + '?session_id={CHECKOUT_SESSION_ID}',
            'cancel_url': 'http://localhost:8000' + reverse('payment_cancel'),
            'customer': customer.id,  # Attach the customer to the session
        }

        if discount:
            session_params['discounts'] = [discount]

        session = stripe.checkout.Session.create(**session_params)

        # Replace placeholders in URLs with actual session ID
        success_url = request.build_absolute_uri(reverse('payment_success')) + f'?session_id={session.id}'
        cancel_url = request.build_absolute_uri(reverse('payment_cancel'))

        # Return the session ID and URLs to the frontend
        return Response({
            'sessionId': session.id,
            'successUrl': success_url,
            'cancelUrl': cancel_url,
            'sessionUrl': session.url
        })

    except stripe.error.StripeError as e:
        # Handle Stripe API errors
        return Response({'error': str(e)}, status=400)
    except Exception as e:
        # Handle other exceptions
        return Response({'error': str(e)}, status=500)

def create_order(**kwargs):
    # Create order in your database
    order = Orders.objects.create(
        plan_name=kwargs['plan_name'],
        username=kwargs['username'],
        first_name=kwargs['first_name'],
        last_name=kwargs['last_name'],
        gym_id=kwargs['gym_id'],
        product_id=kwargs['product_id'],
        address=kwargs['address'],
        phone_number=kwargs['phone_number'],
        country=kwargs['country'],
        pin_code=kwargs['pin_code'],
        user_id=kwargs['user_id'],
        payment_type=kwargs['payment_type']
    )
    return order

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('session_id', openapi.IN_QUERY, description="Stripe session ID", type=openapi.TYPE_STRING)
    ],
    responses={
        200: openapi.Response(description='Payment successful'),
        400: openapi.Response(description='Error'),
        500: openapi.Response(description='Server Error')
    }
)
@api_view(['GET'])
def payment_success(request):
    session_id = request.GET.get('session_id')
    session = stripe.checkout.Session.retrieve(session_id)
    customer = stripe.Customer.retrieve(session.customer)
    user_id = customer.metadata.get('user_id') 
    gym_id = customer.metadata.get('gym_id', 'N/A') 
    plan_name = customer.metadata.get('plan_name')

    gym = get_object_or_404(GymDetails, id=gym_id)

            # Retrieve the CustomUserRegistration instance
    user = get_object_or_404(CustomUserRegistration, id=user_id)

    payment = Payment.objects.create(
        username=customer.metadata.get('username', 'N/A'),
        first_name=customer.metadata.get('first_name', 'N/A'),
        last_name=customer.metadata.get('last_name', 'N/A'),
        plan_name = customer.metadata.get('plan_name', 'N/A'),
        gym=gym,
        amount=session.amount_total / 100,
        stripe_payment_id=session.payment_intent,
        status='success',
        user=user,
    )
    if session.mode == 'subscription':
        stripe_subscription = stripe.Subscription.retrieve(session.subscription)
        subscription_status = stripe_subscription.status

        if subscription_status in ['active', 'trialing']:
            plan_status = 'active'
        elif subscription_status in ['canceled', 'incomplete_expired']:
            plan_status = 'expired'
        elif subscription_status == 'past_due':
            plan_status = 'pending'
        else:
            plan_status = 'unknown'
        Customer.objects.create(
            plan_name = customer.metadata.get('plan_name'), 
            username=customer.metadata.get('username', 'N/A'),
            first_name=customer.metadata.get('first_name', 'N/A'),
            last_name=customer.metadata.get('last_name', 'N/A'),
            gym=customer.metadata.get('gym_id', 'N/A'),
            stripe_subscription_id=stripe_subscription.id,
            plan_start_date=datetime.utcfromtimestamp(int(stripe_subscription['current_period_start'])),
            plan_end_date=datetime.utcfromtimestamp(int(stripe_subscription['current_period_end'])),
            plan_status = plan_status,
            user =customer.metadata.get('user_id', 'N/A')
        )

    return Response({'message': 'Payment successful'})

@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(description='Payment was canceled'),
        400: openapi.Response(description='Error')
    }
)
@api_view(['GET'])
def payment_cancel(request):
    # Handle the payment cancellation
    return Response({'message': 'Payment was canceled'})

@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return Response({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return Response({'error': 'Invalid signature'}, status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session_completed(session)
    
    elif event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        handle_subscription_created(subscription)
    
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)

    return Response(status=200)

def handle_checkout_session_completed(session):
    customer_id = session.get('customer')
    if customer_id:
        customer = stripe.Customer.retrieve(customer_id)
        payment = Payment.objects.filter(stripe_payment_id=session.payment_intent).first()
        if payment:
            payment.status = 'success'
            payment.save()

        if session.mode == 'subscription':
            stripe_subscription = stripe.Subscription.retrieve(session.subscription)
            subscription_status = stripe_subscription.status
            plan_status = get_plan_status(subscription_status)
            Customer.objects.create(
                username=customer.metadata.get('username', 'N/A'),
                first_name=customer.metadata.get('first_name', 'N/A'),
                last_name=customer.metadata.get('last_name', 'N/A'),
                gym_id=customer.metadata.get('gym_id', 'N/A'),
                stripe_subscription_id=stripe_subscription.id,
                plan_start_date=datetime.utcfromtimestamp(stripe_subscription.current_period_start),
                plan_end_date=datetime.utcfromtimestamp(stripe_subscription.current_period_end),
                plan_status=plan_status
            )

def handle_subscription_created(subscription):
    customer_id = subscription.get('customer')
    if customer_id:
        customer = stripe.Customer.retrieve(customer_id)
        plan_status = get_plan_status(subscription['status'])
        Customer.objects.create(
            username=customer.metadata.get('username', 'N/A'),
            first_name=customer.metadata.get('first_name', 'N/A'),
            last_name=customer.metadata.get('last_name', 'N/A'),
            gym_id=customer.metadata.get('gym_id', 'N/A'),
            stripe_subscription_id=subscription.id,
            plan_start_date=datetime.utcfromtimestamp(subscription['current_period_start']),
            plan_end_date=datetime.utcfromtimestamp(subscription['current_period_end']),
            plan_status=plan_status
        )

def handle_subscription_updated(subscription):
    customer_id = subscription.get('customer')
    if customer_id:
        customer = stripe.Customer.retrieve(customer_id)
        plan_status = get_plan_status(subscription['status'])
        Customer.objects.update_or_create(
            stripe_subscription_id=subscription.id,
            defaults={
                'plan_start_date': datetime.utcfromtimestamp(subscription['current_period_start']),
                'plan_end_date': datetime.utcfromtimestamp(subscription['current_period_end']),
                'plan_status': plan_status
            }
        )

def handle_subscription_deleted(subscription):
    Customer.objects.filter(stripe_subscription_id=subscription.id).delete()

def get_plan_status(status):
    if status in ['active', 'trialing']:
        return 'active'
    elif status in ['canceled', 'incomplete_expired']:
        return 'expired'
    elif status == 'past_due':
        return 'pending'
    else:
        return 'unknown'


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'stripe_payment_id': openapi.Schema(type=openapi.TYPE_STRING, description="Stripe Payment ID"),
            'amount': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Amount"),
            'status': openapi.Schema(type=openapi.TYPE_STRING, description="Status"),
            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Creation Date"),
            'user': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="User ID (UUID)"),
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="First Name"),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description="Last Name"),
            'gym_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="Gym ID (UUID)"),
            'admin': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="Admin ID (UUID)")
        },
        required=[ 'amount', 'gym_id', 'admin']  # Add required fields if necessary
    ),
    responses={201: PaymentSerializer},
)
@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'stripe_payment_id': openapi.Schema(type=openapi.TYPE_STRING, description="Stripe Payment ID"),
            'amount': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Amount"),
            'status': openapi.Schema(type=openapi.TYPE_STRING, description="Status"),
            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Creation Date"),
            'user': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="User ID (UUID)"),
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="First Name"),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description="Last Name"),
            'gym_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="Gym ID (UUID)"),
            'admin': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description="Admin ID (UUID)")
        },
        required=[ 'amount' 'gym_id', 'admin']  # Add required fields if necessary
    ),
    responses={200: PaymentSerializer},
)
@swagger_auto_schema(
    method='get',
    manual_parameters = [
    openapi.Parameter(
        'admin', 
        openapi.IN_QUERY, 
        description="Admin ID (UUID format)", 
        type=openapi.TYPE_STRING, 
        format=openapi.FORMAT_UUID
    ),
    openapi.Parameter(
        'gym_id', 
        openapi.IN_QUERY, 
        description="Gym ID (UUID format)", 
        type=openapi.TYPE_STRING, 
        format=openapi.FORMAT_UUID
    ),
],
    responses={
        200: openapi.Response(description='Payment details'),
        400: openapi.Response(description='Error'),
        404: openapi.Response(description='Not Found'),
        500: openapi.Response(description='Server Error')
    }
)
@api_view(['GET', 'POST', 'PUT'])
def get_payment_details(request):
    if request.method == "GET":
        admin_id = request.GET.get('admin')
        gym_id = request.GET.get('gym_id')
        if not admin_id or not gym_id:
            return Response({"error": "Admin ID and Gym ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)
            payment = get_object_or_404(Payment, gym=gym_id)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == "POST":
        print(request.data)
        admin_id = request.data.get('admin')
        gym_id = request.data.get('gym_id')

        if not admin_id or not gym_id:
            return Response({"error": "Admin ID and Gym ID are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)
        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            gym = get_object_or_404(GymDetails, id = gym_id)
            serializer.save(gym=gym)
            return Response({"message": "Customer details added successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        payment_id = request.data.get('payment_id')
        admin_id = request.data.get('admin_id')
        gym_id = request.data.get('gym_id')

        if not payment_id or not admin_id or not gym_id:
            return Response({"error": "Payment ID, Admin ID, and Gym ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify that the admin exists and is a staff member
            admin = CustomUserRegistration.objects.get(id=admin_id, is_staff=True)
            
            # Verify that the gym exists and is associated with the admin
            gym = GymDetails.objects.get(id=gym_id, admin=admin)
            
            # Retrieve the payment by payment_id and gym_id
            payment = get_object_or_404(Payment, id=payment_id, gym=gym)
            
            # Serialize the data and update the payment
            serializer = PaymentSerializer(payment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Payment details updated successfully"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except CustomUserRegistration.DoesNotExist:
            return Response({"error": "Admin ID not found or not an admin user"}, status=status.HTTP_404_NOT_FOUND)
        except GymDetails.DoesNotExist:
            return Response({"error": "Gym not found for the given Gym ID and Admin ID"}, status=status.HTTP_404_NOT_FOUND)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found for the given Payment ID and Gym ID"}, status=status.HTTP_404_NOT_FOUND)