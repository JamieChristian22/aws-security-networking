# Threat Model

| Threat | Example | Control |
|---|---|---|
| lateral movement | dev reaches prod directly | TGW route-table isolation |
| uninspected egress | spoke NAT bypass | default route through inspection |
| command-and-control | malicious outbound domain/IP | Network Firewall policy |
| network reconnaissance | broad east-west reachability | segmentation and SGs |
| data exfiltration | unrestricted outbound traffic | inspection + egress policy |
| blind spots | missing flow evidence | Flow Logs + firewall logs |
