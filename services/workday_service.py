import requests

class WorkdayService:
    """
    Service class for interacting with Workday to retrieve open, pending approvals,
    and to send approvals back to Workday.
    """
    def __init__(self, config):
        self.config = config

    def get_pending_approvals(self, user_id):
        """
        Fetches pending approvals for a specific user from Workday.
        """
        url = f"{self.config['base_url']}/api/pending_approvals"
        headers = {
            "Authorization": f"Bearer {self.config['api_token']}"
        }
        response = requests.get(url, headers=headers, params={"user_id": user_id})
        response.raise_for_status()
        return response.json()

    def send_approval(self, user_id, approval, comments):
        """
        Sends an approval back to Workday.
        """
        url = f"{self.config['base_url']}/api/approve"
        headers = {
            "Authorization": f"Bearer {self.config['api_token']}",
            "Content-Type": "application/json"
        }
        data = {
            "user_id": user_id,
            "approval_id": approval['id'],
            "comments": comments
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()
