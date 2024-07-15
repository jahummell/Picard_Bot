import requests

class OktaService:
    """
    Service class for interacting with Okta to retrieve the list of active users.
    """
    def __init__(self, config):
        self.config = config

    def get_active_users(self):
        """
        Fetches the list of active users from Okta.
        """
        url = f"{self.config['base_url']}/api/v1/users"
        headers = {
            "Authorization": f"SSWS {self.config['api_token']}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        users = response.json()
        return [user['id'] for user in users if user['status'] == 'ACTIVE']
