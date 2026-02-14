# Application Load Balancer
resource "aws_lb" "prod" {
  name               = "mine-mvp1-alb-internet-prod"
  internal           = false
  load_balancer_type = "application"
  security_groups    = ["sg-01af02cfe591ee9d9"]

  subnets = [
    "subnet-068659d5a55025bcb",  # ap-northeast-2d
    "subnet-0bf72b3a117401c47"   # ap-northeast-2c
  ]

  enable_deletion_protection = false
  enable_http2              = true
  idle_timeout              = 60

  tags = {
    Name    = "mine-mvp1-alb-internet-prod"
    project = "mine"
    version = "mvp2"
    server  = "prod"
  }
}

# HTTP Listener (80) - Redirect to HTTPS
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.prod.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# HTTPS Listener (443)
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.prod.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-Res-PQ-2025-09"
  certificate_arn   = "arn:aws:acm:ap-northeast-2:219268921033:certificate/b646df55-259b-4122-8218-30e64f0850e6"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.be_prod.arn
  }
}

# Listener Rule: /server/* -> Backend
# Note: URL rewrite transform needs to be added manually via AWS CLI or Console
resource "aws_lb_listener_rule" "backend" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 1

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.be_prod.arn
  }

  condition {
    path_pattern {
      values = ["/server/*"]
    }
  }
}

# Listener Rule: /* -> Frontend
resource "aws_lb_listener_rule" "frontend" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 3

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fe_prod.arn
  }

  condition {
    path_pattern {
      values = ["/*"]
    }
  }
}
