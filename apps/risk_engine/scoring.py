"""
Risk Scoring Engine
====================
This module is the technical realisation of Objective 2 of the MSc
proposal — "Design the risk scoring framework which will be used in
determining the link between the risk factors and the security
framework" — and is invoked by Objective 3 (the web application) every
time an assessment is submitted.
"""

RISK_LEVELS = {
    "critical":   {"min": 0,  "max": 39,  "color": "#dc2626", "description": "Immediate action required — multiple critical control gaps found."},
    "high":       {"min": 40, "max": 54,  "color": "#ea580c", "description": "High risk — prioritise remediation within 30 days."},
    "medium":     {"min": 55, "max": 69,  "color": "#ca8a04", "description": "Medium risk — develop a remediation plan for the next review cycle."},
    "low":        {"min": 70, "max": 84,  "color": "#16a34a", "description": "Low risk — monitor and maintain current controls."},
    "negligible": {"min": 85, "max": 100, "color": "#22c55e", "description": "No significant risks identified; controls meet or exceed expectations."},
}

# Higher score = lower risk (score is a "security maturity" score, 100 = fully secure).
CATEGORY_WEIGHTS = {
    "authentication": 0.20,
    "encryption": 0.20,
    "api_security": 0.15,
    "data_storage": 0.15,
    "network_security": 0.10,
    "incident_response": 0.10,
    "third_party": 0.05,
    "compliance": 0.05,
}

FRAMEWORK_CATEGORY_MAP = {
    "owasp": ["authentication", "encryption", "api_security", "data_storage"],
    "nist": ["authentication", "network_security", "incident_response", "data_storage"],
    "cbn": ["compliance", "authentication", "data_storage", "third_party"],
}

MAX_MATURITY = 5  # AssessmentResponse.Score.EXCEEDS

# Category-specific recommendations
CATEGORY_RECOMMENDATIONS = {
    "authentication": {
        "critical": [
            "Implement multi-factor authentication (MFA) for all user accounts immediately.",
            "Enforce strong password policies (minimum 12 characters, special characters).",
            "Implement account lockout after 5 failed login attempts.",
            "Use Argon2 or bcrypt for password hashing.",
        ],
        "high": [
            "Implement MFA for all sensitive operations.",
            "Strengthen password policies to meet OWASP standards.",
            "Implement session timeout after 15 minutes of inactivity.",
        ],
        "medium": [
            "Review current authentication mechanisms and identify gaps.",
            "Consider implementing MFA for high-risk transactions.",
            "Strengthen password reset process with identity verification.",
        ],
        "low": [
            "Maintain current authentication controls.",
            "Periodically review and update authentication policies.",
            "Monitor for unusual login patterns.",
        ],
    },
    "encryption": {
        "critical": [
            "Implement TLS 1.3 for all data in transit immediately.",
            "Encrypt all sensitive data at rest using AES-256.",
            "Implement certificate pinning to prevent MITM attacks.",
            "Use a secure key management service (KMS) for cryptographic keys.",
        ],
        "high": [
            "Upgrade to TLS 1.3 for all API communication.",
            "Encrypt sensitive data at rest.",
            "Implement certificate pinning for mobile apps.",
            "Rotate cryptographic keys regularly.",
        ],
        "medium": [
            "Review encryption protocols and upgrade to modern standards.",
            "Ensure all backups are encrypted.",
            "Consider implementing certificate pinning.",
        ],
        "low": [
            "Maintain current encryption standards.",
            "Periodically audit encryption practices.",
            "Stay updated with latest encryption best practices.",
        ],
    },
    "api_security": {
        "critical": [
            "Implement proper authentication and authorization on ALL API endpoints.",
            "Sanitize all client-supplied input to prevent SQL injection and XSS.",
            "Implement API rate limiting to prevent brute-force attacks.",
            "Never expose API keys in client-side code.",
        ],
        "high": [
            "Add authentication to unprotected API endpoints.",
            "Implement input validation for all API requests.",
            "Add rate limiting to sensitive API endpoints.",
            "Rotate API keys regularly.",
        ],
        "medium": [
            "Review API endpoints for proper access control.",
            "Implement basic rate limiting on all endpoints.",
            "Add input validation where missing.",
        ],
        "low": [
            "Maintain current API security controls.",
            "Periodically test APIs for vulnerabilities.",
            "Monitor API usage for suspicious activity.",
        ],
    },
    "data_storage": {
        "critical": [
            "Implement NDPR-compliant data protection immediately.",
            "Minimize collection of sensitive customer data (BVN, NIN, card data).",
            "Encrypt all sensitive data in storage.",
            "Implement data retention and disposal policies.",
        ],
        "high": [
            "Review data storage practices to ensure NDPR compliance.",
            "Encrypt sensitive data at rest.",
            "Implement data minimization principles.",
            "Secure backups with encryption and access controls.",
        ],
        "medium": [
            "Review data handling procedures.",
            "Implement data classification and handling policies.",
            "Ensure backups are properly secured.",
        ],
        "low": [
            "Maintain current data protection practices.",
            "Periodically review data storage policies.",
            "Stay updated with NDPR requirements.",
        ],
    },
    "network_security": {
        "critical": [
            "Implement network segmentation to prevent lateral movement.",
            "Deploy intrusion detection/prevention systems (IDS/IPS).",
            "Conduct vulnerability scans at least monthly.",
            "Deploy a Web Application Firewall (WAF).",
        ],
        "high": [
            "Implement network segmentation for sensitive systems.",
            "Deploy IDS/IPS to monitor network traffic.",
            "Conduct quarterly vulnerability scans.",
            "Add WAF to protect public-facing services.",
        ],
        "medium": [
            "Review network security architecture.",
            "Consider implementing network segmentation.",
            "Schedule regular vulnerability scans.",
        ],
        "low": [
            "Maintain current network security controls.",
            "Periodically review firewall rules.",
            "Monitor network traffic for anomalies.",
        ],
    },
    "incident_response": {
        "critical": [
            "Develop and test an incident response plan immediately.",
            "Implement 24/7 monitoring and logging (SIEM/SOC).",
            "Establish reporting procedures to CBN/NDIC within required timeframes.",
            "Develop disaster recovery and business continuity plans.",
        ],
        "high": [
            "Create a formal incident response plan.",
            "Implement security monitoring and logging.",
            "Establish regulatory reporting procedures.",
            "Develop a disaster recovery plan.",
        ],
        "medium": [
            "Document an incident response plan.",
            "Implement basic logging and monitoring.",
            "Ensure regulatory reporting procedures are in place.",
        ],
        "low": [
            "Maintain current incident response capabilities.",
            "Periodically test incident response plans.",
            "Stay updated with regulatory reporting requirements.",
        ],
    },
    "third_party": {
        "critical": [
            "Conduct security risk assessments on ALL third-party vendors immediately.",
            "Include security and data-protection obligations in all vendor contracts.",
            "Ensure payment processors are PCI-DSS certified.",
            "Terminate relationships with non-compliant vendors.",
        ],
        "high": [
            "Implement vendor security risk assessments before onboarding.",
            "Add security clauses to vendor contracts.",
            "Ensure third parties meet PCI-DSS standards.",
            "Monitor third-party security posture regularly.",
        ],
        "medium": [
            "Review third-party relationships for security risks.",
            "Add basic security requirements to vendor contracts.",
            "Assess third-party security practices.",
        ],
        "low": [
            "Maintain current third-party risk controls.",
            "Periodically review vendor security.",
            "Stay updated with supply-chain security best practices.",
        ],
    },
    "compliance": {
        "critical": [
            "Submit required Cybersecurity Self-Assessment to CBN immediately.",
            "Appoint a Chief Information Security Officer (CISO).",
            "Establish board-level oversight of cybersecurity risk.",
            "Implement annual cybersecurity awareness training for all staff.",
        ],
        "high": [
            "Ensure CBN Cybersecurity Self-Assessment is submitted on time.",
            "Appoint a dedicated CISO or security lead.",
            "Establish board-level security committee.",
            "Conduct annual security awareness training.",
        ],
        "medium": [
            "Review CBN compliance requirements.",
            "Ensure security policies are documented and reviewed annually.",
            "Consider appointing a security officer.",
        ],
        "low": [
            "Maintain current compliance posture.",
            "Stay updated with CBN regulatory requirements.",
            "Maintain cybersecurity policies and procedures.",
        ],
    },
}

# General recommendations based on risk level
GENERAL_RECOMMENDATIONS = {
    "critical": [
        "Immediate remediation required - allocate resources to address critical vulnerabilities.",
        "Engage external cybersecurity experts for a comprehensive security audit.",
        "Implement a prioritized remediation plan with clear timelines.",
        "Consider temporary measures to reduce risk (e.g., restrict access, disable vulnerable features).",
        "Notify relevant stakeholders and regulators as required.",
    ],
    "high": [
        "Prioritize remediation of high-risk vulnerabilities within 30 days.",
        "Develop a formal remediation plan with assigned responsibilities.",
        "Increase security monitoring and logging.",
        "Conduct a detailed security review of affected systems.",
    ],
    "medium": [
        "Develop a remediation plan for identified weaknesses.",
        "Schedule improvements for the next review cycle.",
        "Monitor security posture closely.",
        "Address medium-risk findings in a timely manner.",
    ],
    "low": [
        "Continue to monitor and maintain current security controls.",
        "Periodically review and update security policies.",
        "Stay informed about emerging threats and best practices.",
    ],
    "negligible": [
        "No significant risks identified - maintain current security posture.",
        "Continue regular security assessments to ensure ongoing compliance.",
        "Stay updated with evolving security threats and frameworks.",
    ],
}


class RiskScoringEngine:
    def calculate_category_score(self, responses, category):
        """responses: iterable of AssessmentResponse (with .question prefetched)"""
        filtered = [r for r in responses if r.question.category == category]
        if not filtered:
            return None
        weighted_total = sum(r.score * r.question.weight for r in filtered)
        weighted_max = sum(MAX_MATURITY * r.question.weight for r in filtered)
        if weighted_max == 0:
            return None
        return round((weighted_total / weighted_max) * 100, 2)

    def calculate_all_category_scores(self, responses):
        return {cat: self.calculate_category_score(responses, cat) for cat in CATEGORY_WEIGHTS}

    def calculate_overall_score(self, category_scores: dict):
        total, weight_sum = 0.0, 0.0
        for category, score in category_scores.items():
            if score is None:
                continue
            weight = CATEGORY_WEIGHTS.get(category, 0.1)
            total += score * weight
            weight_sum += weight
        if weight_sum == 0:
            return 0.0
        return round(total / weight_sum, 2)

    def get_risk_level(self, score: float):
        for level, bounds in RISK_LEVELS.items():
            if bounds["min"] <= score <= bounds["max"]:
                return {"level": level, **bounds}
        return {"level": "medium", **RISK_LEVELS["medium"]}

    def calculate_compliance_scores(self, category_scores: dict):
        compliance = {}
        for framework, categories in FRAMEWORK_CATEGORY_MAP.items():
            scores = [category_scores[c] for c in categories if category_scores.get(c) is not None]
            compliance[framework] = round(sum(scores) / len(scores), 2) if scores else 0.0
        return compliance

    def build_findings(self, responses):
        """Group weak responses (score <= 2) into severity buckets for the report."""
        findings = {"critical": [], "high": [], "medium": [], "low": []}
        for r in responses:
            if r.score == 0:
                bucket = "critical"
            elif r.score == 1:
                bucket = "high"
            elif r.score == 2:
                bucket = "medium"
            else:
                continue
            findings[bucket].append({
                "category": r.question.category,
                "control": r.question.question_text,
                "framework_reference": r.question.framework_reference,
                "current_maturity": r.get_score_display(),
                "recommendation": self._recommend(r),
            })
        return findings

    def _recommend(self, response):
        """Generate specific recommendation for a weak response."""
        category = response.question.category
        score = response.score
        
        if category in CATEGORY_RECOMMENDATIONS:
            if score <= 1:
                level = "critical"
            elif score == 2:
                level = "high"
            else:
                level = "medium"
            
            recommendations = CATEGORY_RECOMMENDATIONS[category].get(level, [])
            if recommendations:
                return recommendations[0]
        
        # Default recommendation
        return f"Implement and evidence '{response.question.question_text}' to at least an 'Implemented and Effective' maturity level."

    def build_recommendations(self, category_scores, risk_level):
        """Generate comprehensive recommendations based on category scores and risk level."""
        recommendations = {}
        
        # Add category-specific recommendations
        for category, score in category_scores.items():
            if score is None:
                continue
            
            if score < 40:
                level = "critical"
            elif score < 55:
                level = "high"
            elif score < 70:
                level = "medium"
            elif score < 85:
                level = "low"
            else:
                level = "negligible"
            
            category_recs = CATEGORY_RECOMMENDATIONS.get(category, {}).get(level, [])
            recommendations[category] = {
                "score": score,
                "level": level,
                "recommendations": category_recs,
            }
        
        # Add general recommendations based on overall risk level
        recommendations["general"] = GENERAL_RECOMMENDATIONS.get(risk_level, [])
        
        return recommendations

    def score_assessment(self, assessment, responses):
        """Full pipeline: compute and persist all scores on the Assessment instance."""
        category_scores = self.calculate_all_category_scores(responses)
        overall = self.calculate_overall_score(category_scores)
        risk = self.get_risk_level(overall)
        compliance = self.calculate_compliance_scores(category_scores)

        assessment.authentication_score = category_scores["authentication"]
        assessment.encryption_score = category_scores["encryption"]
        assessment.api_security_score = category_scores["api_security"]
        assessment.data_storage_score = category_scores["data_storage"]
        assessment.network_security_score = category_scores["network_security"]
        assessment.incident_response_score = category_scores["incident_response"]
        assessment.third_party_score = category_scores["third_party"]
        assessment.compliance_score = category_scores["compliance"]

        assessment.overall_score = overall
        assessment.risk_level = risk["level"]
        assessment.owasp_compliance = compliance["owasp"]
        assessment.nist_compliance = compliance["nist"]
        assessment.cbn_compliance = compliance["cbn"]

        # Build recommendations
        recommendations = self.build_recommendations(category_scores, risk["level"])

        return {
            "category_scores": category_scores,
            "overall_score": overall,
            "risk_level": risk,
            "compliance": compliance,
            "findings": self.build_findings(responses),
            "recommendations": recommendations,
        }