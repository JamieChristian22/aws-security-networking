resource "aws_cloudwatch_log_group" "nfw" {
  name              = var.log_group_name
  retention_in_days = var.retention_days
  tags              = var.tags
}

resource "aws_networkfirewall_rule_group" "stateful" {
  name     = "${var.name}-stateful"
  capacity = 100
  type     = "STATEFUL"
  rule_group {
    rules_source {
      stateful_rules = [
        # Allow DNS to VPC resolver (UDP 53) if you run a resolver in the hub; otherwise remove.
        {
          action = "PASS"
          header = {
            protocol         = "UDP"
            source           = "ANY"
            source_port      = "ANY"
            direction        = "ANY"
            destination      = "ANY"
            destination_port = "53"
          }
          rule_options = [{ keyword = "sid:1" }]
        },
        # Allow HTTPS outbound
        {
          action = "PASS"
          header = {
            protocol         = "TCP"
            source           = "ANY"
            source_port      = "ANY"
            direction        = "ANY"
            destination      = "ANY"
            destination_port = "443"
          }
          rule_options = [{ keyword = "sid:2" }]
        },
        # Deny everything else (simple baseline)
        {
          action = "DROP"
          header = {
            protocol         = "IP"
            source           = "ANY"
            source_port      = "ANY"
            direction        = "ANY"
            destination      = "ANY"
            destination_port = "ANY"
          }
          rule_options = [{ keyword = "sid:999" }]
        }
      ]
    }
  }
  tags = merge(var.tags, { Name = "${var.name}-stateful" })
}

resource "aws_networkfirewall_firewall_policy" "this" {
  name = "${var.name}-policy"
  firewall_policy {
    stateful_rule_group_reference {
      resource_arn = aws_networkfirewall_rule_group.stateful.arn
    }
    stateful_engine_options {
      rule_order = "STRICT_ORDER"
    }
  }
  tags = merge(var.tags, { Name = "${var.name}-policy" })
}

resource "aws_networkfirewall_firewall" "this" {
  name                = var.name
  firewall_policy_arn = aws_networkfirewall_firewall_policy.this.arn
  vpc_id              = var.vpc_id

  dynamic "subnet_mapping" {
    for_each = var.firewall_subnet_ids
    content {
      subnet_id = subnet_mapping.value
    }
  }

  tags = merge(var.tags, { Name = var.name })
}

resource "aws_networkfirewall_logging_configuration" "this" {
  firewall_arn = aws_networkfirewall_firewall.this.arn
  logging_configuration {
    log_destination_config {
      log_destination = { logGroup = aws_cloudwatch_log_group.nfw.name }
      log_destination_type = "CloudWatchLogs"
      log_type = "FLOW"
    }
    log_destination_config {
      log_destination = { logGroup = aws_cloudwatch_log_group.nfw.name }
      log_destination_type = "CloudWatchLogs"
      log_type = "ALERT"
    }
  }
}
