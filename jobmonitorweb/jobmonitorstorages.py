import os

from jobmonitor.storage import JobMonitorJsonStorage


class JobMonitorJsonPlusStorage(JobMonitorJsonStorage):
    def __init__(self, base_path, monitor):
        self.base_path = base_path
        self.monitor = monitor

    def get_file_name(self, data_type):
        fn = "%s-%s.json" % (data_type, self.monitor.pk)
        return os.path.join(self.base_path, fn)
