from django.core.management.base import BaseCommand
from apps.assessments.models import AssessmentQuestion
from apps.risk_engine.frameworks.owasp_masvs import OWASP_MASVS_CONTROLS
from apps.risk_engine.frameworks.nist_csf import NIST_CSF_CONTROLS
from apps.risk_engine.frameworks.cbn_framework import CBN_CONTROLS


class Command(BaseCommand):
    help = "Seeds the AssessmentQuestion table with OWASP MASVS, NIST CSF and CBN control questions."

    def handle(self, *args, **options):
        controls = [
            ("owasp", OWASP_MASVS_CONTROLS),
            ("nist", NIST_CSF_CONTROLS),
            ("cbn", CBN_CONTROLS),
        ]
        created = 0
        skipped = 0
        
        for framework, framework_controls in controls:
            for c in framework_controls:
                _, was_created = AssessmentQuestion.objects.get_or_create(
                    framework=framework,
                    framework_reference=c["framework_reference"],
                    defaults={
                        "category": c["category"],
                        "question_text": c["question"],
                        "description": c.get("description", ""),
                        "weight": c.get("weight", 1.0),
                    },
                )
                if was_created:
                    created += 1
                else:
                    skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"Question bank seeded: {created} created, {skipped} already existed."
        ))