from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Monitor
from .tasks import celery_check_jobs


def index(request):
    qs = Monitor.objects.filter(is_active=True)
    return render(request, 'jobmonitorweb/index.html', {'qs': qs})


@csrf_exempt
def check_jobs(request):
    monitor_pk = request.POST.get('monitor_pk', '')
    monitor = Monitor.objects.get(pk=monitor_pk)
    if not monitor.can_start():
        return JsonResponse({
            "task_status": monitor.get_task_status(),
        })
    celery_check_jobs.delay(monitor)
    return JsonResponse({
        "task_status": 'RUNNING',
    })
