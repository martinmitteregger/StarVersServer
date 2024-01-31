import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from uuid import UUID

from delayedqueue import DelayedQueue

from app.services.starvers_polling_task import StarVersPollingTask


LOG = logging.getLogger(__name__)

class ScheduledThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers=10, name=''):
        super().__init__(max_workers=max_workers, thread_name_prefix=name)
        self._max_workers = max_workers
        self.queue = DelayedQueue()
        self.shutdown = False

    def schedule_polling_at_fixed_rate(self, knowledge_graph_id: UUID, period: int, *args, **kwargs) -> bool:
        if self.shutdown:
            raise RuntimeError(f"Cannot schedule new task after shutdown!")
        
        task = StarVersPollingTask(knowledge_graph_id, period*1000, *args, is_fixed_rate=True, executor_ctx=self, **kwargs)
        return self._put(task, 0)

    def _put(self, task: StarVersPollingTask, delay: int) -> bool:
        if delay < 0:
            raise ValueError(f"Delay `{delay}` must be a non-negative number")
        LOG.info(f"Enqueuing {task} with delay of {delay}")
        return self.queue.put(task, delay)

    def __run(self):
        while not self.shutdown:
            try:
                print('Check Queue...')
                task: StarVersPollingTask = self.queue.get()
                print('Task found...')
                future = super().submit(task.run)
                future.result()
            except Exception as e:
                print(e)

    def stop(self, wait_for_completion: Optional[bool] = True):
        self.shutdown = True
        super().shutdown(wait_for_completion)

    def start(self):
        t = threading.Thread(target=self.__run)
        t.setDaemon(True)
        t.start()
