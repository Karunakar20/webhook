from rest_framework.views import APIView

from api.service.webhook_service import WebhookService

class WebhookView(APIView):
     def get(self,request):
          data = request.data
          headers = request.headers
          cmd = request.query_params.get('cmd', None)
          id = request.query_params.get('id', None)
          
          return WebhookService(data,headers,cmd).get(id)
     
     def post(self,request):
          
          data = request.data
          headers = request.headers
          cmd = request.query_params.get('cmd', None)
          
          return WebhookService(data,headers,cmd).manage()
          
          
