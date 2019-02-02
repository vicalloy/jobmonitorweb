import json

import pytz
from celery.result import AsyncResult
from django.conf import settings
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django_celery_beat.models import CrontabSchedule
from django_celery_beat.models import PeriodicTask
from jsonfield import JSONField
from lbutils import create_instance

from .jobmonitorstorages import JobMonitorJsonPlusStorage


class Param(models.Model):
    code = models.CharField(_('Param code'), max_length=200)
    value = models.CharField(_('Value'), max_length=200)
    description = models.CharField(_('Description'), max_length=200)

    class Meta:
        ordering = ('code',)

    def __str__(self):
        return self.value


class Monitor(models.Model):
    title = models.CharField(_('Title'), max_length=200)
    is_active = models.BooleanField(_('Is active'), default=True)
    params = JSONField()
    skip_words = models.CharField(_('Skip words'), max_length=200, blank=True)
    monitor_class = models.ForeignKey(
        Param,
        limit_choices_to={'code': 'monitor_class'},
        related_name='monitor_class_monitors',
        null=True, on_delete=models.SET_NULL)
    message_backends = models.ManyToManyField(
        Param, blank=True,
        limit_choices_to={'code': 'message_backend'},
        related_name='message_backend_monitors',
        verbose_name='Message backends')
    schedule = JSONField(blank=True)

    task_id = models.CharField(_('Task id'), max_length=200, blank=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title

    def get_task_status(self):
        if not self.task_id:
            return 'None'
        result = AsyncResult(self.task_id)
        return result.status

    def can_start(self):
        task_status = self.get_task_status()
        return task_status in ['None', 'REVOKED', 'FAILURE']

    def get_skip_word_list(self):
        word_list = self.skip_words.split(',')
        word_list = [e.strip() for e in word_list if e.strip()]
        return word_list

    def get_message_backend_list(self, **kwargs):
        message_backend_list = []
        for message_backend_param in self.message_backends.all():
            message_backend_factory = getattr(settings, 'JM_MESSAGE_BACKEND_FACTORY', None)
            message_backend = message_backend_factory(
                message_backend_param.value,
                self,
                **kwargs,
            )
            message_backend_list.append(message_backend)
        return message_backend_list

    def monitor_jobs(self, **kwargs):
        storage = JobMonitorJsonPlusStorage(base_path=settings.DATA_DIR, monitor=self)

        message_backend_list = self.get_message_backend_list(
            **kwargs
        )
        monitor_class_name = self.monitor_class.value
        monitor = create_instance(
            monitor_class_name,
            storage=storage,
            message_backend_list=message_backend_list
        )
        monitor.monitor_jobs(params=self.params, skip_words=self.get_skip_word_list())


class MonitorLog(models.Model):
    monitor = models.ForeignKey(
        Monitor,
        related_name="logs",
        on_delete=models.CASCADE)
    message = models.TextField(_('message'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    def __str__(self):
        return self.message

    class Meta:
        ordering = ('-created_at',)


def update_periodic_task(monitor, is_delete=False):
    task_name = "monitor_%s" % monitor.pk
    if is_delete:
        PeriodicTask.objects.filter(name=task_name).delete()
    if not monitor.schedule:
        return
    timezone = pytz.timezone(settings.TIME_ZONE)
    schedule, _ = CrontabSchedule.objects.get_or_create(
        timezone=timezone,
        **monitor.schedule
    )
    task = PeriodicTask.objects.filter(name=task_name).first()
    if not task:
        task = PeriodicTask(name=task_name)
    task.enabled = monitor.is_active
    task.crontab = schedule
    task.task = 'jobmonitorweb.tasks.celery_check_jobs'
    task.kwargs = json.dumps({
        'monitor': monitor.pk,
    })
    task.save()


@receiver(signals.post_delete, sender=Monitor)
def update_periodic_task_on_delete(sender, instance, *args, **kwargs):
    update_periodic_task(instance, is_delete=True)


@receiver(signals.post_save, sender=Monitor)
def update_periodic_task_on_save(sender, instance, *args, **kwargs):
    update_periodic_task(instance, is_delete=False)
