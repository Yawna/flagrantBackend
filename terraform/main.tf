resource "aws_iam_role" "iam_for_lambda" {
  name = "flagrant_backend"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "policy" {
  name   = "flagrant_backend_policy"
  policy = templatefile("execution_policy.json",{dynamo_arn = aws_dynamodb_table.flagrant_dynamodb_table.arn})
  role   = aws_iam_role.iam_for_lambda.id
}

resource "aws_lambda_function" "backend" {
  # If the file is not in the current working directory you will need to include a 
  # path.module in the filename.
  filename      = "base.zip"
  function_name = "flagrant_backend"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "lambda_function.main"

  runtime = "python3.9"

  lifecycle {
    ignore_changes = [
      layers, # Usually managed through reviser
      filename,
    ]
  }
}

resource "aws_lambda_function_url" "public_url" {
  function_name      = aws_lambda_function.backend.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["https://www.flagoff.org","https://flagoff.org","http://localhost:3000"]
    allow_methods     = ["*"]
    allow_headers     = ["date", "keep-alive"]
    expose_headers    = ["keep-alive", "date"]
    max_age           = 86400
  }
}

resource "aws_dynamodb_table" "flagrant_dynamodb_table" {
  name           = "flagrant_storage"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "hash_key"
  range_key      = "range_key"

  attribute {
    name = "hash_key"
    type = "S"
  }

  attribute {
    name = "range_key"
    type = "S"
  }
}

