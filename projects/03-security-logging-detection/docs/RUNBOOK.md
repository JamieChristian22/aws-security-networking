# Detection operations and replay runbook

## Missing finding

Begin with a known finding ID and update time. Confirm the original exists in Security Hub and matches the EventBridge rule's source/detail-type. For alerting, confirm HIGH/CRITICAL, ACTIVE and NEW fields. A resolved or suppressed finding is intentionally excluded from the notification rule.

Check EventBridge invocations/failed invocations, Lambda invocation/error metrics and the delivery queue. If Lambda ran, inspect structured logs and the processing queue. Locate the S3 version using the normalized timestamp/hash derivation; archive success with index failure means evidence is retained but search freshness is degraded.

## Processing queue backlog

1. Record queue URL, oldest message age, count and affected time window. Do not purge.
2. Receive a small sample with a nonzero visibility timeout and preserve its invocation record privately.
3. Distinguish validation failure, S3 authorization, private DNS/connectivity, SigV4 error, search authorization and search capacity.
4. Repair the root cause through a reviewed configuration/code change. Test the original event with one synchronous invocation.
5. For a Lambda failure destination, extract `requestPayload` as the replay event. EventBridge DLQ messages have a different envelope; inspect before replaying.
6. Replay a limited batch. Verify archive/index success for each finding version and alarm recovery.
7. Delete only successfully processed queue messages using their current receipt handles. Keep failed messages and document the reason.

```bash
aws sqs get-queue-attributes --queue-url "$QUEUE_URL" --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible
aws lambda get-function-event-invoke-config --function-name "$INGEST_FUNCTION"
aws logs tail "/aws/lambda/$INGEST_FUNCTION" --since 30m
```

## Search index outage or authorization error

Check the domain control-plane status and cluster metrics. Private DNS must resolve within the VPC; a public laptop timeout is expected and does not diagnose a service outage. HTTP 403 with a working connection suggests principal/path/signature scope; timeout suggests route/DNS/SG or service health. Do not turn off TLS verification or expose the domain to make the error disappear.

Restore the approved network/policy or service configuration, then replay retained S3 finding versions. Index recreation and scale changes require a plan and capacity/cost review. The S3 archive is the recovery source, but backup existence does not prove a successful restore.

## Alert not received

Check the exact finding fields, EventBridge target errors, SNS publish permission and subscription confirmation. Manually publishing to SNS only proves the last step, not the EventBridge match. Test the full event path before closure. Alarm missing-data treatment is notBreaching; absence of alerts is not evidence of healthy telemetry.

## Retention review

Weekly during active use, inspect OpenSearch storage/shard growth and S3 lifecycle. Add a reviewed index retention policy before long-lived operation. Review alert volume and false positives before changing severity criteria; preserve the rationale and regression fixture for each tuning decision.
