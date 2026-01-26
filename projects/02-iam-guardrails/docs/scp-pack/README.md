# SCP Pack (AWS Organizations)

These SCPs are designed for org-level governance. They are provided as JSON policies.

Policies:
- `deny-leave-org.json` – prevents accounts from leaving the org
- `deny-disable-cloudtrail.json` – prevents disabling CloudTrail
- `deny-public-s3.json` – blocks public S3 buckets
- `deny-iam-admin-attach.json` – blocks attaching Admin policies outside break-glass process

Apply via AWS Organizations at root/OUs.
