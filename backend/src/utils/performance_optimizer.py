"""
Performance Optimization Utilities
This module provides utilities for performance monitoring and optimization.
"""
import time
import asyncio
import functools
from typing import Dict, List, Callable, Any
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
import psutil
import gc
from src.utils.logging import get_logger


logger = get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """Data class to hold performance metrics"""
    execution_time: float
    memory_usage_before: float
    memory_usage_after: float
    cpu_percent: float
    timestamp: datetime


class PerformanceOptimizer:
    """Performance optimization and monitoring utilities"""

    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.function_performance: Dict[str, List[float]] = {}
        logger.info("Performance optimizer initialized")

    @contextmanager
    def performance_monitor(self, operation_name: str = "operation"):
        """
        Context manager to monitor performance of code blocks
        """
        # Get initial metrics
        start_time = time.perf_counter()
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        cpu_percent = psutil.cpu_percent()

        try:
            yield
        finally:
            # Get final metrics
            end_time = time.perf_counter()
            memory_after = process.memory_info().rss / 1024 / 1024  # MB

            execution_time = end_time - start_time

            # Store metrics
            metric = PerformanceMetrics(
                execution_time=execution_time,
                memory_usage_before=memory_before,
                memory_usage_after=memory_after,
                cpu_percent=cpu_percent,
                timestamp=datetime.now()
            )

            self.metrics.append(metric)

            # Store function-specific metrics
            if operation_name not in self.function_performance:
                self.function_performance[operation_name] = []
            self.function_performance[operation_name].append(execution_time)

            # Log performance metrics
            logger.info(
                f"Performance: {operation_name} executed in {execution_time:.4f}s",
                extra_data={
                    "execution_time": execution_time,
                    "memory_before_mb": memory_before,
                    "memory_after_mb": memory_after,
                    "cpu_percent": cpu_percent
                }
            )

    def performance_decorator(self, name: str = None):
        """
        Decorator to monitor function performance
        """
        def decorator(func: Callable) -> Callable:
            func_name = name or f"{func.__module__}.{func.__name__}"

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                with self.performance_monitor(func_name):
                    return await func(*args, **kwargs)

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                with self.performance_monitor(func_name):
                    return func(*args, **kwargs)

            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate a performance report
        """
        if not self.metrics:
            return {"message": "No performance metrics collected yet"}

        total_exec_time = sum(m.execution_time for m in self.metrics)
        avg_exec_time = total_exec_time / len(self.metrics)

        total_memory_change = sum(m.memory_usage_after - m.memory_usage_before for m in self.metrics)
        avg_memory_change = total_memory_change / len(self.metrics)

        avg_cpu = sum(m.cpu_percent for m in self.metrics) / len(self.metrics)

        # Calculate function-specific stats
        function_stats = {}
        for func_name, times in self.function_performance.items():
            function_stats[func_name] = {
                "call_count": len(times),
                "total_time": sum(times),
                "avg_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times)
            }

        return {
            "total_operations": len(self.metrics),
            "total_execution_time": total_exec_time,
            "average_execution_time": avg_exec_time,
            "total_memory_change": total_memory_change,
            "average_memory_change": avg_memory_change,
            "average_cpu_usage": avg_cpu,
            "function_stats": function_stats,
            "timestamp": datetime.now().isoformat()
        }

    def optimize_memory(self):
        """
        Perform memory optimization tasks
        """
        # Force garbage collection
        collected = gc.collect()
        logger.info(f"Memory optimization: collected {collected} objects")

        # Clear old metrics if they exceed a threshold
        if len(self.metrics) > 1000:  # Keep only last 1000 metrics
            self.metrics = self.metrics[-500:]
            logger.info("Cleared old performance metrics to save memory")

    def get_suggestions(self) -> List[str]:
        """
        Get performance optimization suggestions based on collected metrics
        """
        suggestions = []

        if not self.metrics:
            return suggestions

        # Check for slow functions
        for func_name, times in self.function_performance.items():
            avg_time = sum(times) / len(times)
            if avg_time > 1.0:  # Functions taking more than 1 second on average
                suggestions.append(f"Optimize function {func_name}: avg execution time {avg_time:.2f}s")

        # Check for memory growth
        if len(self.metrics) >= 2:
            memory_changes = [m.memory_usage_after - m.memory_usage_before for m in self.metrics[-10:]]
            avg_growth = sum(memory_changes) / len(memory_changes)
            if avg_growth > 10:  # Growing by more than 10MB per operation
                suggestions.append(f"Memory leak detected: avg growth {avg_growth:.2f}MB per operation")

        # Check for high CPU usage
        avg_cpu = sum(m.cpu_percent for m in self.metrics[-10:]) / min(10, len(self.metrics))
        if avg_cpu > 80:  # High CPU usage
            suggestions.append(f"High CPU usage detected: avg {avg_cpu:.2f}%")

        return suggestions


# Global instance
performance_optimizer = PerformanceOptimizer()


def performance_check():
    """
    Function to perform a performance check and return results
    """
    report = performance_optimizer.get_performance_report()
    suggestions = performance_optimizer.get_suggestions()

    result = {
        "report": report,
        "suggestions": suggestions
    }

    logger.info(
        "Performance check completed",
        extra_data={"report_summary": {
            "total_operations": report.get("total_operations", 0),
            "average_execution_time": report.get("average_execution_time", 0),
            "suggestions_count": len(suggestions)
        }}
    )

    return result


# Example usage decorators for key functions in the application
def optimize_content_service():
    """
    Apply performance optimizations to content service functions
    """
    # This would be used to wrap key functions in content_service.py
    pass


def optimize_database_queries():
    """
    Apply performance optimizations to database queries
    """
    # This would include query optimization techniques
    pass


def optimize_embedding_service():
    """
    Apply performance optimizations to embedding service
    """
    # This would include techniques for optimizing embeddings
    pass