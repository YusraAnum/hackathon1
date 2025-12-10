import time
import threading
from collections import defaultdict, deque
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.utils.logging import get_logger


logger = get_logger(__name__)


class MetricsService:
    """
    Service for collecting and monitoring performance metrics.
    """

    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.response_times = deque(maxlen=1000)  # Keep last 1000 response times
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'errors': 0,
            'total_time': 0,
            'avg_time': 0
        })
        self.lock = threading.Lock()
        logger.info("Metrics service initialized")

    def record_request(self, endpoint: str, response_time: float, is_error: bool = False):
        """Record a request with its response time and error status"""
        with self.lock:
            self.request_count += 1
            if is_error:
                self.error_count += 1

            self.response_times.append(response_time)

            # Update endpoint-specific stats
            self.endpoint_stats[endpoint]['count'] += 1
            if is_error:
                self.endpoint_stats[endpoint]['errors'] += 1
            self.endpoint_stats[endpoint]['total_time'] += response_time
            self.endpoint_stats[endpoint]['avg_time'] = (
                self.endpoint_stats[endpoint]['total_time'] /
                self.endpoint_stats[endpoint]['count']
            )

    def get_request_rate(self, window_minutes: int = 1) -> float:
        """Get requests per minute"""
        # This is a simplified version - in a real implementation, we'd track timestamps
        # For now, we'll return a placeholder based on the last 1000 entries
        with self.lock:
            if len(self.response_times) == 0:
                return 0
            # Calculate based on the time span of recorded requests
            return len(self.response_times) / (window_minutes)  # Simplified

    def get_error_rate(self) -> float:
        """Get error rate as percentage"""
        with self.lock:
            if self.request_count == 0:
                return 0
            return (self.error_count / self.request_count) * 100

    def get_avg_response_time(self) -> float:
        """Get average response time"""
        with self.lock:
            if len(self.response_times) == 0:
                return 0
            return sum(self.response_times) / len(self.response_times)

    def get_p95_response_time(self) -> float:
        """Get 95th percentile response time"""
        with self.lock:
            if len(self.response_times) == 0:
                return 0
            sorted_times = sorted(self.response_times)
            index = int(0.95 * len(sorted_times))
            if index >= len(sorted_times):
                index = len(sorted_times) - 1
            return sorted_times[index]

    def get_p99_response_time(self) -> float:
        """Get 99th percentile response time"""
        with self.lock:
            if len(self.response_times) == 0:
                return 0
            sorted_times = sorted(self.response_times)
            index = int(0.99 * len(sorted_times))
            if index >= len(sorted_times):
                index = len(sorted_times) - 1
            return sorted_times[index]

    def get_endpoint_stats(self, endpoint: str) -> Dict:
        """Get statistics for a specific endpoint"""
        with self.lock:
            return dict(self.endpoint_stats[endpoint])

    def get_all_metrics(self) -> Dict:
        """Get all collected metrics"""
        with self.lock:
            return {
                'total_requests': self.request_count,
                'total_errors': self.error_count,
                'error_rate_percent': self.get_error_rate(),
                'avg_response_time_ms': self.get_avg_response_time(),
                'p95_response_time_ms': self.get_p95_response_time(),
                'p99_response_time_ms': self.get_p99_response_time(),
                'requests_per_minute': self.get_request_rate(),
                'endpoint_stats': {k: dict(v) for k, v in self.endpoint_stats.items()}
            }

    def reset_metrics(self):
        """Reset all metrics"""
        with self.lock:
            self.request_count = 0
            self.error_count = 0
            self.response_times.clear()
            self.endpoint_stats.clear()
            logger.info("Metrics reset")


# Global instance
metrics_service = MetricsService()