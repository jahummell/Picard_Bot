from flask import Flask, request, jsonify
from services.slack_service import SlackService
from config.settings import Config
import json

app = Flask(__name__)
config = Config()
slack_service = SlackService(config)

@app.route('/slack/events', methods=['POST'])
def slack_events():
    """
    Endpoint to handle Slack events.
    """
    data = request.json

    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})

    event = data.get('event', {})
    if event.get('type') == 'message' and 'subtype' not in event:
        user_id = event.get('user')
        text = event.get('text')
        slack_service.handle_user_commands(user_id, text)

    return jsonify({'status': 'ok'})

@app.route('/slack/interactive', methods=['POST'])
def slack_interactive():
    """
    Endpoint to handle Slack interactive messages.
    """
    payload = request.form.get('payload')
    data = json.loads(payload)

    user_id = data['user']['id']
    actions = data['actions']
    if actions:
        action = actions[0]
        action_id = action['action_id']
        value = action['value']
        slack_service.handle_interactive_message(user_id, action_id, value)

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=3000, debug=True)
