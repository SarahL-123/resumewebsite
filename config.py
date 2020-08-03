import os


S3_BUCKET                 = os.environ.get("S3_BUCKET")
S3_KEY                    = os.environ.get("S3_ACCESS_KEY")
S3_SECRET                 = os.environ.get("S3_SECRET_ACCESS_KEY")
S3_REGION                 = os.environ.get("S3_REGION")


S3_LOCATION               = 'http://{}.s3{}.amazonaws.com/'.format(S3_BUCKET, S3_REGION)

# SECRET_KEY                = os.urandom(32)
DEBUG                     = True
PORT                      = 5000