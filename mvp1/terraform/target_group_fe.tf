resource "aws_lb_target_group" "fe_prod" {
  name     = "mine-mvp1-fe-tg-prod"
  port     = 3000
  protocol = "HTTP"
  vpc_id   = "vpc-08b6e4bef859b5897"

  target_type = "instance"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 100
    path                = "/api/health"
    protocol            = "HTTP"
    matcher             = "200"
  }

  deregistration_delay = 300

  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400
    enabled         = false
  }

  tags = {
    Name    = "mine-mvp1-fe-tg-prod"
    project = "mine"
    version = "mvp2"
    server  = "prod"
  }
}
