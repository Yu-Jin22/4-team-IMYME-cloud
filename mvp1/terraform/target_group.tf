resource "aws_lb_target_group" "be_prod" {
  name     = "mine-mvp1-be-tg-prod"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = "vpc-08b6e4bef859b5897"

  target_type = "instance"

  health_check {
    enabled             = true
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
  }

  deregistration_delay = 30

  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400
    enabled         = false
  }

  tags = {
    Name    = "mine-mvp1-be-tg-prod"
    project = "mine"
    version = "mvp2"
    server  = "prod"
  }
}
