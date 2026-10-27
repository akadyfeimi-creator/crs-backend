#!/usr/bin/env bash
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

echo "Seeding questions..."
python manage.py seed_questions

echo "Creating admin and test users..."
python manage.py shell -c "
from apps.accounts.models import User
from apps.institutions.models import Institution

# Admin
if not User.objects.filter(email='admin@gmail.com').exists():
    User.objects.create_superuser(email='admin@gmail.com', username='admin', password='admin123')

# Analysts
for email in ['analyst1@cyberrisk.ng', 'analyst2@cyberrisk.ng', 'analyst3@cyberrisk.ng']:
    if not User.objects.filter(email=email).exists():
        User.objects.create_user(username=email.split('@')[0], email=email, password='Secure@2026!', role='analyst')

# Assessors
assessors = [('assessor1@testbank.ng', 'First Bank of Nigeria'), ('assessor2@zenith.ng', 'Zenith Bank'), ('assessor3@gtbank.ng', 'GTBank'), ('assessor4@accessbank.ng', 'Access Bank'), ('assessor5@uba.ng', 'UBA'), ('assessor6@palm.ng', 'PalmPay'), ('assessor7@opay.ng', 'OPay'), ('assessor8@kuda.ng', 'Kuda Bank'), ('assessor9@moniepoint.ng', 'Moniepoint'), ('assessor10@flutterwave.ng', 'Flutterwave')]
for email, org in assessors:
    if not User.objects.filter(email=email).exists():
        User.objects.create_user(username=email.split('@')[0], email=email, password='Assessor@2026!', role='assessor', organization=org)

# Viewers
viewers = [('viewer1@cbn.gov.ng', 'CBN'), ('viewer2@ndic.gov.ng', 'NDIC'), ('viewer3@nitda.gov.ng', 'NITDA'), ('viewer4@stanbic.ng', 'Stanbic IBTC'), ('viewer5@fidelity.ng', 'Fidelity Bank'), ('viewer6@unionbank.ng', 'Union Bank'), ('viewer7@ecobank.ng', 'Ecobank'), ('viewer8@sterling.ng', 'Sterling Bank'), ('viewer9@fcmb.ng', 'FCMB'), ('viewer10@wema.ng', 'Wema Bank')]
for email, org in viewers:
    if not User.objects.filter(email=email).exists():
        User.objects.create_user(username=email.split('@')[0], email=email, password='Viewer@2026!', role='viewer', organization=org)

# Institutions
admin = User.objects.filter(email='admin@gmail.com').first()
insts = [('First Bank of Nigeria', 'bank', 'RC123456', 'info@firstbank.com'), ('Zenith Bank', 'bank', 'RC456789', 'info@zenithbank.com'), ('GTBank', 'bank', 'RC789012', 'info@gtbank.com'), ('Access Bank', 'bank', 'RC345678', 'info@accessbank.com'), ('UBA', 'bank', 'RC901234', 'info@ubagroup.com'), ('PalmPay', 'fintech', 'RC567890', 'info@palmpay.com'), ('OPay', 'fintech', 'RC234567', 'info@opay.com'), ('Kuda Bank', 'fintech', 'RC890123', 'info@kuda.com'), ('Moniepoint', 'fintech', 'RC678901', 'info@moniepoint.com'), ('Flutterwave', 'fintech', 'RC456123', 'info@flutterwave.com')]
for name, type_, reg, email in insts:
    if not Institution.objects.filter(name=name).exists():
        Institution.objects.create(name=name, type=type_, registration_number=reg, email=email, created_by=admin)

print('✅ All data created!')
"

echo "Deployment complete!"