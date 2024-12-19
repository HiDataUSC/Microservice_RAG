import os

# Environment variables for the indexing microservice
# AWS S3 parameters
AWS_S3_BUCKET = 'dev-bucket-upload'

# AWS RDS parameters
AWS_RDS = {
    'host': 'database-dev-test.cdi8oo0ia8yh.us-east-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'admin123456',
    'database': 'database-dev-test'
}