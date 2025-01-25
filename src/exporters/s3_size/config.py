from pydantic import BaseModel


class Config(BaseModel):
    bucket_name: str
    key_prefix: str

    @property
    def s3_url(self) -> str:
        return f"s3://{self.bucket_name}/{self.key_prefix}"
