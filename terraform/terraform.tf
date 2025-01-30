provider "aws"{
  access_key = var.ACCESS_KEY
  secret_key = var.SECRET_KEY
  region = "eu-west-2"
}

# TASK DEFINITION
data "aws_iam_role" "execution_role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_ecs_task_definition" "c15-robert-howarth-food_trucks" {
  family = "c15-robert-howarth-food_trucks"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn = data.aws_iam_role.execution_role.arn
  container_definitions = jsonencode([
    {
      name      = "c15-robert-howarth"
      image     = var.PIPELINE_IMAGE_URI
      cpu       = 256
      memory    = 512
      essential = true
      launch_type = "FARGATE" 
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        }
      ]
      environment = [
        ### DATABASE
        {
        name="DB_HOST"
        value=var.DB_HOST
        },
        {
        name="DB_PORT"
        value=var.DB_PORT
        },
        {
        name="DB_NAME"
        value=var.DB_NAME
        },
        {
        name="DB_USER"
        value=var.DB_USER
        },
        {
        name="DB_PASSWORD"
        value=var.DB_PASSWORD
        },
        ### AWS
        {
        name="ACCESS_KEY"
        value=var.ACCESS_KEY
        },
        {
        name="SECRET_KEY"
        value=var.SECRET_KEY
        },
        {
        name="BUCKET"
        value=var.BUCKET
        },
        {
        name="FOLDER"
        value=var.FOLDER
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        "options": {
          awslogs-group="ecs/c15-robert-howarth-food_trucks"
          awslogs-stream-prefix="ecs"
          awslogs-create-group="true"
          awslogs-region="eu-west-2"
        }
      }
    }  ])
}

## LAMBDA

## ECR - Select the repository and the image wanted

data "aws_ecr_repository" "lambda-image-repo" {
  name = "c15-rob-report"
}

data "aws_ecr_image" "lambda-image-version" {
  repository_name = data.aws_ecr_repository.lambda-image-repo.name
  image_tag       = "latest"
}


## Permissions etc. for the Lambda

# Trust doc
data "aws_iam_policy_document" "lambda-role-trust-policy-doc" {
    statement {
      effect = "Allow"
      principals {
        type = "Service"
        identifiers = [ "lambda.amazonaws.com" ]
      }
      actions = [
        "sts:AssumeRole"
      ]
    }
}

# Permissions doc
data "aws_iam_policy_document" "lambda-role-permissions-policy-doc" {
    statement {
      effect = "Allow"
      actions = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
      resources = [ "arn:aws:logs:eu-west-2:129033205317:*" ]
    }
}

# Role
resource "aws_iam_role" "lambda-role" {
    name = "c15-rob-report-lambda-role"
    assume_role_policy = data.aws_iam_policy_document.lambda-role-trust-policy-doc.json
}

# Permissions policy
resource "aws_iam_policy" "lambda-role-permissions-policy" {
    name = "c15-rob-report-lambda-role-permission"
    policy = data.aws_iam_policy_document.lambda-role-permissions-policy-doc.json
}

# Connect the policy to the role
resource "aws_iam_role_policy_attachment" "lambda-role-policy-connection" {
  role = aws_iam_role.lambda-role.name
  policy_arn = aws_iam_policy.lambda-role-permissions-policy.arn
}


## Lambda - create the lambda resource

resource "aws_lambda_function" "simple-email-lambda" {
  function_name = "c15-rob-report-lambda-function"
  role = aws_iam_role.lambda-role.arn
  package_type = "Image"
  image_uri = data.aws_ecr_image.lambda-image-version.image_uri
  environment {
    variables = {
        DB_HOST = var.DB_HOST
        DB_PORT = var.DB_PORT
        DB_NAME = var.DB_NAME
        DB_USER = var.DB_USER
        DB_PASSWORD = var.DB_PASSWORD

    }
  }
}