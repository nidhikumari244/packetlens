from report_generator import generate_report


def test_report_contains_incident_sections():
    report = generate_report(
        "DNS lookup failed",
        {
            "category": "DNS",
            "severity": "Medium",
            "confidence_score": 80,
            "impact": "Users cannot reach internal portal.",
            "root_cause": "DNS resolver timeout.",
            "explanation": "Name resolution is failing.",
            "troubleshooting_steps": ["Check DNS server"],
            "recommended_commands": ["nslookup portal.company.com"],
            "prevention_tips": ["Use redundant resolvers"],
            "escalation_guidance": ["Escalate with nslookup output"],
            "evidence": {"domains": ["portal.company.com"], "ip_addresses": [], "commands_detected": ["nslookup"]},
        },
        "2026-06-05 14:00:00",
    )

    assert "Incident Report" in report
    assert "Business Impact" in report
    assert "Extracted Evidence" in report
    assert "Escalation Guidance" in report
