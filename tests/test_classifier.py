from classifier import classify_issue, fallback_diagnosis


def test_dns_classification_extracts_evidence():
    result = classify_issue("nslookup portal.company.com fails, but ping 8.8.8.8 works")

    assert result["category"] == "DNS"
    assert result["confidence"] == "High"
    assert "8.8.8.8" in result["evidence"]["ip_addresses"]
    assert "portal.company.com" in result["evidence"]["domains"]


def test_dhcp_classification_high_severity():
    result = classify_issue("DHCP not assigning IP and client shows 169.254.10.22")

    assert result["category"] == "DHCP"
    assert result["severity"] == "High"


def test_fallback_contains_industry_fields():
    diagnosis = fallback_diagnosis("traceroute stops after gateway", "Routing", "High")

    assert diagnosis["impact"]
    assert diagnosis["confidence_score"] >= 0
    assert diagnosis["escalation_guidance"]
    assert diagnosis["recommended_commands"]
