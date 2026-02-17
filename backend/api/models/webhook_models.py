import uuid
from django.db import models

class Integration(models.Model):
     name = models.CharField(max_length=255)
     api_key = models.CharField(max_length=255, unique=True)
     target_url = models.URLField()
     created_at = models.DateTimeField(auto_now_add=True)
     
     class Meta:
          db_table = 'tb_integrations'             #"tb_" means table. I use it only as a naming convention.

     def __str__(self):
          return self.name
     
class Status(models.IntegerChoices):
     
     PENDING = 1, "Pending"
     DELIVERED = 2, "Delivered"
     FAILED = 3, "Failed"
     RETRYING = 4, "Retrying"

class WebhookEvent(models.Model):
     integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='tb_integrations')
     payload = models.JSONField()
     headers = models.JSONField(default=dict)
     status = models.IntegerField(choices=Status.choices,default=Status.PENDING)
     attempts = models.IntegerField(default=0)
     last_error = models.TextField(null=True, blank=True)
     next_retry_at = models.DateTimeField(null=True, blank=True)
     created_at = models.DateTimeField(auto_now_add=True)

     class Meta:
          db_table = 'tb_webhook_event'            #"tb_" means table. I use it only as a naming convention.
          ordering = ['-created_at']

     # def __str__(self):
     #      return f"{self.integration.name} - {self.id} - {self.status}"
