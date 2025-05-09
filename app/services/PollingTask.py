import time
from datetime import datetime
from uuid import UUID

import requests

from app.Database import Session, engine
from app.LoggingConfig import get_logger
from app.models.TrackingTaskModel import TrackingTaskDto
from app.services.VersioningService import StarVersService

LOG = get_logger(__name__)

class PollingTask():
    def __init__(self, dataset_id: UUID, period: int, *args, time_func=time.time, is_initial=True, **kwargs):
        super().__init__()
        self.dataset_id = dataset_id
        self.period = period
        self.args = args
        self.kwargs = kwargs
        self.__stopped = False
        self.__time_func = time_func
        self.__is_initial = is_initial
        self.next_run = self.__time_func()
        self.__versioning_wrapper = None

    @property
    def is_initial_run(self) -> bool:
        return self.__is_initial
    
    @property
    def executor_ctx(self):
        return self.kwargs['executor_ctx']
    
    @property
    def time_func(self):
        return self.__time_func

    def __get_next_run(self) -> int:
        return self.__time_func() + self.period

    def set_next_run(self, time_taken: int = 0) -> None:
        self.__is_initial = False
        self.next_run = self.__get_next_run() - time_taken

    def __lt__(self, other) -> bool:
        return self.next_run < other.next_run

    def __repr__(self) -> str:
        return f"(Polling Task {self.dataset_id}, Periodic: {self.period} seconds (s), Next run: {time.ctime(self.next_run)})"

    def run(self):
        start_time = time.time_ns()
        try:
            with Session(engine) as session:
                self.__stopped = self.__run(session)
        except Exception as e:
            LOG.error(e)
        finally:
            if self.__stopped:
                LOG.info(f'Stopped tracking task for dataset with uuid={self.dataset_id}!')
                return
            
            end_time = time.time_ns()
            time_taken = (end_time - start_time) / 1_000_000_000 # convert ns to s
            
            self.set_next_run(time_taken)
            next_delay = self.period - time_taken
            if next_delay < 0 or self.next_run <= self.__time_func():
                self.executor_ctx._put(self, 0)
            else:
                self.executor_ctx._put(self, next_delay)

    def __run(self, session: Session) -> bool:
        LOG.info(f"[{self.dataset_id}] Start tracking task for dataset")

        from app.services.ManagementService import get_by_id
        dataset = get_by_id(id=self.dataset_id, session=session)

        if not dataset.active:
            return True

        version_timestamp = datetime.now()

        if self.__versioning_wrapper is None:
            tracking_task = TrackingTaskDto(
                id=dataset.id,
                name=dataset.repository_name,
                rdf_dataset_url=dataset.rdf_dataset_url,
                delta_type=dataset.delta_type)
                        
            self.__versioning_wrapper = StarVersService(tracking_task)

        if (self.__is_initial): # if initial no diff is necessary
            LOG.info(f"[{self.dataset_id}] Initial version for dataset")

            # push triples into repository
            self.__versioning_wrapper.run_initial_versioning(version_timestamp)

        else: # get diff to previous version using StarVers
            delta_event = self.__versioning_wrapper.run_versioning(version_timestamp)

            if delta_event is not None:
                LOG.info(f"[{self.dataset_id}] Changes for dataset detected")

                if dataset.notification_webhook is not None:
                    LOG.info(f"[{self.dataset_id}] Notified webhook for dataset")
                    requests.post(dataset.notification_webhook, json=delta_event.model_dump(mode='json'))
            else:
                LOG.info(f"[{self.dataset_id}] No changes for dataset detected")
                return
        
        dataset.last_modified = version_timestamp
        session.commit()
        session.refresh(dataset)

        LOG.info(f"[{self.dataset_id}] Finished tracking task for dataset")

        return False
