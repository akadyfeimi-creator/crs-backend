"""Central Bank of Nigeria (CBN) Risk-Based Cybersecurity Framework for
Other Financial Institutions (OFIs) — governance, compliance and
Nigeria-specific regulatory controls."""

CBN_CONTROLS = [
    {"category": "compliance", "question": "Has the organization submitted a Cybersecurity Self-Assessment to the CBN as required?", "description": "CBN requires periodic self-assessment submissions from regulated OFIs.", "weight": 1.5, "framework_reference": "CBN-GOV-1"},
    {"category": "compliance", "question": "Does the organization have a designated Chief Information Security Officer (CISO)?", "description": "CBN requires a named individual accountable for cybersecurity.", "weight": 1.2, "framework_reference": "CBN-GOV-2"},
    {"category": "compliance", "question": "Is there board-level oversight of cybersecurity risk (e.g. a board IT/risk committee)?", "description": "Cybersecurity governance should be visible at board level.", "weight": 1.0, "framework_reference": "CBN-GOV-3"},
    {"category": "compliance", "question": "Is an annual cybersecurity awareness training programme conducted for all staff?", "description": "Human error remains a leading cause of security incidents.", "weight": 1.0, "framework_reference": "CBN-GOV-4"},
    {"category": "compliance", "question": "Does the organization maintain a cybersecurity policy reviewed at least annually?", "description": "Policies must be kept current with the evolving threat landscape.", "weight": 1.0, "framework_reference": "CBN-GOV-5"},

    {"category": "authentication", "question": "Does the platform comply with CBN's guidelines on customer authentication for e-payments?", "description": "CBN mandates minimum authentication standards for electronic transactions.", "weight": 1.5, "framework_reference": "CBN-AUTH-1"},
    {"category": "authentication", "question": "Are transaction limits and step-up authentication applied for high-value transfers?", "description": "Higher-risk transactions should require stronger verification.", "weight": 1.0, "framework_reference": "CBN-AUTH-2"},

    {"category": "data_storage", "question": "Is customer BVN/NIN data stored and processed per CBN/NDPR data protection requirements?", "description": "Sensitive identity data requires additional regulatory safeguards.", "weight": 1.2, "framework_reference": "CBN-DATA-1"},
    {"category": "data_storage", "question": "Is customer financial data hosted within jurisdictions permitted by CBN guidelines?", "description": "Data localisation/residency rules may restrict where data can be stored.", "weight": 1.0, "framework_reference": "CBN-DATA-2"},

    {"category": "third_party", "question": "Are payment switch/processor integrations certified against PCI-DSS or equivalent?", "description": "Third-party payment infrastructure must meet recognised security standards.", "weight": 1.2, "framework_reference": "CBN-TP-1"},
    {"category": "third_party", "question": "Does the organization conduct due diligence on fintech/agent-banking partners?", "description": "Partner risk can directly translate into customer-facing incidents.", "weight": 1.0, "framework_reference": "CBN-TP-2"},
]