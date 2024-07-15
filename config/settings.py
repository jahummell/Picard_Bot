import boto3
import json

class Config:
    """
    Contains configuration settings for the bot, including service account credentials, API endpoints, etc.
    Retrieves secrets from AWS Secrets Manager.
    """
    def __init__(self):
        self.database_uri = 'database.db'
        self.log_level = 'INFO'
        self.okta = self.get_secret("okta_secret")
        self.coupa = self.get_secret("coupa_secret")
        self.brex = self.get_secret("brex_secret")
        self.jira = self.get_secret("jira_secret")
        self.servicenow = self.get_secret("servicenow_secret")
        self.workday = self.get_secret("workday_secret")
        self.slack = self.get_secret("slack_secret")

    def get_secret(self, secret_name):
        """
        Retrieves a secret from AWS Secrets Manager.
        """
        client = boto3.client('secretsmanager')

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except Exception as e:
            raise Exception(f"Error retrieving secret {secret_name}: {e}")

        # Decrypts secret using the associated KMS key.
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
