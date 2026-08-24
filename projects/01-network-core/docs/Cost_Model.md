# Cost Model

Primary cost drivers are Transit Gateway attachments/data processing, Network Firewall endpoint hours/data processing, NAT Gateway hours/data processing, and CloudWatch log ingestion.

Architecture decision rule: preserve required segmentation and inspection; optimize data paths and log retention only after traffic patterns are measured.
