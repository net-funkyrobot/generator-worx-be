import pickle

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .decorators import task_only


@csrf_exempt
@task_only
def deferred_handler(request):
    service_obj = pickle.loads(request.body)
    service_obj.run()

    return HttpResponse("OK")
