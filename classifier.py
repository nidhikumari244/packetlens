"""Rule-based network issue classification and fallback diagnosis helpers."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Dict, List


@dataclass(frozen=True)
class CategoryRule:
    category: str
    keywords: tuple[str, ...]
    default_severity: str


CATEGORY_RULES: tuple[CategoryRule, ...] = (
    CategoryRule(
        "DNS",
        ("dns", "domain", "nslookup", "dig", "name resolution", "lookup failed", "host not found"),
        "Medium",
    ),
    CategoryRule(
        "DHCP",
        ("dhcp", "ip not assigned", "apipa", "169.254", "lease", "no ip address", "not assigning ip"),
        "High",
    ),
    CategoryRule(
        "Routing",
        ("traceroute", "tracert", "gateway", "route", "next hop", "hop", "ttl", "routing"),
        "High",
    ),
    CategoryRule(
        "Firewall",
        ("blocked", "firewall", "acl", "access-list", "port closed", "denied", "filtered"),
        "High",
    ),
    CategoryRule(
        "HTTP/HTTPS",
        ("website", "browser", "http", "https", "ssl", "tls", "certificate", "web page", "url"),
        "Medium",
    ),
    CategoryRule(
        "Wi-Fi",
        ("wifi", "wi-fi", "wireless", "ssid", "signal", "roaming", "interference", "access point"),
        "Medium",
    ),
    CategoryRule(
        "TCP/IP",
        ("ping", "packet loss", "latency", "icmp", "tcp", "ip", "timeout", "unreachable"),
        "Medium",
    ),
)


HIGH_SEVERITY_TERMS = (
    "down",
    "outage",
    "cannot connect",
    "no internet",
    "100% packet loss",
    "production",
    "critical",
)

LOW_SEVERITY_TERMS = ("slow sometimes", "intermittent", "minor", "warning")


def classify_issue(user_input: str) -> Dict[str, object]:
    """Classify a network issue using transparent keyword rules."""
    normalized = user_input.lower()
    evidence = extract_evidence(user_input)
    matches: List[dict] = []

    for rule in CATEGORY_RULES:
        matched_keywords = [keyword for keyword in rule.keywords if keyword in normalized]
        if rule.category == "DNS" and evidence["domains"]:
            matched_keywords.append("domain pattern")
        if matched_keywords:
            matches.append(
                {
                    "category": rule.category,
                    "score": len(matched_keywords),
                    "keywords": matched_keywords,
                    "default_severity": rule.default_severity,
                }
            )

    if not matches:
        return {
            "category": "Unknown",
            "severity": infer_severity(normalized, "Low"),
            "matched_keywords": [],
            "confidence": "Low",
            "confidence_score": 35,
            "evidence": evidence,
        }

    matches.sort(key=lambda item: item["score"], reverse=True)
    best = matches[0]
    confidence = "High" if best["score"] >= 2 else "Medium"
    confidence_score = min(95, 55 + int(best["score"]) * 15)

    return {
        "category": best["category"],
        "severity": infer_severity(normalized, str(best["default_severity"])),
        "matched_keywords": best["keywords"],
        "confidence": confidence,
        "confidence_score": confidence_score,
        "evidence": evidence,
    }


def infer_severity(normalized_input: str, default: str) -> str:
    if any(term in normalized_input for term in HIGH_SEVERITY_TERMS):
        return "High"
    if any(term in normalized_input for term in LOW_SEVERITY_TERMS):
        return "Low"
    return default


def extract_evidence(user_input: str) -> Dict[str, object]:
    """Extract simple technical signals from the text for auditability."""
    ip_addresses = sorted(set(re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", user_input)))
    domains = sorted(
        set(
            re.findall(
                r"\b(?:[a-zA-Z0-9-]+\.)+(?:com|net|org|in|io|co|local|corp|edu|gov)\b",
                user_input,
            )
        )
    )
    command_hits = []
    for command in ("ping", "tracert", "traceroute", "nslookup", "dig", "curl", "ipconfig", "netstat"):
        if command in user_input.lower():
            command_hits.append(command)

    return {
        "ip_addresses": ip_addresses,
        "domains": domains,
        "commands_detected": command_hits,
        "length": len(user_input.strip()),
    }


def build_impact_summary(category: str, severity: str) -> str:
    if severity == "High":
        return f"{category} issue may affect user productivity or service availability and should be triaged urgently."
    if severity == "Medium":
        return f"{category} issue may affect a subset of users or applications and needs structured validation."
    return f"{category} issue appears limited, but should be documented and monitored for recurrence."


def escalation_guidance(category: str, severity: str) -> List[str]:
    if severity == "High":
        return [
            "Escalate to network operations if multiple users or production services are impacted.",
            "Capture command outputs, timestamps, affected VLAN/site, and recent change details.",
            "Open a priority incident if the issue is reproducible and business-critical.",
        ]
    if category in {"Firewall", "Routing", "DHCP"}:
        return [
            "Escalate if device-level configuration access is required.",
            "Attach traceroute, IP configuration, and policy or scope evidence.",
        ]
    return [
        "Escalate if troubleshooting steps do not isolate the issue.",
        "Include screenshots or command output when handing off.",
    ]


def fallback_diagnosis(user_input: str, category: str, severity: str) -> Dict[str, object]:
    """Return a deterministic diagnosis when AI is unavailable."""
    playbooks = {
        "DNS": {
            "root_cause": "DNS resolution is likely failing or returning an incorrect address.",
            "explanation": "The device may have basic connectivity, but it cannot translate a domain name into the correct IP address.",
            "steps": [
                "Verify that the client has a valid DNS server configured.",
                "Test name resolution using nslookup or dig.",
                "Compare results with a public resolver such as 8.8.8.8 or 1.1.1.1.",
                "Flush the local DNS cache and retry the website.",
                "Check whether the issue affects one domain or multiple domains.",
            ],
            "commands": ["nslookup example.com", "ipconfig /all", "ipconfig /flushdns", "ping 8.8.8.8"],
            "prevention": ["Use redundant DNS servers.", "Monitor DNS resolver availability.", "Document DNS changes."],
        },
        "TCP/IP": {
            "root_cause": "There may be packet loss, IP reachability failure, or unstable network connectivity.",
            "explanation": "ICMP or TCP traffic is not consistently reaching the destination, which can affect applications.",
            "steps": [
                "Ping the default gateway to confirm local network reachability.",
                "Ping an external IP address to check internet reachability.",
                "Check packet loss percentage and latency variation.",
                "Inspect interface status, cable, Wi-Fi signal, or ISP link quality.",
                "Use traceroute to identify where packets start dropping.",
            ],
            "commands": ["ping <gateway-ip>", "ping 8.8.8.8", "tracert 8.8.8.8", "netstat -s"],
            "prevention": ["Monitor latency and loss.", "Use reliable cabling.", "Track interface errors."],
        },
        "DHCP": {
            "root_cause": "The client is probably not receiving a valid IP lease from the DHCP server.",
            "explanation": "Without a DHCP lease, the device may self-assign an address or fail to join the network.",
            "steps": [
                "Check whether the client has an APIPA address such as 169.254.x.x.",
                "Renew the DHCP lease.",
                "Verify DHCP server availability and scope exhaustion.",
                "Confirm VLAN and relay agent configuration.",
                "Check switch port status and access VLAN assignment.",
            ],
            "commands": ["ipconfig /all", "ipconfig /release", "ipconfig /renew", "show ip dhcp binding"],
            "prevention": ["Monitor DHCP scope utilization.", "Use DHCP failover.", "Document VLAN-to-scope mapping."],
        },
        "Routing": {
            "root_cause": "Traffic is likely stopping because of a missing, incorrect, or unreachable route.",
            "explanation": "The source can reach part of the path, but packets do not have a valid next hop to the destination.",
            "steps": [
                "Run traceroute to identify the last responding hop.",
                "Verify the default gateway on the client.",
                "Check route tables on routers or layer-3 switches.",
                "Confirm that return routes exist.",
                "Review recent routing, VLAN, or ACL changes.",
            ],
            "commands": ["tracert <destination>", "route print", "ping <gateway-ip>", "show ip route"],
            "prevention": ["Use route monitoring.", "Maintain change logs.", "Validate return paths after network changes."],
        },
        "Firewall": {
            "root_cause": "A firewall, ACL, or security policy may be blocking required traffic.",
            "explanation": "Connectivity may exist at the network layer, but specific ports or protocols are being denied.",
            "steps": [
                "Identify the application port and protocol.",
                "Test port reachability from the client.",
                "Review local firewall and network firewall policies.",
                "Check logs for denied traffic.",
                "Temporarily test with a controlled allow rule if permitted.",
            ],
            "commands": ["Test-NetConnection <host> -Port 443", "netsh advfirewall show allprofiles", "telnet <host> 443"],
            "prevention": ["Maintain firewall rule documentation.", "Review deny logs.", "Use least-privilege allow rules."],
        },
        "HTTP/HTTPS": {
            "root_cause": "The issue may be at the web, TLS, proxy, or application layer.",
            "explanation": "The network may be reachable, but browser traffic can fail due to DNS, certificate, proxy, or server issues.",
            "steps": [
                "Verify DNS resolution for the website.",
                "Test the website from another browser or network.",
                "Check TLS certificate validity and system time.",
                "Inspect proxy settings.",
                "Use curl to view HTTP status and connection errors.",
            ],
            "commands": ["curl -I https://example.com", "nslookup example.com", "Test-NetConnection example.com -Port 443"],
            "prevention": ["Monitor certificates.", "Standardize proxy settings.", "Use uptime checks for critical websites."],
        },
        "Wi-Fi": {
            "root_cause": "Wireless signal quality, interference, or authentication may be affecting connectivity.",
            "explanation": "Wi-Fi issues can cause intermittent packet loss, slow speed, or failure to join the network.",
            "steps": [
                "Check signal strength and distance from the access point.",
                "Verify SSID and authentication settings.",
                "Test with another device on the same Wi-Fi.",
                "Look for channel interference or overloaded access points.",
                "Reconnect or reconfigure the wireless profile.",
            ],
            "commands": ["netsh wlan show interfaces", "netsh wlan show profiles", "ping <gateway-ip>"],
            "prevention": ["Plan AP placement.", "Monitor channel utilization.", "Use secure and consistent WLAN settings."],
        },
    }

    result = playbooks.get(
        category,
        {
            "root_cause": "The exact protocol layer is unclear from the current information.",
            "explanation": "More details are needed to isolate whether the issue is DNS, routing, firewall, DHCP, or application-related.",
            "steps": [
                "Confirm whether the issue affects one device or many devices.",
                "Check IP address, gateway, and DNS configuration.",
                "Test ping to the gateway and a public IP.",
                "Run traceroute to the destination.",
                "Collect error messages from the affected application.",
            ],
            "commands": ["ipconfig /all", "ping <gateway-ip>", "ping 8.8.8.8", "tracert <destination>", "nslookup <domain>"],
            "prevention": ["Keep network diagrams updated.", "Document recurring incidents.", "Monitor key network services."],
        },
    )

    return {
        "root_cause": result["root_cause"],
        "explanation": result["explanation"],
        "category": category,
        "severity": severity,
        "impact": build_impact_summary(category, severity),
        "confidence": "Rule-based",
        "confidence_score": 70 if category != "Unknown" else 35,
        "evidence": extract_evidence(user_input),
        "troubleshooting_steps": result["steps"],
        "recommended_commands": result["commands"],
        "prevention_tips": result["prevention"],
        "escalation_guidance": escalation_guidance(category, severity),
        "source": "Rule-based fallback",
    }
