import datetime
import uuid

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Pharmacy, Customer, Order

User = get_user_model()

T = 'registration/register_pharmacy/'
ALLOWED_TYPES = {'application/pdf', 'image/jpeg', 'image/png'}
ALLOWED_EXT = ('.pdf', '.jpg', '.jpeg', '.png')
MAX_SIZE = 5 * 1024 * 1024  # 5 MB


# ---------- Basic pages ----------

def home(request):
    return render(request, 'landingPage.html')


def categoriesPage(request):
    return render(request, 'categoriesPage.html')


def category_detail(request, category_slug):
    # A dictionary to map URL slugs to display titles
    category_titles = {
        'pain-relief': 'Pain Relief & Fever',
        'maternity-care': 'Baby and Maternity Care',
        'vitamins': 'Vitamins & Supplements',
        'first-aid': 'First Aid & Wound Care',
        'personal-care': 'Personal Care & Hygiene',
        'oral-care': 'Oral Care',
        'medical-equipment': 'Medical Equipment',
        'eye-ear-care': 'Eye and Ear Care',
        'sports-nutrition': 'Sports Nutrition and Fitness',
        'senior-care': 'Senior Care',
    }

    category_title = category_titles.get(category_slug, 'Category')

    context = {
        'category_slug': category_slug,
        'category_title': category_title,
    }

    return render(request, 'byCategory/category_detail.html', context)


# ---------- Login / logout ----------

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        user = authenticate(request, username=email, password=request.POST.get('password', ''))

        if user is not None:
            login(request, user)
            if not request.POST.get('remember'):
                request.session.set_expiry(0)  # expires when the browser closes
            return redirect('home')

        return render(request, 'registration/login.html',
                      {'error': 'Incorrect email or password.', 'email': email})

    return render(request, 'registration/login.html')


def logout_view(request):
    if request.method == 'POST':  # Django expects logout via POST
        logout(request)
    return redirect('home')


# ---------- Customer registration ----------

def registerCustomer(request):
    if request.method == 'POST':
        p = request.POST
        email = p['email'].strip().lower()
        error = None

        if p['password'] != p['confirm_password']:
            error = 'Passwords do not match.'
        elif User.objects.filter(username=email).exists():
            error = 'An account with this email already exists.'
        else:
            try:
                validate_password(p['password'])
            except ValidationError as e:
                error = ' '.join(e.messages)

        if error:
            # send the typed values back so the form isn't wiped
            return render(request, 'registration/registerCustomer.html', {'error': error, 'data': p})

        with transaction.atomic():
            user = User.objects.create_user(
                username=email,
                email=email,
                password=p['password'],  # create_user hashes it
                first_name=p['fullname'].strip(),
            )
            Customer.objects.create(
                user=user,
                phone=p['phone'].strip(),
                address=p['address'].strip(),
            )

        login(request, user)
        return redirect('home')

    return render(request, 'registration/registerCustomer.html')


# ---------- Pharmacy registration (4 steps) ----------

def valid_upload(f):
    return (f.content_type in ALLOWED_TYPES
            and f.name.lower().endswith(ALLOWED_EXT)
            and f.size <= MAX_SIZE)


def save_upload(f):
    return default_storage.save(f'pharmacy_docs/{uuid.uuid4().hex}_{f.name}', f)


def step1(request):
    if request.method == 'POST':
        p = request.POST
        email = p['email'].strip().lower()
        error = None

        if p['password'] != p['confirm_password']:
            error = 'Passwords do not match.'
        elif User.objects.filter(username=email).exists():
            error = 'An account with this email already exists.'
        else:
            try:
                validate_password(p['password'])
            except ValidationError as e:
                error = ' '.join(e.messages)

        if error:
            return render(request, T + 'step1.html', {'error': error})

        request.session['reg'] = {
            'fullname': p['fullname'].strip(),
            'role': p['role'],
            'email': email,
            'phone': p['phone'].strip(),
            'password': make_password(p['password']),  # hashed, never the raw password
        }
        return redirect('step2')

    return render(request, T + 'step1.html')


def step2(request):
    reg = request.session.get('reg')
    if not reg or 'fullname' not in reg:
        return redirect('step1')

    if request.method == 'POST':
        p = request.POST
        reg.update({
            'pharmacy_name': p['pharmacy_name'].strip(),
            'pharmacy_type': p['pharmacy_type'],
            'tin': p['tin'].strip(),
            'street_address': p['street_address'].strip(),
            'location_pin': p['location_pin'].strip(),
        })
        request.session['reg'] = reg
        return redirect('step3')

    return render(request, T + 'step2.html')


def step3(request):
    reg = request.session.get('reg')
    if not reg or 'pharmacy_name' not in reg:
        return redirect('step2')

    if request.method == 'POST':
        error = None

        try:
            expiry = datetime.date.fromisoformat(request.POST['lto_expiry'])
            if expiry <= datetime.date.today():
                error = 'Your FDA LTO has expired. Please enter a valid expiration date.'
        except ValueError:
            error = 'Enter a valid expiration date.'

        files = {k: request.FILES.get(k) for k in ('lto_copy', 'prc_id', 'business_permit')}
        if not error and any(not f or not valid_upload(f) for f in files.values()):
            error = 'Upload all three documents as PDF, JPG, or PNG (max 5MB each).'

        if error:
            return render(request, T + 'step3.html', {'error': error})

        # Files can't live in the session, so save them now and keep only the paths
        for key, f in files.items():
            reg[key] = save_upload(f)

        reg['lto_number'] = request.POST['lto_number'].strip()
        reg['lto_expiry'] = expiry.isoformat()
        request.session['reg'] = reg
        return redirect('step4')

    return render(request, T + 'step3.html')


def step4(request):
    reg = request.session.get('reg')
    if not reg or 'lto_copy' not in reg:
        return redirect('step3')

    if request.method == 'POST':
        p = request.POST
        valid_providers = {
            'bank_transfer': {'BDO', 'BPI', 'Metrobank', 'UnionBank', 'Landbank'},
            'gcash': {'GCash'},
            'maya': {'Maya'},
        }
        proof = request.FILES.get('payout_proof')
        error = None

        if p.get('provider') not in valid_providers.get(p.get('settlement_method'), set()):
            error = 'Please choose a valid settlement method and provider.'
        elif not (p.get('rx_compliance') and p.get('merchant_terms')):
            error = 'You must accept both agreements to continue.'
        elif proof and not valid_upload(proof):
            error = 'Proof must be a PDF, JPG, or PNG up to 5MB.'
        elif User.objects.filter(username=reg['email']).exists():
            error = 'An account with this email already exists.'

        if error:
            return render(request, T + 'step4.html', {'error': error})

        with transaction.atomic():
            user = User.objects.create(
                username=reg['email'],
                email=reg['email'],
                first_name=reg['fullname'],
                password=reg['password'],  # already hashed in step 1
            )
            Pharmacy.objects.create(
                owner=user,
                role=reg['role'],
                phone=reg['phone'],
                name=reg['pharmacy_name'],
                pharmacy_type=reg['pharmacy_type'],
                tin=reg['tin'],
                street_address=reg['street_address'],
                location_pin=reg['location_pin'],
                lto_number=reg['lto_number'],
                lto_expiry=reg['lto_expiry'],
                lto_copy=reg['lto_copy'],
                prc_id=reg['prc_id'],
                business_permit=reg['business_permit'],
                settlement_method=p['settlement_method'],
                provider=p['provider'],
                account_name=p['account_name'].strip(),
                account_number=p['account_number'].strip(),
                payout_proof=save_upload(proof) if proof else '',
                rx_compliance_agreed=True,
                terms_agreed=True,
            )

        login(request, user)
        request.session.pop('reg', None)
        return redirect('home')  # swap for a merchant dashboard when you build one

    return render(request, T + 'step4.html')

@login_required
def account_orders(request):
    customer = getattr(request.user, 'customer', None)
    if customer is None:          # e.g. a pharmacy owner
        return redirect('home')

    tabs = [(key, label) for key, label in Order.STATUS if key != 'cancelled']
    status = request.GET.get('status', 'to_pay_onsite')
    if status not in dict(tabs):
        status = 'to_pay_onsite'

    orders = (Order.objects
            .filter(customer=customer, status=status)
            .select_related('pharmacy', 'product'))

    return render(request, 'account/orders.html', {
        'active_page': 'orders',
        'tabs': tabs,
        'active_status': status,
        'orders': orders,
    })


@login_required
def cancel_order(request, order_id):
    customer = getattr(request.user, 'customer', None)
    if request.method == 'POST' and customer:
        order = get_object_or_404(Order, pk=order_id, customer=customer)  # only your own orders
        if order.status == 'to_pay_onsite':
            order.status = 'cancelled'
            order.save(update_fields=['status'])
    return redirect('account_orders')