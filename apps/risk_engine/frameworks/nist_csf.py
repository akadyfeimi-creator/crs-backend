"""NIST Cybersecurity Framework (CSF) controls, mapped to the five functions:
Identify, Protect, Detect, Respond, Recover."""

NIST_CSF_CONTROLS = [
    {"category": "authentication", "question": "Does the organization maintain an identity and access management (IAM) policy?", "description": "Formal IAM policy covering provisioning, review and de-provisioning.", "weight": 1.2, "framework_reference": "NIST-PR.AC-1"},
    {"category": "authentication", "question": "Are user access privileges reviewed at least quarterly?", "description": "Periodic access review reduces privilege creep.", "weight": 1.0, "framework_reference": "NIST-PR.AC-4"},
    {"category": "authentication", "question": "Is the principle of least privilege enforced for staff and system accounts?", "description": "Accounts should hold only the access required for their role.", "weight": 1.2, "framework_reference": "NIST-PR.AC-6"},

    {"category": "network_security", "question": "Are network boundaries protected with firewalls and network segmentation?", "description": "Segmenting sensitive systems limits lateral movement in a breach.", "weight": 1.2, "framework_reference": "NIST-PR.AC-5"},
    {"category": "network_security", "question": "Is intrusion detection/prevention (IDS/IPS) deployed and actively monitored?", "description": "Detects anomalous or malicious network activity in real time.", "weight": 1.2, "framework_reference": "NIST-DE.CM-1"},
    {"category": "network_security", "question": "Are vulnerability scans performed on infrastructure at least quarterly?", "description": "Regular scanning identifies exploitable weaknesses before attackers do.", "weight": 1.0, "framework_reference": "NIST-DE.CM-8"},
    {"category": "network_security", "question": "Is a Web Application Firewall (WAF) deployed in front of public-facing services?", "description": "WAFs mitigate common web application attacks (OWASP Top 10).", "weight": 1.0, "framework_reference": "NIST-PR.PT-3"},

    {"category": "incident_response", "question": "Does the organization have a documented and tested incident response plan?", "description": "A formal IR plan reduces detection-to-containment time.", "weight": 1.5, "framework_reference": "NIST-RS.RP-1"},
    {"category": "incident_response", "question": "Is there 24/7 monitoring/logging capable of detecting a security incident?", "description": "Continuous monitoring (SIEM/SOC) enables timely detection.", "weight": 1.2, "framework_reference": "NIST-DE.AE-3"},
    {"category": "incident_response", "question": "Are security incidents reported to relevant regulators (CBN/NDIC) within required timeframes?", "description": "Regulatory breach-notification timelines must be met.", "weight": 1.0, "framework_reference": "NIST-RS.CO-2"},
    {"category": "incident_response", "question": "Is there a documented disaster recovery / business continuity plan, tested annually?", "description": "Ensures recovery of critical services after a major incident.", "weight": 1.0, "framework_reference": "NIST-RC.RP-1"},

    {"category": "data_storage", "question": "Are data classification and handling procedures documented and enforced?", "description": "Clear rules for how different sensitivity levels of data must be handled.", "weight": 1.0, "framework_reference": "NIST-ID.AM-5"},
    {"category": "data_storage", "question": "Is a formal data retention and secure-disposal policy in place?", "description": "Data should not be retained beyond its legitimate business need.", "weight": 1.0, "framework_reference": "NIST-PR.DS-3"},

    {"category": "third_party", "question": "Are third-party vendors/partners subject to a security risk assessment before onboarding?", "description": "Third parties often introduce supply-chain risk.", "weight": 1.2, "framework_reference": "NIST-ID.SC-2"},
    {"category": "third_party", "question": "Do contracts with third parties include security and data-protection obligations?", "description": "Contractual controls ensure accountability across the supply chain.", "weight": 1.0, "framework_reference": "NIST-ID.SC-3"},
]