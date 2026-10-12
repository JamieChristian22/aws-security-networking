# Implemented detection catalog

| ID | Signal | Match | Action | Test |
|---|---|---|---|---|
| DET-01 | Security Hub imported finding | Source/detail-type only | Archive and normalize/index | Direct fixture for handler; real sample event for bus |
| DET-02 | Security Hub imported finding | HIGH/CRITICAL + ACTIVE + NEW | SNS | Real sandbox sample with matching fields |
| DET-03 | Lambda errors | One or more in 5 minutes | CloudWatch alarm → SNS | Controlled dependency failure in sandbox |
| DET-04 | Either failure queue has visible messages | Maximum >= 1 in 5 minutes | CloudWatch alarm → SNS | Controlled delivery/processing failure |
| DET-05 | OpenSearch cluster red | Maximum >= 1 in 5 minutes | CloudWatch alarm → SNS | Review configuration; do not deliberately damage a shared cluster |

Tune DET-02 by studying actual false positives, not by suppressing all noisy products. Record finding category, business reason, owner, expiration and a negative fixture for every suppression. Other desired rules, such as root activity or broad security-group changes, are explicit future additions and must not be listed as implemented detections.
