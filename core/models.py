from django.db import models
from django.conf import settings
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    sub_category = models.CharField(max_length=100) # e.g., "Baby Feeding"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)

    def __str__(self):
        return self.name

class Pharmacy(models.Model):
    ROLES = [
        ('owner', 'Owner'),
        ('pharmacist', 'Pharmacist-in-Charge'),
        ('manager', 'Manager'),
        ('representative', 'Authorized Representative'),
    ]
    TYPES = [
        ('independent_retail', 'Independent Retail Pharmacy'),
        ('chain_branch', 'Chain Branch'),
        ('hospital', 'Hospital Pharmacy'),
        ('clinic', 'Clinic Pharmacy'),
    ]
    SETTLEMENT = [
        ('bank_transfer', 'Bank Transfer (PESONet / InstaPay)'),
        ('gcash', 'GCash Merchant'),
        ('maya', 'Maya Business'),
    ]

    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pharmacy')

    # Step 1
    role = models.CharField(max_length=20, choices=ROLES)
    phone = models.CharField(max_length=20)

    # Step 2
    name = models.CharField(max_length=150)
    pharmacy_type = models.CharField(max_length=20, choices=TYPES)
    tin = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255)
    location_pin = models.CharField(max_length=255)

    # Step 3
    lto_number = models.CharField(max_length=50)
    lto_expiry = models.DateField()
    lto_copy = models.FileField(upload_to='pharmacy_docs/')
    prc_id = models.FileField(upload_to='pharmacy_docs/')
    business_permit = models.FileField(upload_to='pharmacy_docs/')

    # Step 4
    settlement_method = models.CharField(max_length=20, choices=SETTLEMENT)
    provider = models.CharField(max_length=30)
    account_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=30)
    payout_proof = models.FileField(upload_to='pharmacy_docs/', blank=True)
    rx_compliance_agreed = models.BooleanField(default=False)
    terms_agreed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer')
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name or self.user.email

class Order(models.Model):
    STATUS = [
        ('to_pay_onsite', 'To Pay Onsite'),
        ('to_deliver', 'To Deliver'),
        ('to_receive', 'To Receive'),
        ('returns', 'Returns'),
        ('cancelled', 'Cancelled'),
    ]
    FULFILLMENT = [
        ('pickup', 'On-Site Pickup'),
        ('delivery', 'Delivery'),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # price at the time of ordering
    fulfillment = models.CharField(max_length=10, choices=FULFILLMENT, default='pickup')
    status = models.CharField(max_length=20, choices=STATUS, default='to_pay_onsite')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def total(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        creating = self._state.adding
        if creating and not self.order_number:
            self.order_number = uuid.uuid4().hex[:12]  # temporary, replaced below
        super().save(*args, **kwargs)
        if creating:
            # e.g. MC-2026-00123
            self.order_number = f"MC-{self.created_at.year}-{self.pk:05d}"
            super().save(update_fields=['order_number'])

    def __str__(self):
        return self.order_number