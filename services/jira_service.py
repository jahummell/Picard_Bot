import requests

class JiraService:
    """
    Service class for interacting with Jira to retrieve pending actions for the user,
    and to send approvals back to Jira.
    """
    def __init__(self, config):
        self.config = config

    def get_pending_approvals(self, user_id):
        """
        Fetches pending approvals for a specific user from Jira.
        """
        url = f"{self.config['base_url']}/rest/api/2/search"
        headers = {
            "Authorization": f"Bearer {self.config['api_token']}"
        }
        jql = f"assignee={user_id} AND status='Pending Approval'"
        response = requests.get(url, headers=headers, params={"jql": jql})
        response.raise_for_status()
        return response.json()['issues']

    def send_approval(self, user_id, approval, comments):
        """
        Sends an approval back to Jira.
        """
        url = f"{self.config['base_url']}/rest/api/2/issue/{approval['id']}/transitions"
        headers = {
            "Authorization": f"Bearer {self.config['api_token']}",
            "Content-Type": "application/json"
        }
        data = {
            "transition": {
                "id": "approve_transition_id"
            },
            "fields": {
                "comment": {
                    "add": {
                        "body": comments
                    }
                }
            }
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()
