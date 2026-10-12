# Detection pipeline architecture

## Data paths

CloudTrail management events go to private versioned S3 and CloudWatch Logs. GuardDuty and Security Hub are account/region services; enablement ownership is explicit. Security Hub imported findings enter two EventBridge rules: all findings go to ingestion, while active new HIGH/CRITICAL findings go to SNS.

The ingestion Lambda runs in private subnets without a NAT gateway. It reaches S3 through a scoped gateway endpoint and OpenSearch through private VPC interfaces. Its role signs each document PUT with SigV4. The OpenSearch security group permits HTTPS from the ingestion security group; the domain policy permits only that role's finding-document writes. There is no public dashboard or broadly authorized analyst reader.

## Delivery semantics

| Stage | Success behavior | Failure behavior |
|---|---|---|
| EventBridge → Lambda | Service accepts asynchronous invocation | Bounded delivery retry and delivery DLQ |
| Lambda normalization | Required identity/timestamp validated | Exception; asynchronous processing retry |
| Lambda → S3 | Original finding version archived | Exception; no index call for that finding |
| Lambda → OpenSearch | Normalized document written | Exception; archived evidence remains |
| Lambda retry exhausted | Not applicable | Failure destination contains invocation record in processing DLQ |

The two queues mean different things. EventBridge's delivery DLQ indicates inability to hand off the event; Lambda's processing destination indicates failure after acceptance. They have 14-day retention and backlog alarms. Operators must act before retention expires.

## Record model

Normalized fields include finding identity, product ARN, account, region, normalized UTC update time, severity, title, record state and resource list. The full original record remains in private S3. The document ID hashes product ARN + finding ID + normalized update timestamp. A replay of the same version has the same key; a later version has a different key. This protects against older events overwriting newer ones.

Indices are monthly (`securityhub-YYYY.MM`). A latest-state query must group versions by finding identity and choose the greatest update time. The archive uses a 365-day current-object lifecycle and 90-day noncurrent-version expiry. There is no automatic OpenSearch retention job in this release; storage lifecycle is an explicit operational gap.

## Detection scope

The deployed alert rule handles Security Hub severity/state. Root activity and security-service shutdown detection are not implemented as additional custom detection rules in this stack. CloudTrail is available for investigation; custom rules belong in a separately tested catalog. Default Security Hub standards are disabled because a complete Config recorder/rule prerequisite design is outside this independent lab.

The root is single-account. Delegated administrators, cross-account event buses, organization trails and cross-region aggregation are production extensions. Two small search nodes across two AZs demonstrate placement but do not constitute a measured availability guarantee.
