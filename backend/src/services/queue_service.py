import asyncio
import threading
import time
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from src.utils.logging import get_logger


logger = get_logger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class QueueTask:
    id: str
    task_type: str
    payload: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class RequestQueueService:
    """
    Service to manage request queuing for AI queries to manage load
    """
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.task_queue = asyncio.Queue()
        self.active_tasks: Dict[str, QueueTask] = {}
        self.results: Dict[str, QueueTask] = {}
        self.lock = threading.Lock()
        self.running = True
        self.worker_tasks = []
        logger.info(f"Request queue service initialized with max {max_concurrent} concurrent tasks")

    async def start_workers(self):
        """Start worker tasks to process queue"""
        for i in range(self.max_concurrent):
            worker_task = asyncio.create_task(self._worker(f"worker-{i}"))
            self.worker_tasks.append(worker_task)
        logger.info(f"Started {self.max_concurrent} worker tasks")

    async def stop_workers(self):
        """Stop all worker tasks"""
        self.running = False
        for task in self.worker_tasks:
            if not task.done():
                task.cancel()
        # Wait for all tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        logger.info("Stopped all worker tasks")

    async def _worker(self, worker_id: str):
        """Worker task to process items from the queue"""
        logger.info(f"Worker {worker_id} started")
        while self.running:
            try:
                # Wait for a task from the queue with a timeout
                task_id = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)

                # Get the task from active tasks
                if task_id in self.active_tasks:
                    queue_task = self.active_tasks[task_id]

                    # Update task status
                    with self.lock:
                        queue_task.status = TaskStatus.PROCESSING
                        queue_task.started_at = datetime.now()

                    logger.debug(f"Worker {worker_id} processing task {task_id}")

                    # Process the task based on its type
                    try:
                        result = await self._process_task(queue_task)
                        with self.lock:
                            queue_task.result = result
                            queue_task.status = TaskStatus.COMPLETED
                            queue_task.completed_at = datetime.now()
                    except Exception as e:
                        logger.error(f"Error processing task {task_id}: {e}")
                        with self.lock:
                            queue_task.error = str(e)
                            queue_task.status = TaskStatus.FAILED
                            queue_task.completed_at = datetime.now()

                    # Remove from active tasks and add to results
                    with self.lock:
                        del self.active_tasks[task_id]
                        self.results[task_id] = queue_task

                    # Mark task as done
                    self.task_queue.task_done()

                    logger.debug(f"Worker {worker_id} completed task {task_id}")
                else:
                    # Task was removed, just mark as done
                    self.task_queue.task_done()
            except asyncio.TimeoutError:
                # Continue the loop if no task is available
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                continue

    async def _process_task(self, queue_task: QueueTask) -> Any:
        """Process a specific task based on its type"""
        if queue_task.task_type == "ai_query":
            # Import here to avoid circular imports
            from src.services.ai_service import ai_service
            from src.services.rag_service import rag_service

            query = queue_task.payload.get("query")
            context = queue_task.payload.get("context", [])
            user_id = queue_task.payload.get("user_id")

            # Get context from RAG if not provided
            if not context:
                question = queue_task.payload.get("question")
                context = await rag_service.retrieve_context(question)

            # Generate response using AI service
            response = ai_service.generate_response(query, context, user_id)
            return response
        else:
            raise ValueError(f"Unknown task type: {queue_task.task_type}")

    async def submit_task(self, task_type: str, payload: Dict[str, Any]) -> str:
        """Submit a task to the queue"""
        import uuid
        task_id = str(uuid.uuid4())

        queue_task = QueueTask(
            id=task_id,
            task_type=task_type,
            payload=payload
        )

        with self.lock:
            self.active_tasks[task_id] = queue_task

        await self.task_queue.put(task_id)
        logger.info(f"Submitted task {task_id} of type {task_type} to queue")

        return task_id

    def get_task_status(self, task_id: str) -> Optional[QueueTask]:
        """Get the status of a specific task"""
        with self.lock:
            if task_id in self.active_tasks:
                return self.active_tasks[task_id]
            elif task_id in self.results:
                return self.results[task_id]
            else:
                return None

    def get_queue_size(self) -> int:
        """Get the current size of the task queue"""
        return self.task_queue.qsize()

    def cleanup_old_results(self, max_age_minutes: int = 60):
        """Clean up old completed/failed results to free memory"""
        cutoff_time = datetime.now()
        cutoff_time.replace(minute=cutoff_time.minute - max_age_minutes)

        with self.lock:
            old_results = []
            for task_id, task in self.results.items():
                if task.completed_at and task.completed_at < cutoff_time:
                    old_results.append(task_id)

            for task_id in old_results:
                del self.results[task_id]

        logger.info(f"Cleaned up {len(old_results)} old results")


# Global instance
queue_service = RequestQueueService()