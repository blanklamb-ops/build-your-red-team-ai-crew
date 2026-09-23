#!/usr/bin/env python3
"""
RSVP webhook server for GoPhish-ICS campaigns.
Receives calendar response notifications and records telemetry.
"""

from flask import Flask, request, jsonify
from telemetry import TelemetryStore, RSVPStatus
import yaml
import logging

app = Flask(__name__)
telemetry_store = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_server(config_path: str = 'config.yaml'):
    """
    Initialize server with configuration.

    Args:
        config_path: Path to config file
    """
    global telemetry_store

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    db_path = config.get('database', {}).get('path', 'telemetry.db')
    telemetry_store = TelemetryStore(db_path)

    logger.info(f"Initialized telemetry store at {db_path}")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


@app.route('/rsvp', methods=['POST'])
def rsvp_webhook():
    """
    Handle RSVP webhook from calendar clients or mail gateways.

    Expected JSON payload:
    {
        "campaign_id": "campaign-123",
        "recipient_id": "recipient-456",
        "recipient_email": "user@example.com",
        "status": "ACCEPTED|DECLINED|TENTATIVE|NEEDS-ACTION"
    }
    """
    if not telemetry_store:
        return jsonify({'error': 'Server not initialized'}), 500

    try:
        data = request.get_json()

        # Validate required fields
        required = ['campaign_id', 'recipient_id', 'recipient_email', 'status']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Parse status
        try:
            status = RSVPStatus(data['status'])
        except ValueError:
            return jsonify({'error': f'Invalid status: {data["status"]}'}), 400

        # Extract optional metadata
        user_agent = request.headers.get('User-Agent')
        ip_address = request.headers.get('X-Forwarded-For') or request.remote_addr

        # Record RSVP
        telemetry_store.record_rsvp(
            campaign_id=data['campaign_id'],
            recipient_id=data['recipient_id'],
            recipient_email=data['recipient_email'],
            status=status,
            user_agent=user_agent,
            ip_address=ip_address
        )

        logger.info(f"Recorded RSVP: {data['recipient_email']} -> {status.value}")

        return jsonify({
            'status': 'recorded',
            'campaign_id': data['campaign_id'],
            'recipient_id': data['recipient_id']
        }), 200

    except Exception as e:
        logger.error(f"Error processing RSVP: {e}")
        return jsonify({'error': str(e)}), 500


def run_server(config_path: str = 'config.yaml'):
    """
    Run the RSVP webhook server.

    Args:
        config_path: Path to config file
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    init_server(config_path)

    host = config.get('server', {}).get('host', '127.0.0.1')
    port = config.get('server', {}).get('port', 8080)

    logger.info(f"Starting RSVP server on {host}:{port}")
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    run_server()
