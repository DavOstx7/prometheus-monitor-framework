from pydantic import BaseModel

class Config(BaseModel):
    """
    A configuration model representing the S3 bucket details.

    Attributes:
        bucket_name (str): The name of the S3 bucket.
        key_prefix (str): The key prefix or path within the S3 bucket.

    Properties:
        s3_url (str): A computed property that generates the full S3 URL in the format 's3://{bucket_name}/{key_prefix}'.
    """

    bucket_name: str
    key_prefix: str

    @property
    def s3_url(self) -> str:
        """
        Computes the full S3 URL using the bucket name and key prefix.

        Returns:
            str: The formatted S3 URL.
        """
        return f"s3://{self.bucket_name}/{self.key_prefix}"
