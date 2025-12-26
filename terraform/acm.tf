# Backend Certificate (ALB - eu-central-1)
resource "aws_acm_certificate" "backend_cert" {
  domain_name       = "${var.backend_subdomain}.${var.domain_name}"
  validation_method = "DNS"

  tags = {
    Name = "${var.project_name}-${var.environment}-backend-cert"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Frontend Certificate (CloudFront - us-east-1)
resource "aws_acm_certificate" "frontend_cert" {
  provider          = aws.us_east_1
  domain_name       = "${var.subdomain}.${var.domain_name}"
  validation_method = "DNS"

  tags = {
    Name = "${var.project_name}-${var.environment}-frontend-cert"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# DNS Validation Record for Backend
resource "aws_route53_record" "backend_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.backend_cert.domain_validation_options : dvo.domain_name => dvo
  }

  allow_overwrite = true
  name            = each.value.resource_record_name
  records         = [each.value.resource_record_value]
  ttl             = 60
  type            = each.value.resource_record_type
  zone_id         = data.aws_route53_zone.main.zone_id
}

# DNS Validation Record for Frontend
resource "aws_route53_record" "frontend_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.frontend_cert.domain_validation_options : dvo.domain_name => dvo
  }

  allow_overwrite = true
  name            = each.value.resource_record_name
  records         = [each.value.resource_record_value]
  ttl             = 60
  type            = each.value.resource_record_type
  zone_id         = data.aws_route53_zone.main.zone_id
}

# Backend Certificate Validation
resource "aws_acm_certificate_validation" "backend_cert" {
  certificate_arn         = aws_acm_certificate.backend_cert.arn
  validation_record_fqdns = [for record in aws_route53_record.backend_cert_validation : record.fqdn]
}

# Frontend Certificate Validation
resource "aws_acm_certificate_validation" "frontend_cert" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.frontend_cert.arn
  validation_record_fqdns = [for record in aws_route53_record.frontend_cert_validation : record.fqdn]
}
