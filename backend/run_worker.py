
import time
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # change to your project name
django.setup()

import requests
from django.utils import timezone
from django.db.models import Q
from api.models.webhook_models import WebhookEvent,Status
from api.settings import MAX_RETRIES,DEMO

class RunWorker:

    def _process_event(self, event:WebhookEvent):
        target_url = event.integration.target_url
        headers = event.headers # Original headers
        headers['Content-Type'] = 'application/json'
        
        try:
            response = requests.post(target_url, json=event.payload, headers=headers, timeout=10)
            
            # if 200 <= response.status_code < 300:
            if DEMO:
                event.status = Status.DELIVERED
                event.last_error = None
                event.save()
                msg = f'Event {event.id} delivered successfully.'
                print(msg)
                
            else:
                err_msg = f"HTTP {response.status_code}: {response.text}"
                self._handle_failure(event, err_msg)
        
        except Exception as e:
            self._handle_failure(event, str(e))

    def _handle_failure(self, event:WebhookEvent, error_msg):
        event.attempts += 1
        event.last_error = error_msg
        
        if event.attempts >= MAX_RETRIES:
            event.status = Status.FAILED
            event.next_retry_at = None
            msg = f'Event {event.id} failed permanently after {event.attempts} attempts.'
            print(msg)
        else:
            event.status = Status.RETRYING
            backoff_seconds = 2 ** event.attempts     #Increase the time like: 2s, 4s, 8s, 16s, 32s
            event.next_retry_at = timezone.now() + timezone.timedelta(seconds=backoff_seconds)
            msg = f'Event {event.id} failed (Attempt {event.attempts}). Retrying in {backoff_seconds}s.'
            print(msg)
        
        event.save()

    def handle(self):
        
        while True:
            now = timezone.now()
            events = WebhookEvent.objects.filter(
                status__in=[Status.PENDING, Status.RETRYING]
            ).filter(Q(next_retry_at__lte=now) | Q(next_retry_at__isnull=True)
            ).order_by('created_at')

            if not events.exists():
                time.sleep(1) # Pass the handler for 1sec, to avoiding busy loop
                msg = "Events Not found"
                print(msg)
                continue

            for event in events:
                self._process_event(event)
                
if __name__ == '__main__':
    RunWorker().handle()


