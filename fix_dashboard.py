"""
Fix Dashboard - Create Assessments and Data
Run this script to populate the database with real assessment data
"""

import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cyberrisk.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import User, AuditLog
from apps.institutions.models import Institution
from apps.assessments.models import Assessment, AssessmentQuestion, AssessmentResponse
from apps.risk_engine.scoring import RiskScoringEngine
from apps.risk_engine.models import RiskAssessmentReport, SecurityTrend

User = get_user_model()

def create_assessments():
    """Create real assessments with responses"""
    print("\n🔍 Creating assessments...")
    
    # Get admin user
    admin = User.objects.filter(email='admin@gmail.com').first()
    if not admin:
        admin = User.objects.filter(is_superuser=True).first()
    
    if not admin:
        print("❌ No admin user found! Run createsuperuser first.")
        return
    
    # Get assessors
    assessors = list(User.objects.filter(role='assessor'))
    if not assessors:
        # Use admin as fallback
        assessors = [admin]
    
    # Get institutions
    institutions = list(Institution.objects.all())
    if not institutions:
        print("❌ No institutions found! Add institutions first.")
        return
    
    # Get questions
    questions = list(AssessmentQuestion.objects.all())
    if not questions:
        print("❌ No questions found! Run seed_questions first.")
        return
    
    print(f"✅ Found: {len(institutions)} institutions, {len(assessors)} assessors, {len(questions)} questions")
    
    # Check if assessments already exist
    existing = Assessment.objects.count()
    if existing > 0:
        print(f"⚠️ {existing} assessments already exist. Skipping creation.")
        return
    
    engine = RiskScoringEngine()
    
    # Define 15 scenarios with different risk levels
    # score_range: (min_score, max_score) for each question
    # 1 = critical (scores 0-1), 5 = negligible (scores 4-5)
    
    scenarios = [
        # (title, institution_index, assessor_index, risk_profile)
        ("Critical Risk Assessment - First Bank", 0, 0, 1),
        ("High Risk Assessment - Zenith Bank", 1, 0, 2),
        ("Medium Risk Assessment - GTBank", 2, 0, 3),
        ("Low Risk Assessment - Access Bank", 3, 0, 4),
        ("Negligible Risk - UBA", 4, 0, 5),
        ("Critical Risk - PalmPay", 5, 0, 1),
        ("High Risk - OPay", 6, 0, 2),
        ("Medium Risk - Kuda Bank", 7, 0, 3),
        ("Low Risk - Moniepoint", 8, 0, 4),
        ("Negligible Risk - Flutterwave", 9, 0, 5),
        ("Medium Risk - Lagos MFB", 10, 0, 3),
        ("High Risk - Nigeria Payment", 11, 0, 2),
        ("Critical Risk - First Bank Q2", 0, 0, 1),
        ("Low Risk - Zenith Bank Q2", 1, 0, 4),
        ("Medium Risk - GTBank Q2", 2, 0, 3),
    ]
    
    score_ranges = {
        1: (0, 1),  # critical
        2: (1, 2),  # high
        3: (2, 3),  # medium
        4: (3, 4),  # low
        5: (4, 5),  # negligible
    }
    
    created_count = 0
    
    for title, inst_idx, assessor_idx, risk_profile in scenarios:
        institution = institutions[inst_idx % len(institutions)]
        assessor = assessors[assessor_idx % len(assessors)]
        
        # Create assessment with a past date (for history)
        days_ago = random.randint(10, 90)
        created_date = timezone.now() - timedelta(days=days_ago)
        
        assessment = Assessment.objects.create(
            institution=institution,
            assessor=assessor,
            title=title,
            description=f"{title} - comprehensive security assessment",
            status=Assessment.Status.SUBMITTED,
            created_at=created_date,
            updated_at=created_date,
            submitted_at=created_date + timedelta(days=1),
        )
        
        # Create responses based on risk profile
        min_score, max_score = score_ranges[risk_profile]
        
        for q in questions:
            score = random.randint(min_score, max_score)
            AssessmentResponse.objects.create(
                assessment=assessment,
                question=q,
                score=score,
                evidence=f"Evidence for {q.question_text[:50]}...",
                notes=f"Assessed on {created_date.strftime('%Y-%m-%d')}",
                created_at=created_date,
                updated_at=created_date,
            )
        
        # Score the assessment
        responses = list(assessment.responses.select_related('question').all())
        result = engine.score_assessment(assessment, responses)
        
        # Save all scores
        assessment.overall_score = result['overall_score']
        assessment.risk_level = result['risk_level']['level']
        assessment.authentication_score = result['category_scores'].get('authentication')
        assessment.encryption_score = result['category_scores'].get('encryption')
        assessment.api_security_score = result['category_scores'].get('api_security')
        assessment.data_storage_score = result['category_scores'].get('data_storage')
        assessment.network_security_score = result['category_scores'].get('network_security')
        assessment.incident_response_score = result['category_scores'].get('incident_response')
        assessment.third_party_score = result['category_scores'].get('third_party')
        assessment.compliance_score = result['category_scores'].get('compliance')
        assessment.owasp_compliance = result['compliance'].get('owasp')
        assessment.nist_compliance = result['compliance'].get('nist')
        assessment.cbn_compliance = result['compliance'].get('cbn')
        assessment.save()
        
        # Create risk report
        RiskAssessmentReport.objects.create(
            assessment=assessment,
            generated_by=admin,
            category_scores=result['category_scores'],
            overall_score=result['overall_score'],
            risk_level=result['risk_level']['level'],
            compliance=result['compliance'],
            critical_findings=result['findings']['critical'],
            high_findings=result['findings']['high'],
            medium_findings=result['findings']['medium'],
            low_findings=result['findings']['low'],
            generated_at=created_date + timedelta(days=1),
        )
        
        print(f"  ✅ Created: {title}")
        print(f"     Risk: {assessment.risk_level} | Score: {assessment.overall_score}")
        created_count += 1
    
    print(f"\n✅ Total assessments created: {created_count}")


def create_security_trends():
    """Create historical security trends"""
    print("\n📊 Creating security trends...")
    
    # Delete existing trends
    SecurityTrend.objects.all().delete()
    
    # Create 6 months of trends
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30 * i)
        
        SecurityTrend.objects.create(
            period=month_start.date(),
            total_assessments=random.randint(8, 20),
            average_score=random.uniform(45, 85),
            critical_count=random.randint(0, 3),
            high_count=random.randint(1, 5),
            medium_count=random.randint(2, 6),
            low_count=random.randint(1, 4),
            negligible_count=random.randint(0, 2),
        )
        print(f"  ✅ Created trend for {month_start.strftime('%B %Y')}")
    
    print(f"✅ Total trends: {SecurityTrend.objects.count()}")


def create_audit_logs():
    """Create audit logs"""
    print("\n📜 Creating audit logs...")
    
    # Clear existing
    AuditLog.objects.all().delete()
    
    # Get users
    users = list(User.objects.all())
    if not users:
        return
    
    actions = [
        'login_success', 'login_failed', 'user_registered',
        'assessment_created', 'assessment_submitted',
        'assessment_scored', 'report_generated',
        'password_changed', 'institution_created',
    ]
    
    for i in range(50):
        user = random.choice(users)
        action = random.choice(actions)
        
        days_ago = random.randint(0, 90)
        timestamp = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        log = AuditLog.objects.create(
            user=user,
            action=action,
            ip_address=f"192.168.1.{random.randint(1, 255)}",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
            details={'description': f'{action} performed by {user.email}'},
        )
        log.created_at = timestamp
        log.save()
    
    print(f"✅ Total audit logs: {AuditLog.objects.count()}")


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 FIXING DASHBOARD - CREATING DATA")
    print("=" * 60)
    
    create_assessments()
    create_security_trends()
    create_audit_logs()
    
    # Print summary
    from django.db.models import Avg
    
    print("\n" + "=" * 60)
    print("📊 DATABASE SUMMARY")
    print("=" * 60)
    print(f"👤 Users: {User.objects.count()}")
    print(f"🏦 Institutions: {Institution.objects.count()}")
    print(f"📋 Assessments: {Assessment.objects.count()}")
    print(f"📝 Questions: {AssessmentQuestion.objects.count()}")
    print(f"📄 Reports: {RiskAssessmentReport.objects.count()}")
    print(f"📈 Trends: {SecurityTrend.objects.count()}")
    
    # Risk distribution
    print("\n🎯 RISK LEVEL DISTRIBUTION:")
    for level in ['critical', 'high', 'medium', 'low', 'negligible']:
        count = Assessment.objects.filter(risk_level=level).count()
        print(f"  {level.upper():15}: {count}")
    
    # Average score
    avg = Assessment.objects.aggregate(avg=Avg('overall_score'))['avg']
    print(f"\n📈 Average Score: {round(avg, 2) if avg else 'N/A'}")
    
    print("\n✅ DASHBOARD DATA READY!")