# Failure Mode Analysis

| Failure | Expected Effect | Recovery |
|---|---|---|
| Firewall endpoint unavailable | inspected egress impaired | verify AZ endpoint/route and restore |
| TGW attachment issue | spoke isolation | repair attachment/association |
| NAT failure | outbound internet loss | replace NAT / route |
| bad route propagation | possible unintended reachability | remove propagation and validate |
| logging failure | reduced investigation visibility | restore log destination/permissions |
