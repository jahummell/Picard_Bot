provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "picard" {
  ami           = "ami-0c55b159cbfafe1f0" # Amazon Linux 2 AMI
  instance_type = "t3.micro"

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y docker
              service docker start
              docker run -d -p 80:80 slack-bot
              EOF

  tags = {
    Name = "picard-instance"
  }
}
