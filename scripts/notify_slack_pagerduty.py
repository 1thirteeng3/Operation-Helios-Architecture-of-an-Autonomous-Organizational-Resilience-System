"""Send notifications to Slack and PagerDuty.

This script provides helper functions to send alert messages to a Slack
channel via Incoming Webhook and to trigger incidents on PagerDuty using
the Events API v2. Use it within your alerting pipeline (e.g., Prometheus
Alertmanager integrations) to simulate real-time collaboration during
incidents.

Environment variables:

 - SLACK_WEBHOOK_URL: URL do webhook do Slack.
 - PAGERDUTY_INTEGRATION_KEY: chave de integração do PagerDuty.

Usage:

    python scripts/notify_slack_pagerduty.py --message "Incident detected" --severity critical

"""

import argparse
import json
import os
import sys
from typing import Optional

try:
    import requests  # type: ignore
except ImportError:
    requests = None  # will fallback to urllib
import urllib.request


def send_slack(message: str) -> None:
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook:
        print("[notify] Slack webhook não configurado", file=sys.stderr)
        return
    payload = {"text": message}
    if requests:
        resp = requests.post(webhook, json=payload, timeout=5)
        if resp.status_code != 200:
            print(f"[notify] Falha ao enviar mensagem ao Slack: {resp.text}", file=sys.stderr)
    else:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(webhook, data=data, headers={'Content-Type': 'application/json'})
        try:
            urllib.request.urlopen(req, timeout=5)
        except Exception as exc:
            print(f"[notify] Falha ao enviar mensagem ao Slack: {exc}", file=sys.stderr)


def trigger_pagerduty(message: str, severity: str = "error") -> None:
    key = os.environ.get("PAGERDUTY_INTEGRATION_KEY")
    if not key:
        print("[notify] Chave de integração do PagerDuty não configurada", file=sys.stderr)
        return
    event = {
        "routing_key": key,
        "event_action": "trigger",
        "payload": {
            "summary": message,
            "severity": severity,
            "source": "helius-sim-lab",
        },
    }
    url = "https://events.pagerduty.com/v2/enqueue"
    if requests:
        resp = requests.post(url, json=event, timeout=5)
        if resp.status_code >= 300:
            print(f"[notify] Falha ao acionar o PagerDuty: {resp.text}", file=sys.stderr)
    else:
        data = json.dumps(event).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        try:
            urllib.request.urlopen(req, timeout=5)
        except Exception as exc:
            print(f"[notify] Falha ao acionar o PagerDuty: {exc}", file=sys.stderr)


def main(message: str, severity: str) -> None:
    send_slack(message)
    trigger_pagerduty(message, severity)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enviar notificações para Slack e PagerDuty")
    parser.add_argument("--message", required=True, help="Mensagem a ser enviada")
    parser.add_argument("--severity", default="error", help="Severidade do incidente (info, warning, error, critical)")
    args = parser.parse_args()
    main(args.message, args.severity)