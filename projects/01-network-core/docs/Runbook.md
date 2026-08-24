# Network Security Operations Runbook

## Spoke Cannot Reach Internet
Check TGW attachment → TGW route → inspection subnet route → firewall endpoint → NAT route → IGW.

## Unexpected Cross-Spoke Reachability
Review TGW route-table association/propagation first. Remove unintended route propagation, validate with Reachability Analyzer, and document the change.

## Firewall Block Investigation
Capture source/destination/port, check Network Firewall alert/flow logs, validate rule order and stateful policy, then determine whether the traffic is authorized.

## SEV-1 Network Security Event
Preserve flow/firewall logs, isolate affected route/SG where safe, notify security owner, document timeline, and avoid deleting evidence during containment.
