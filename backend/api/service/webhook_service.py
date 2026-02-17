from rest_framework import status
from api.models.webhook_models import WebhookEvent,Integration,Status
from rest_framework.response import Response

class WebhookService:
     def __init__(self,data,headers,cmd):
          self.data = data
          self.headers = headers
          self.cmd = cmd
          
     def _reqData(self):
          self.api_key = self.headers.get('X-API-Key')
          self.pay_load = self.data.get('payload')
          self.id = self.data.get('id')
          
     def _create_event(self):
          try:
          
               integrations = Integration.objects.filter(api_key = self.api_key).first()
               
               if not integrations:
                    raise Exception("Integration not found")
               
               event = WebhookEvent.objects.create(
                    integration=integrations,
                    payload=self.pay_load,
                    headers=dict(self.headers),
                    status=Status.PENDING
               )
               
               return Response({'id': event.id, 'status': 'Accepted'},status=status.HTTP_202_ACCEPTED)
          
          except Exception as e:
               return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
     def _retry(self):
          
          try:
               event = WebhookEvent.objects.filter(id = self.id,status=Status.FAILED).first()
               
               if not event:
                    raise Exception("Event is not found")
               
               event.status = Status.PENDING
               event.attempts = 0
               event.next_retry_at = None
               event.last_error = None
               event.save()
               return Response({'status': 'Event queued for replay'}, status=status.HTTP_200_OK)
          
          except Exception as e:
               return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
          
     def _get_all(self):
          try:
               
               response = []
               events = (WebhookEvent.objects.select_related('integration').only('id', 'status', 'integration__name','integration__created_at'))
               for event in events:
                    data = {
                         "id": event.id,
                         "name": event.integration.name,
                         "status": event.get_status_display(),
                         'timestamp': event.integration.created_at
                    }
                    
                    response.append(data)
                    
               return Response(response, status=status.HTTP_200_OK)
          
          except Exception as e:
               return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
     def _get_by_id(self):
          try:

               event = (
                    WebhookEvent.objects
                    .select_related('integration')
                    .only(
                         'id',
                         'attempts',
                         'payload',
                         'status',
                         'headers',
                         'integration__name',
                         'integration__target_url'
                    )
                    .get(id=self.id))

               data = {
               "id": event.id,
               "name": event.integration.name,
               "attempts": event.attempts,
               'headers': event.headers,
               "payload": event.payload,
               "url": event.integration.target_url,
               "status": event.get_status_display()
               }

               return Response(data, status=status.HTTP_200_OK)
          
          except Exception as e:
               return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)            

     def manage(self):
          self._reqData()
          
          match self.cmd:
               case 'create_event':
                    return self._create_event()
                    
               case 'retry_event':
                    return self._retry()
               
               case _:
                    msg = "endpoint not found"
                    return Response(msg,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
               
     def get(self,id):
          self.id = id 
          
          match self.cmd:
               case 'get':
                    if self.id:
                         return self._get_by_id()
                    else:
                         return self._get_all()
                    
               case _:
                    msg = "endpoint not found"
                    return Response(msg,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
               
               
          
          
          
          
     