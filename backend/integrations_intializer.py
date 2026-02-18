import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # change to your project name
django.setup()

from api.models.webhook_models import Integration

def initializer():
     
     integrations = [
          {
          "name": "Customer Payment Webhook",
          "api_key": "secret-key-001",
          "target_url": "https://webhook.site/razorpay/b8b9b8b9"
          },
          {
          "name": "Courier Update Integration",
          "api_key": "secret-key-002",
          "target_url": "https://webhook.site/dtdc/a1b0b8b9-b8b9"
     },
          {
          "name": "OTP Verification Service",
          "api_key": "secret-key-003",
          "target_url": "http://invalid-domain-xyz-123.com/webhook"
     }
          ]
     
     
     for integration in integrations:     
          Integration.objects.create(
               name = integration.get('name'),
               api_key = integration.get('api_key'),
               target_url = integration.get('target_url')
          )
     
     print("Data inserted for integration successfully")
          
          
if __name__ == '__main__':
    initializer()
          
          