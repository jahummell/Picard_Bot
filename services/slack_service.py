import requests
import json
from datetime import datetime
from threading import Timer
from services.coupa_service import CoupaService
from services.brex_service import BrexService
from services.jira_service import JiraService
from services.servicenow_service import ServiceNowService
from services.workday_service import WorkdayService

class SlackService:
    """
    Service class for interacting with Slack to send messages to users and receive their responses.
    """
    def __init__(self, config):
        self.config = config
        self.pending_approvals = {}
        self.user_responses = {}

    def send_approval_list(self, user_id, approvals):
        """
        Sends the list of pending approvals to a user via Slack.
        """
        user_email = self.get_user_email(user_id)
        message = self.create_approval_message(approvals)
        self.pending_approvals[user_id] = approvals
        self.send_message(user_email, message)

    def get_user_email(self, user_id):
        """
        Retrieves the user email from Okta or a mapping.
        """
        # Implementation for retrieving user email from Okta or a mapping
        return f"user_{user_id}@example.com"  # Placeholder

    def create_approval_message(self, approvals):
        """
        Creates the approval message to be sent to the user.
        """
        message = "You have pending approvals:\n"
        for idx, approval in enumerate(approvals, 1):
            message += f"{idx}. {approval['summary']} ({approval['date']}) - {approval['link']}\n"
        message += "\nCommands:\n"
        message += "1. 'list', 'approvals', 'list approvals' - Retrieve a list of currently pending approvals\n"
        message += "2. 'help' - Display a list of commands and expected outcomes\n"
        message += "3. 'approve N' - Approve the item with the number N\n"
        message += "4. 'reject N' - Reject the item with the number N\n"
        return message

    def send_message(self, user_email, message):
        """
        Sends a message to the user in Slack.
        """
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.config['api_token']}",
            "Content-Type": "application/json"
        }
        data = {
            "channel": user_email,
            "text": message
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

    def handle_user_commands(self, user_id, command):
        """
        Handles the user's commands and processes approvals or rejections accordingly.
        """
        command_parts = command.strip().lower().split()
        approvals = self.pending_approvals.get(user_id, [])

        if command in ['list', 'approvals', 'list approvals']:
            self.send_approval_list(user_id, approvals)
        elif command == 'help' or not command_parts[0] in ['approve', 'reject']:
            self.send_help_message(user_id)
        elif command_parts[0] in ['approve', 'reject']:
            if len(command_parts) == 2 and command_parts[1].isdigit():
                item_number = int(command_parts[1])
                if 1 <= item_number <= len(approvals):
                    approval = approvals[item_number - 1]
                    self.confirm_action(user_id, command_parts[0], approval)
                else:
                    self.send_invalid_item_message(user_id)
            else:
                self.send_invalid_command_message(user_id)

    def send_help_message(self, user_id):
        """
        Sends a help message to the user with a list of commands and expected outcomes.
        """
        message = ("Commands:\n"
                   "1. 'list', 'approvals', 'list approvals' - Retrieve a list of currently pending approvals\n"
                   "2. 'help' - Display a list of commands and expected outcomes\n"
                   "3. 'approve N' - Approve the item with the number N\n"
                   "4. 'reject N' - Reject the item with the number N\n")
        self.send_message(user_id, message)

    def send_invalid_command_message(self, user_id):
        """
        Sends a message to the user indicating the command was invalid.
        """
        message = "Invalid command. Type 'help' for a list of valid commands."
        self.send_message(user_id, message)

    def send_invalid_item_message(self, user_id):
        """
        Sends a message to the user indicating the item number was invalid.
        """
        message = "Invalid item number. Type 'list' to see the list of pending approvals."
        self.send_message(user_id, message)

    def confirm_action(self, user_id, action, approval):
        """
        Confirms the user's action (approval or rejection) for the specified item.
        """
        action_text = "approve" if action == "approve" else "reject"
        message = (f"Please confirm that you wish to {action_text} '{approval['summary']} ({approval['date']}) - {approval['link']}' "
                   f"by typing 'Y' or 'Yes'.")
        self.user_responses[user_id] = {
            'action': action,
            'approval': approval
        }
        self.send_message(user_id, message)

    def handle_interactive_message(self, user_id, action_id, value):
        """
        Handles interactive messages from Slack.
        """
        if action_id in ['approve', 'reject']:
            approvals = self.pending_approvals.get(user_id, [])
            item_number = int(value)
            approval = approvals[item_number - 1]
            if action_id == 'approve':
                self.process_approval(user_id, approval)
            else:
                self.process_rejection(user_id, approval)

    def process_approval(self, user_id, approval):
        """
        Processes the user's approval and sends it to the downstream system.
        """
        comment = self.get_user_comment(user_id)
        system_service = self.get_system_service(approval['system'])
        response = system_service.send_approval(user_id, approval, comment)
        if response['status'] == 'success':
            self.send_action_confirmation(user_id, 'approved', approval, comment)
        else:
            self.send_action_failure(user_id, 'approve', approval)

    def process_rejection(self, user_id, approval):
        """
        Processes the user's rejection and sends it to the downstream system.
        """
        comment = self.get_user_comment(user_id)
        system_service = self.get_system_service(approval['system'])
        response = system_service.send_rejection(user_id, approval, comment)
        if response['status'] == 'success':
            self.send_action_confirmation(user_id, 'rejected', approval, comment)
        else:
            self.send_action_failure(user_id, 'reject', approval)

    def get_user_comment(self, user_id):
        """
        Retrieves the user's comment from Slack.
        """
        self.send_message(user_id, "Please provide a comment for your action:")
        while user_id not in self.user_responses or 'comment' not in self.user_responses[user_id]:
            pass  # Wait for user response
        return self.user_responses[user_id]['comment']

    def send_action_confirmation(self, user_id, action, approval, comment):
        """
        Sends a confirmation message to the user after successfully processing the action.
        """
        action_text = "approved" if action == "approve" else "rejected"
        message = (f"Successfully {action_text} '{approval['summary']} ({approval['date']}) - {approval['link']}'\n"
                   f"User: {user_id}\n"
                   f"Date/Time: {datetime.now()}\n"
                   f"Comment: {comment}")
        self.send_message(user_id, message)

    def send_action_failure(self, user_id, action, approval):
        """
        Sends a failure message to the user if the action could not be processed.
        """
        action_text = "approve" if action == "approve" else "reject"
        message = f"Failed to {action_text} '{approval['summary']} ({approval['date']}) - {approval['link']}'"
        self.send_message(user_id, message)

    def send_action_cancelled_message(self, user_id):
        """
        Sends a message to the user indicating the action was cancelled.
        """
        message = "Action cancelled."
        self.send_message(user_id, message)

    def get_system_service(self, system_name):
        """
        Returns the service object for the specified system.
        """
        services = {
            'coupa': CoupaService(self.config.coupa),
            'brex': BrexService(self.config.brex),
            'jira': JiraService(self.config.jira),
            'servicenow': ServiceNowService(self.config.servicenow),
            'workday': WorkdayService(self.config.workday)
        }
        return services[system_name]
