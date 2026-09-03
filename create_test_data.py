"""
Create Test Data for Cybersecurity Risk Assessment System
=========================================================
This script creates:
- 23 test users with different roles
- 10+ institutions (banks, fintechs, MFBs, PSPs)
- 15+ assessments with different risk levels
- Historical trends for analytics
- Dummy audit logs
"""

import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cyberrisk.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import User, AuditLog
from apps.institutions.models import Institution
from apps.assessments.models import Assessment, AssessmentQuestion, AssessmentResponse
from apps.risk_engine.scoring import RiskScoringEngine
from apps.risk_engine.models import RiskAssessmentReport, SecurityTrend

User = get_user_model()

def create_users():
    """Create 23 test users with different roles"""
    print("Creating users...")
    
    # Admin user (already exists)
    admin, created = User.objects.get_or_create(
        email='admin@gmail.com',
        defaults={
            'username': 'admin',
            'role': User.Role.ADMIN,
            'is_staff': True,
            'is_superuser': True,
            'is_verified': True,
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"  Created admin: {admin.email}")
    else:
        print(f"  Admin already exists: {admin.email}")
    
    # Security Analysts (3)
    analysts_data = [
        ('analyst1@cyberrisk.ng', 'analyst1', 'Chinedu', 'Okafor'),
        ('analyst2@cyberrisk.ng', 'analyst2', 'Aisha', 'Bello'),
        ('analyst3@cyberrisk.ng', 'analyst3', 'Tunde', 'Adebayo'),
    ]
    
    analysts = []
    for email, username, first, last in analysts_data:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': first,
                'last_name': last,
                'role': User.Role.ANALYST,
                'organization': 'Cybersecurity Assessment Center',
                'is_verified': True,
            }
        )
        if created:
            user.set_password('Secure@2026!')
            user.save()
            print(f"  Created analyst: {user.email}")
        analysts.append(user)
    
    # Risk Assessors (10)
    assessors_data = [
        ('assessor1@testbank.ng', 'assessor1', 'Emeka', 'Nwosu', 'First Bank of Nigeria'),
        ('assessor2@zenith.ng', 'assessor2', 'Funke', 'Adeyemi', 'Zenith Bank'),
        ('assessor3@gtbank.ng', 'assessor3', 'Ibrahim', 'Musa', 'GTBank'),
        ('assessor4@accessbank.ng', 'assessor4', 'Ngozi', 'Eze', 'Access Bank'),
        ('assessor5@uba.ng', 'assessor5', 'Yusuf', 'Ali', 'UBA'),
        ('assessor6@palm.ng', 'assessor6', 'Bola', 'Ogun', 'PalmPay'),
        ('assessor7@opay.ng', 'assessor7', 'Kemi', 'Adesina', 'OPay'),
        ('assessor8@kuda.ng', 'assessor8', 'David', 'Igwe', 'Kuda Bank'),
        ('assessor9@moniepoint.ng', 'assessor9', 'Sade', 'Balogun', 'Moniepoint'),
        ('assessor10@flutterwave.ng', 'assessor10', 'Tobi', 'Akin', 'Flutterwave'),
    ]
    
    assessors = []
    for email, username, first, last, org in assessors_data:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': first,
                'last_name': last,
                'role': User.Role.ASSESSOR,
                'organization': org,
                'is_verified': True,
            }
        )
        if created:
            user.set_password('Assessor@2026!')
            user.save()
            print(f"  Created assessor: {user.email}")
        assessors.append(user)
    
    # Viewers (10)
    viewers_data = [
        ('viewer1@cbn.gov.ng', 'viewer1', 'Halima', 'Sani', 'CBN'),
        ('viewer2@ndic.gov.ng', 'viewer2', 'Peter', 'Obi', 'NDIC'),
        ('viewer3@nitda.gov.ng', 'viewer3', 'Grace', 'Okafor', 'NITDA'),
        ('viewer4@stanbic.ng', 'viewer4', 'Musa', 'Danladi', 'Stanbic IBTC'),
        ('viewer5@fidelity.ng', 'viewer5', 'Lara', 'Johnson', 'Fidelity Bank'),
        ('viewer6@unionbank.ng', 'viewer6', 'Chuka', 'Obi', 'Union Bank'),
        ('viewer7@ecobank.ng', 'viewer7', 'Nkechi', 'Umeh', 'Ecobank'),
        ('viewer8@sterling.ng', 'viewer8', 'Adebayo', 'Ojo', 'Sterling Bank'),
        ('viewer9@fcmb.ng', 'viewer9', 'Zainab', 'Lawal', 'FCMB'),
        ('viewer10@wema.ng', 'viewer10', 'John', 'Okafor', 'Wema Bank'),
    ]
    
    viewers = []
    for email, username, first, last, org in viewers_data:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': first,
                'last_name': last,
                'role': User.Role.VIEWER,
                'organization': org,
                'is_verified': True,
            }
        )
        if created:
            user.set_password('Viewer@2026!')
            user.save()
            print(f"  Created viewer: {user.email}")
        viewers.append(user)
    
    print(f"✅ Total users: {User.objects.count()}")
    return {
        'admin': admin,
        'analysts': analysts,
        'assessors': assessors,
        'viewers': viewers,
    }


def create_institutions(users):
    """Create 12 institutions"""
    print("\nCreating institutions...")
    
    institutions_data = [
        ('First Bank of Nigeria', 'bank', 'RC123456', 'https://www.firstbanknigeria.com', 'info@firstbanknigeria.com', '+2348012345678'),
        ('Zenith Bank', 'bank', 'RC456789', 'https://www.zenithbank.com', 'info@zenithbank.com', '+2348023456789'),
        ('GTBank', 'bank', 'RC789012', 'https://www.gtbank.com', 'info@gtbank.com', '+2348034567890'),
        ('Access Bank', 'bank', 'RC345678', 'https://www.accessbankplc.com', 'info@accessbankplc.com', '+2348045678901'),
        ('UBA', 'bank', 'RC901234', 'https://www.ubagroup.com', 'info@ubagroup.com', '+2348056789012'),
        ('PalmPay', 'fintech', 'RC567890', 'https://www.palmpay.com', 'info@palmpay.com', '+2348067890123'),
        ('OPay', 'fintech', 'RC234567', 'https://www.opay.com', 'info@opay.com', '+2348078901234'),
        ('Kuda Bank', 'fintech', 'RC890123', 'https://www.kuda.com', 'info@kuda.com', '+2348089012345'),
        ('Moniepoint', 'fintech', 'RC678901', 'https://www.moniepoint.com', 'info@moniepoint.com', '+2348090123456'),
        ('Flutterwave', 'fintech', 'RC456123', 'https://www.flutterwave.com', 'info@flutterwave.com', '+2348101234567'),
        ('Lagos Microfinance Bank', 'mfbank', 'RC789456', 'https://www.lagosmfb.com', 'info@lagosmfb.com', '+2348112345678'),
        ('Nigeria Payment Services', 'payment', 'RC123789', 'https://www.nigeriapay.com', 'info@nigeriapay.com', '+2348123456789'),
    ]
    
    institutions = []
    for name, type_, reg_no, website, email, phone in institutions_data:
        inst, created = Institution.objects.get_or_create(
            name=name,
            defaults={
                'type': type_,
                'registration_number': reg_no,
                'website': website,
                'email': email,
                'phone': phone,
                'platform_url': f'https://{name.lower().replace(" ", "")}.ng',
                'created_by': users['admin'],
            }
        )
        if created:
            print(f"  Created institution: {inst.name}")
        institutions.append(inst)
    
    print(f"✅ Total institutions: {Institution.objects.count()}")
    return institutions


def create_assessments(users, institutions):
    """Create 15 assessments with different risk levels"""
    print("\nCreating assessments...")
    
    engine = RiskScoringEngine()
    questions = list(AssessmentQuestion.objects.all())
    
    if not questions:
        print("❌ No questions found. Run seed_questions first!")
        return []
    
    # Define assessment scenarios with target risk levels
    scenarios = [
        # (title, institution_index, assessor_index, risk_profile)
        # risk_profile: 1 = critical (low scores), 5 = negligible (high scores)
        ('Critical Risk Assessment - First Bank', 0, 0, 1),
        ('High Risk Assessment - Zenith Bank', 1, 1, 2),
        ('Medium Risk Assessment - GTBank', 2, 2, 3),
        ('Low Risk Assessment - Access Bank', 3, 3, 4),
        ('Negligible Risk - UBA', 4, 4, 5),
        ('Critical Risk - PalmPay', 5, 5, 1),
        ('High Risk - OPay', 6, 6, 2),
        ('Medium Risk - Kuda Bank', 7, 7, 3),
        ('Low Risk - Moniepoint', 8, 8, 4),
        ('Negligible Risk - Flutterwave', 9, 9, 5),
        ('Medium Risk - Lagos MFB', 10, 0, 3),
        ('High Risk - Nigeria Payment', 11, 1, 2),
        ('Critical Risk - First Bank Q2', 0, 2, 1),
        ('Low Risk - Zenith Bank Q2', 1, 3, 4),
        ('Medium Risk - GTBank Q2', 2, 4, 3),
    ]
    
    assessments = []
    
    for title, inst_idx, assessor_idx, risk_profile in scenarios:
        institution = institutions[inst_idx % len(institutions)]
        assessor = users['assessors'][assessor_idx % len(users['assessors'])]
        
        # Create assessment
        assessment = Assessment.objects.create(
            institution=institution,
            assessor=assessor,
            title=title,
            description=f"{title} - comprehensive security assessment",
            status=Assessment.Status.SUBMITTED,
        )
        
        # Set a random date in the past (for historical trends)
        days_ago = random.randint(1, 120)
        assessment.created_at = timezone.now() - timedelta(days=days_ago)
        assessment.submitted_at = assessment.created_at + timedelta(days=1)
        assessment.save()
        
        # Create responses based on risk profile
        # risk_profile 1 = critical (scores 0-1)
        # risk_profile 2 = high (scores 1-2)
        # risk_profile 3 = medium (scores 2-3)
        # risk_profile 4 = low (scores 3-4)
        # risk_profile 5 = negligible (scores 4-5)
        
        score_ranges = {
            1: (0, 1),  # critical
            2: (1, 2),  # high
            3: (2, 3),  # medium
            4: (3, 4),  # low
            5: (4, 5),  # negligible
        }
        
        min_score, max_score = score_ranges[risk_profile]
        
        for q in questions:
            score = random.randint(min_score, max_score)
            AssessmentResponse.objects.create(
                assessment=assessment,
                question=q,
                score=score,
                evidence=f"Evidence for {q.question_text[:50]}...",
                notes=f"Notes for {q.question_text[:50]}...",
            )
        
        # Score the assessment
        responses = list(assessment.responses.select_related('question').all())
        result = engine.score_assessment(assessment, responses)
        assessment.save()
        
        # Create risk report
        report = RiskAssessmentReport.objects.create(
            assessment=assessment,
            generated_by=users['admin'],
            category_scores=result['category_scores'],
            overall_score=result['overall_score'],
            risk_level=result['risk_level']['level'],
            compliance=result['compliance'],
            critical_findings=result['findings']['critical'],
            high_findings=result['findings']['high'],
            medium_findings=result['findings']['medium'],
            low_findings=result['findings']['low'],
        )
        
        # Set report date to match assessment date
        report.generated_at = assessment.submitted_at
        report.save()
        
        print(f"  Created: {title} | Risk: {assessment.risk_level} | Score: {assessment.overall_score}")
        assessments.append(assessment)
    
    print(f"✅ Total assessments: {Assessment.objects.count()}")
    return assessments


def create_security_trends():
    """Create historical security trends data"""
    print("\nCreating security trends...")
    
    # Clear existing trends
    SecurityTrend.objects.all().delete()
    
    # Create 6 months of trends
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        
        trend, created = SecurityTrend.objects.get_or_create(
            period=month_start.date(),
            defaults={
                'total_assessments': random.randint(5, 15),
                'average_score': random.uniform(45, 80),
                'critical_count': random.randint(0, 3),
                'high_count': random.randint(1, 5),
                'medium_count': random.randint(2, 6),
                'low_count': random.randint(1, 4),
                'negligible_count': random.randint(0, 2),
            }
        )
        if created:
            print(f"  Created trend: {month_start.strftime('%Y-%m')}")
    
    print(f"✅ Total trends: {SecurityTrend.objects.count()}")


def create_audit_logs(users):
    """Create dummy audit logs"""
    print("\nCreating audit logs...")
    
    # Clear existing logs
    AuditLog.objects.all().delete()
    
    actions = [
        'login_success', 'login_failed', 'user_registered', 
        'assessment_created', 'assessment_submitted', 
        'assessment_scored', 'report_generated', 
        'password_changed', 'institution_created',
        'user_updated_by_admin', 'role_changed',
        'question_bank_seeded', 'assessment_exported'
    ]
    
    all_users = list(users['analysts'] + users['assessors'] + users['viewers'])
    
    for i in range(50):
        user = random.choice(all_users)
        action = random.choice(actions)
        
        # Random date in past 90 days
        days_ago = random.randint(0, 90)
        timestamp = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        log = AuditLog.objects.create(
            user=user,
            action=action,
            ip_address=f"192.168.1.{random.randint(1, 255)}",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
            details={
                'description': f'{action} performed by {user.email}',
                'timestamp': timestamp.isoformat(),
            },
        )
        log.created_at = timestamp
        log.save()
        
    print(f"✅ Total audit logs: {AuditLog.objects.count()}")


def print_summary():
    """Print complete summary of all data"""
    print("\n" + "="*60)
    print("🎉 TEST DATA CREATION COMPLETE!")
    print("="*60)
    
    print("\n📊 DATABASE SUMMARY")
    print("-"*40)
    print(f"👤 Users: {User.objects.count()}")
    
    by_role = {}
    for role, count in User.objects.values_list('role').annotate(count=models.Count('id')):
        by_role[role] = count
    print(f"   - Admins: {by_role.get('admin', 0)}")
    print(f"   - Analysts: {by_role.get('analyst', 0)}")
    print(f"   - Assessors: {by_role.get('assessor', 0)}")
    print(f"   - Viewers: {by_role.get('viewer', 0)}")
    
    print(f"🏦 Institutions: {Institution.objects.count()}")
    print(f"📋 Assessments: {Assessment.objects.count()}")
    print(f"📝 Questions: {AssessmentQuestion.objects.count()}")
    print(f"📄 Reports: {RiskAssessmentReport.objects.count()}")
    print(f"📈 Trends: {SecurityTrend.objects.count()}")
    print(f"📜 Audit Logs: {AuditLog.objects.count()}")
    
    # Risk level distribution
    print("\n🎯 RISK LEVEL DISTRIBUTION")
    print("-"*40)
    for risk_level in ['critical', 'high', 'medium', 'low', 'negligible']:
        count = Assessment.objects.filter(risk_level=risk_level).count()
        print(f"   {risk_level.upper():15}: {count}")
    
    # Average scores
    from django.db.models import Avg
    avg_score = Assessment.objects.aggregate(avg=Avg('overall_score'))['avg']
    print(f"\n📈 Average Risk Score: {round(avg_score, 2) if avg_score else 'N/A'}")
    
    print("\n✅ TEST DATA READY FOR USE!")


if __name__ == '__main__':
    from django.db import models
    
    print("🔄 Starting test data creation...")
    users = create_users()
    institutions = create_institutions(users)
    assessments = create_assessments(users, institutions)
    create_security_trends()
    create_audit_logs(users)
    print_summary()