# Validation Checklist

1. Dev default route points to TGW.
2. Prod default route points to TGW.
3. Direct Dev→Prod route is absent.
4. Spoke internet traffic traverses inspection.
5. Allowed HTTPS egress succeeds.
6. Prohibited test port is blocked.
7. Firewall log records the test flow.
8. VPC Flow Logs record accepted/rejected traffic.
9. Removing the inspection route causes expected loss of outbound connectivity rather than bypass.
10. Route restoration returns the environment to normal.

Record source/destination, expected result, actual result, log evidence, and timestamp for every live test.
