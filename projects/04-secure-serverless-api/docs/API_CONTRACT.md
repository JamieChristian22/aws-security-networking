# API contract

## Request

`POST /sandbox/requests`

Headers:

- `Authorization`: a valid Cognito **ID token** for this user pool/app client. The method does not configure OAuth scopes for access-token authorization.
- `Content-Type: application/json`
- `Idempotency-Key`: 16–64 ASCII letters, digits, underscores or hyphens; generate a new random key for a new logical submission.

```json
{"customer_id":"synthetic-customer-01","action":"create"}
```

The customer ID must be a string of 1–64 letters/digits/underscores/hyphens. Action is exactly one of `create`, `update`, `review`. No additional fields are allowed. Decoded body limit is 4096 bytes. Base64 API Gateway bodies are decoded with validation. User identity is taken from verified authorizer claims, not caller-supplied JSON.

## Responses

| Status | Meaning | Client behavior |
|---|---|---|
| 201 | New record created | Store returned request_id |
| 200 | Identical authenticated replay | Treat as already completed |
| 400 | Invalid body/header/type/action | Correct request; do not blindly retry |
| 401/403 | Missing/invalid authorization or gateway/WAF rejection | Reauthenticate or investigate; distinguish gateway from handler |
| 409 | Same subject/key used for changed content | Use original payload or a new key for a genuinely new operation |
| 429 | Gateway throttling | Back off with jitter |
| 503 | Storage dependency failure | Retry with the same key after backoff |

The WAF rate rule uses block, which ordinarily produces a 403; API Gateway throttling ordinarily produces 429. They are distinct behaviors and must not be conflated in the evidence ledger.

A 201/200 body contains `request_id` and `replayed`. Errors return a generic error string without stack traces. The handler does not log the bearer token, body or idempotency key.

## Limits and lifecycle

Stored request/idempotency records have no automatic expiry in this lab. Select retention requirements before using real personal data. The `customer_id` is a label, not a validated business identity. Authentication and per-subject record isolation do not establish consent or authorization to operate on an external customer system.
