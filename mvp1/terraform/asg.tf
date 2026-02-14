# Backend ASG
resource "aws_autoscaling_group" "be_prod" {
  name                = "mine_mvp1_be_asg-prod"
  min_size            = 0
  max_size            = 3
  desired_capacity    = 0
  health_check_type   = "EC2"
  health_check_grace_period = 300
  default_cooldown    = 300

  vpc_zone_identifier = [
    "subnet-043f307b63830fe6e",
    "subnet-0883f6f29b1c0d093"
  ]

  launch_template {
    id      = "lt-082597af524b33fdf"
    version = "$Default"
  }

  # Target Group은 나중에 연결 예정이므로 제외

  tag {
    key                 = "Name"
    value               = "mine_mvp1_be_asg-prod"
    propagate_at_launch = true
  }

  tag {
    key                 = "project"
    value               = "mine"
    propagate_at_launch = true
  }

  tag {
    key                 = "version"
    value               = "mvp2"
    propagate_at_launch = true
  }

  tag {
    key                 = "server"
    value               = "prod"
    propagate_at_launch = true
  }
}

# Frontend ASG
resource "aws_autoscaling_group" "fe_prod" {
  name                = "mine_mvp1_fe_asg-prod"
  min_size            = 0
  max_size            = 3
  desired_capacity    = 0
  health_check_type   = "EC2"
  health_check_grace_period = 300
  default_cooldown    = 300

  vpc_zone_identifier = [
    "subnet-043f307b63830fe6e",
    "subnet-0883f6f29b1c0d093"
  ]

  launch_template {
    id      = data.aws_launch_template.fe.id
    version = "$Default"
  }

  # Target Group은 나중에 연결 예정이므로 제외

  tag {
    key                 = "Name"
    value               = "mine_mvp1_fe_asg-prod"
    propagate_at_launch = true
  }

  tag {
    key                 = "project"
    value               = "mine"
    propagate_at_launch = true
  }

  tag {
    key                 = "version"
    value               = "mvp2"
    propagate_at_launch = true
  }

  tag {
    key                 = "server"
    value               = "prod"
    propagate_at_launch = true
  }
}

# Data source to get FE launch template
data "aws_launch_template" "fe" {
  name = "mine-mvp1-asg-template-fe"
}
