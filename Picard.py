import logging
from services.okta_service import OktaService
from services.coupa_service import CoupaService
from services.brex_service import BrexService
from services.jira_service import JiraService
from services.servicenow_service import ServiceNowService
from services.workday_service import WorkdayService
from services.slack_service import SlackService
from utils.logger import setup_logging
from utils.database import Database
from config.settings import Config
from datetime import datetime

class Picard:
    """
    Main class for the Slack bot. Initializes services, manages scheduling, and handles logging.
    """
    def __init__(self):
        self.config = Config()
        self.db = Database(self.config.database_uri)
        self.logger = setup_logging(self.config.log_level)
        self.okta_service = OktaService(self.config.okta)
        self.coupa_service = CoupaService(self.config.coupa)
        self.brex_service = BrexService(self.config.brex)
        self.jira_service = JiraService(self.config.jira)
        self.servicenow_service = ServiceNowService(self.config.servicenow)
        self.workday_service = WorkdayService(self.config.workday)
        self.slack_service = SlackService(self.config.slack)

    def run(self, test_user_id=None):
        """
        Starts the daily process of fetching pending approvals.
        If test_user_id is provided, runs the bot for a single user ID instead of retrieving the full list from Okta.
        """
        self.logger.info("Starting daily run...")
        if test_user_id:
            user_ids = [test_user_id]
            self.logger.info(f"Running in test mode for user ID: {test_user_id}")
        else:
            user_ids = self.okta_service.get_active_users()
            self.logger.info(f"Retrieved {len(user_ids)} users from Okta")
        for user_id in user_ids:
            self.process_user_approvals(user_id)

    def process_user_approvals(self, user_id):
        """
        Processes approvals for a specific user by retrieving pending approvals from multiple systems
        and sending the list to the user via Slack.
        """
        approvals = []
        approvals.extend(self.coupa_service.get_pending_approvals(user_id))
        approvals.extend(self.brex_service.get_pending_approvals(user_id))
        approvals.extend(self.jira_service.get_pending_approvals(user_id))
        approvals.extend(self.servicenow_service.get_pending_approvals(user_id))
        approvals.extend(self.workday_service.get_pending_approvals(user_id))
        
        self.slack_service.send_approval_list(user_id, approvals)

if __name__ == "__main__":
    bot = Picard()
    # Uncomment for test mode
    # single_user_id = 'user_id_here'
    # bot.run(test_user_id=single_user_id)
    bot.run()
