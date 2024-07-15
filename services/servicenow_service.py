import requests

class ServiceNowService:
    """
    Service class for interacting with ServiceNow to retrieve open pending approvals,
    and to send approvals back to ServiceNow.
    """
    def __init__(self, config):
        self.config = config

    def get_pending_approvals(self, user_id):
        """
        Fetches pending approvals for a specific user from ServiceNow.
        """
        url = f"{self.config['base_url']}/api/now/table/approval"
        headers = {
            "Authorization": f"Bearer {self.config['api_token']}"
        }
        response = requests.get(url, headers=headers, params={"assigned_to": user_id, "state": "pending"})
        response.raise_for_status()
        return response.json()['result']

    def send_approval(self, user_id, approval, comments):
        """
        Sends an approval back to ServiceNow.
        """
        url = f"{self.config['base_url']}/api/now/table/approval/{approval['id']}"
        headers = {
            "Authorization": f"Bearer {self.config['api_token']}",
            "Content-Type": "application/json"
        }
        data = {
            "state": "approved",
            "comments": comments
        }
        response = requests.patch(url, headers=headers, json=data)
        return response.json()
