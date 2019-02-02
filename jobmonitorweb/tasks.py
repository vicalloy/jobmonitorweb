from asgiref.sync import async_to_sync
from celery.schedules import crontab
from channels.layers import get_channel_layer

from jobmonitorweb import celery_app

from .models import Monitor


@celery_app.task
def check_jobs(monitor_pk):
    group_name = "job_monitor_messages"
    channel_layer = get_channel_layer()

    monitor = Monitor.objects.get(pk=monitor_pk)
    monitor.monitor_jobs(group_name=group_name, channel_layer=channel_layer)
    monitor.task_id = ''
    monitor.save()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_message',
            'message_type': 'task_status',
            'message': monitor.get_task_status(),
            'monitor_pk': monitor.pk
        }
    )


def celery_check_jobs(monitor):
    if not isinstance(monitor, Monitor):
        monitor = Monitor.objects.filter(pk=monitor).first()
    task = celery_check_jobs.delay(monitor.pk)
    monitor.task_id = task.task_id
    monitor.save()
