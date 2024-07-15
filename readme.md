# Slack Bot for Pending Approvals

## Overview

This Slack bot retrieves a list of pending approvals on behalf of users and allows them to approve or reject requests directly via Slack. The bot uses a service account with access to act on behalf of any user. The bot runs daily at 3 PM Pacific Time on an EC2 spot instance, retrieving user IDs from Okta and checking multiple systems for pending approvals. The bot sends the list of open approvals to the user, who can then respond with approvals or rejections.

## Project Structure
slack_bot_project/
├── Picard.py
├── app.py
├── README.md
├── requirements.txt
├── Dockerfile
├── terraform/
│   └── main.tf
├── services/
│   ├── __init__.py
│   ├── okta_service.py
│   ├── coupa_service.py
│   ├── brex_service.py
│   ├── jira_service.py
│   ├── servicenow_service.py
│   ├── workday_service.py
│   └── slack_service.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── database.py
└── config/
    └── settings.py



## Design

### clone_repo_as_text.py
- **Purpose**: creates a single text file representing the entire project to use for prompt engineering with generative AI
## Design

### Picard.py
- **Purpose**: Main entry point for the bot.
- **Functions**:
  - `__init__`: Initializes services and configurations.
  - `run`: Starts the daily process of fetching pending approvals.
  - `process_user_approvals`: Processes approvals for a specific user.
- **Logging**: Logs to console and database.
- **Test Mode**: Allows running the bot for a single user ID instead of retrieving the full list from Okta.

### app.py
- **Purpose**: Creates a Flask server to handle Slack events and interactive messages.
- **Functions**:
  - `slack_events`: Handles Slack events.
  - `slack_interactive`: Handles Slack interactive messages.

### services/okta_service.py
- **Purpose**: Retrieves the list of active users from Okta.
- **Functions**:
  - `get_active_users`: Fetches active users from Okta.

### services/coupa_service.py
- **Purpose**: Retrieves pending purchase requests and invoices from Coupa.
- **Functions**:
  - `get_pending_approvals`: Fetches pending approvals for a specific user from Coupa.
  - `send_approval`: Sends an approval back to Coupa.

### services/brex_service.py
- **Purpose**: Retrieves pending expense approvals and budget change requests from Brex.
- **Functions**:
  - `get_pending_approvals`: Fetches pending approvals for a specific user from Brex.
  - `send_approval`: Sends an approval back to Brex.

### services/jira_service.py
- **Purpose**: Retrieves pending actions for the user in Jira.
- **Functions**:
  - `get_pending_approvals`: Fetches pending approvals for a specific user from Jira.
  - `send_approval`: Sends an approval back to Jira.

### services/servicenow_service.py
- **Purpose**: Retrieves open pending approvals from ServiceNow.
- **Functions**:
  - `get_pending_approvals`: Fetches pending approvals for a specific user from ServiceNow.
  - `send_approval`: Sends an approval back to ServiceNow.

### services/workday_service.py
- **Purpose**: Retrieves open, pending approvals from Workday.
- **Functions**:
  - `get_pending_approvals`: Fetches pending approvals for a specific user from Workday.
  - `send_approval`: Sends an approval back to Workday.

### services/slack_service.py
- **Purpose**: Handles sending messages to users and receiving their responses in Slack.
- **Functions**:
  - `send_approval_list`: Sends the list of pending approvals to a user.
  - `get_user_email`: Retrieves the user email from Okta or a mapping.
  - `create_approval_message`: Creates the approval message to be sent to the user.
  - `send_message`: Sends a message to the user in Slack.
  - `handle_user_commands`: Handles the user's commands and processes approvals or rejections accordingly.
  - `send_help_message`: Sends a help message to the user with a list of commands and expected outcomes.
  - `send_invalid_command_message`: Sends a message to the user indicating the command was invalid.
  - `send_invalid_item_message`: Sends a message to the user indicating the item number was invalid.
  - `confirm_action`: Confirms the user's action (approval or rejection) for the specified item.
  - `handle_interactive_message`: Handles interactive messages from Slack.
  - `process_approval`: Processes the user's approval and sends it to the downstream system.
  - `process_rejection`: Processes the user's rejection and sends it to the downstream system.
  - `get_user_comment`: Retrieves the user's comment from Slack.
  - `send_action_confirmation`: Sends a confirmation message to the user after successfully processing the action.
  - `send_action_failure`: Sends a failure message to the user if the action could not be processed.
  - `send_action_cancelled_message`: Sends a message to the user indicating the action was cancelled.
  - `get_system_service`: Returns the service object for the specified system.

### utils/logger.py
- **Purpose**: Handles logging.
- **Functions**:
  - `setup_logging`: Sets up logging to console and database.

### utils/database.py
- **Purpose**: Manages interactions with a static database for tracking progress.
- **Functions**:
  - `__init__`: Initializes the database connection.
  - `create_table`: Creates a table for logging progress.
  - `log_approval`: Logs the approval details into the database.
  - `get_approval`: Retrieves the approval details from the database.

### config/settings.py
- **Purpose**: Contains configuration settings for the bot, including service account credentials, API endpoints, etc.
- **Retrieves Secrets**: Uses AWS Secrets Manager to securely retrieve secrets.

## Deployment

### Dockerfile
- Contains instructions to build the Docker image for the bot.

### Terraform
- **main.tf**: Contains Terraform configuration for deploying the bot on AWS EC2 spot instances.

## Setup

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3.	Configure your settings in config/settings.py.
4.	Build the Docker image:
    docker build -t slack-bot .
5. Deploy using Terraform:
    cd terraform
    terraform init
    terraform apply

## Usage
1. Run the bot
    python Picard.py
2. the bot will fetch pending approvals daily at 3 PM Pacific Time
3. Users will receive messages in Slack with pending approvals and instructions on how to approve / reject requests

## Logging
Logs are visible in the console and written to the database

## Secrets management
Shared secrets are stored in AWS Secrets Manager and referenced within the service-specific classes and files


## Structured Feedback
The bot recognizes the following commands:

list, approvals, list approvals - Retrieve a list of currently pending approvals with a numeric ID.
help - Display a list of commands and expected outcomes.
approve N - Approve the item with the number N.
reject N - Reject the item with the number N.

For every approval or rejection, the bot will confirm the full text of the item being rejected or approved, ask the user to provide a comment, and then process the approval or rejection in the downstream system. The bot will then respond with a confirmation that the action was completed and display the full list of pending approvals again for the user to continue to review.