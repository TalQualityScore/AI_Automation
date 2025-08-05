class NotificationSender:
    def __init__(self, smtp_config, slack_webhook):
        self.smtp_config = smtp_config
        self.slack_webhook = slack_webhook
    
    def send_completion_email(self, result, recipient):
        # Email implementation
        pass
    
    def send_slack_notification(self, result, webhook_url):
        # Slack webhook implementation
        pass