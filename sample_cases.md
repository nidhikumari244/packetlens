# Sample Network Troubleshooting Cases

Use these cases to test the application during demos, interviews, or README screenshots.

## 1. DNS Failure

```text
DNS lookup failed for portal.company.com. Ping to 8.8.8.8 works, but nslookup portal.company.com times out.
```

Expected category: DNS

## 2. HTTP/HTTPS Browser Issue

```text
Cannot access website in browser. Ping works and DNS resolves, but HTTPS page does not load.
```

Expected category: HTTP/HTTPS

## 3. Packet Loss

```text
High packet loss when pinging the default gateway. Some packets timeout and users report slow application access.
```

Expected category: TCP/IP

## 4. Routing Break

```text
traceroute stops after gateway while accessing 10.20.30.40. Other local network devices are reachable.
```

Expected category: Routing

## 5. DHCP Lease Failure

```text
DHCP not assigning IP. Client has 169.254.10.22 address and cannot access internal network resources.
```

Expected category: DHCP

## 6. Firewall Block

```text
Application traffic is blocked on port 443 after a firewall policy update. Ping works but HTTPS connection fails.
```

Expected category: Firewall

## 7. Wi-Fi Instability

```text
Wi-Fi users near the conference room report intermittent disconnects, weak signal, and packet loss.
```

Expected category: Wi-Fi
