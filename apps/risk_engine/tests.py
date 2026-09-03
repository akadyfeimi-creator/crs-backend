from types import SimpleNamespace
from django.test import SimpleTestCase
from apps.risk_engine.scoring import RiskScoringEngine


def make_response(category, score, weight=1.0):
    """A lightweight stand-in for AssessmentResponse, so these are fast unit
    tests that don't need the database."""
    question = SimpleNamespace(
        category=category, weight=weight,
        question_text=f"{category} control", framework_reference="TEST-1",
    )
    return SimpleNamespace(
        question=question, score=score,
        get_score_display=lambda: str(score),
    )


class RiskScoringEngineTests(SimpleTestCase):
    """
    Unit tests for Objective 2: the risk scoring framework.
    These check the maths directly, independent of the web layer.
    """

    def setUp(self):
        self.engine = RiskScoringEngine()

    def test_category_score_is_100_when_all_answers_are_maximum(self):
        responses = [make_response("authentication", 5), make_response("authentication", 5)]
        score = self.engine.calculate_category_score(responses, "authentication")
        self.assertEqual(score, 100.0)

    def test_category_score_is_0_when_all_answers_are_minimum(self):
        responses = [make_response("authentication", 0)]
        score = self.engine.calculate_category_score(responses, "authentication")
        self.assertEqual(score, 0.0)

    def test_category_score_is_none_when_category_has_no_responses(self):
        responses = [make_response("authentication", 5)]
        score = self.engine.calculate_category_score(responses, "encryption")
        self.assertIsNone(score)

    def test_overall_score_is_weighted_average_of_categories(self):
        category_scores = {"authentication": 100, "encryption": 0}
        overall = self.engine.calculate_overall_score(category_scores)
        # weights: authentication=0.20, encryption=0.20 -> equal weight -> midpoint
        self.assertEqual(overall, 50.0)

    def test_risk_level_boundaries_are_correctly_classified(self):
        self.assertEqual(self.engine.get_risk_level(10)["level"], "critical")
        self.assertEqual(self.engine.get_risk_level(45)["level"], "high")
        self.assertEqual(self.engine.get_risk_level(60)["level"], "medium")
        self.assertEqual(self.engine.get_risk_level(75)["level"], "low")
        self.assertEqual(self.engine.get_risk_level(90)["level"], "negligible")

    def test_compliance_scores_average_the_mapped_categories(self):
        category_scores = {
            "authentication": 80, "encryption": 60, "api_security": 100,
            "data_storage": 40, "network_security": 50, "incident_response": 70,
            "third_party": 90, "compliance": 30,
        }
        compliance = self.engine.calculate_compliance_scores(category_scores)
        # owasp = avg(authentication, encryption, api_security, data_storage)
        expected_owasp = round((80 + 60 + 100 + 40) / 4, 2)
        self.assertEqual(compliance["owasp"], expected_owasp)

    def test_build_findings_flags_weak_responses_by_severity(self):
        responses = [
            make_response("authentication", 0),  # critical
            make_response("encryption", 1),       # high
            make_response("api_security", 2),     # medium
            make_response("data_storage", 4),     # not a finding (>2)
        ]
        findings = self.engine.build_findings(responses)
        self.assertEqual(len(findings["critical"]), 1)
        self.assertEqual(len(findings["high"]), 1)
        self.assertEqual(len(findings["medium"]), 1)
        self.assertEqual(len(findings["low"]), 0)

    def test_full_pipeline_score_assessment_end_to_end(self):
        assessment = SimpleNamespace()
        responses = [make_response(cat, 5) for cat in [
            "authentication", "encryption", "api_security", "data_storage",
            "network_security", "incident_response", "third_party", "compliance",
        ]]
        result = self.engine.score_assessment(assessment, responses)
        self.assertEqual(result["overall_score"], 100.0)
        self.assertEqual(result["risk_level"]["level"], "negligible")
        self.assertEqual(assessment.risk_level, "negligible")
