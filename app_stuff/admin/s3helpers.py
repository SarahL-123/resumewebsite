import boto3, botocore

from app_stuff import app

S3_BUCKET = app.config["S3_BUCKET"]
S3_KEY = app.config["S3_KEY"]
S3_SECRET = app.config["S3_SECRET"]
S3_LOCATION = app.config["S3_LOCATION"]


s3 = boto3.client("s3", aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)

# I got the code from here:
# https://www.zabana.me/notes/flask-tutorial-upload-files-amazon-s3
def upload_file_to_s3(file, bucket_name=S3_BUCKET, acl="public-read"):

    print("uploading " + str(file.filename) + " to " + str(S3_LOCATION))
    print(S3_KEY)
    print(S3_SECRET)

    try:

        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={"ACL": acl, "ContentType": file.content_type},
        )

        print("uploaded")
    except Exception as e:
        # tbh I have no idea what errors could appear
        print("Something Happened: ", e)
        return e

    return "{}{}".format(S3_LOCATION, file.filename)


def delete_file_from_s3(filename, bucket_name=S3_BUCKET):

    try:
        s3.delete_object(Bucket=bucket_name, Key=filename)
        return 0
    except Exception as e:
        print("Error in deleting: ", e)
        return 1
