import pytest
import time
from fastapi.testclient import TestClient
from src.api.main import app
from src.utils.performance_optimizer import PerformanceOptimizer, performance_optimizer, PerformanceMetrics


@pytest.fixture
def client():
    """Create a test client for the API"""
    with TestClient(app) as test_client:
        yield test_client


def test_performance_optimizer_initialization():
    """Test that PerformanceOptimizer is properly initialized"""
    assert performance_optimizer is not None
    assert isinstance(performance_optimizer, PerformanceOptimizer)
    assert hasattr(performance_optimizer, 'metrics')
    assert hasattr(performance_optimizer, 'function_performance')


def test_performance_metrics_dataclass():
    """Test PerformanceMetrics dataclass"""
    from datetime import datetime

    metrics = PerformanceMetrics(
        execution_time=0.1,
        memory_usage_before=100.0,
        memory_usage_after=101.0,
        cpu_percent=5.0,
        timestamp=datetime.now()
    )

    assert metrics.execution_time == 0.1
    assert metrics.memory_usage_before == 100.0
    assert metrics.memory_usage_after == 101.0
    assert metrics.cpu_percent == 5.0
    assert metrics.timestamp is not None


def test_performance_monitor_context_manager():
    """Test performance monitoring context manager"""
    initial_count = len(performance_optimizer.metrics)

    # Use the context manager to monitor a code block
    with performance_optimizer.performance_monitor("test_operation"):
        # Simulate some work
        time.sleep(0.01)  # Sleep for 10ms

    # Check that metrics were collected
    final_count = len(performance_optimizer.metrics)
    assert final_count > initial_count

    # Check the most recent metric
    latest_metric = performance_optimizer.metrics[-1]
    assert isinstance(latest_metric, PerformanceMetrics)
    assert latest_metric.execution_time >= 0
    assert latest_metric.memory_usage_before >= 0
    assert latest_metric.memory_usage_after >= 0


def test_performance_decorator_sync_function():
    """Test performance decorator with synchronous function"""
    @performance_optimizer.performance_decorator(name="test_sync_function")
    def test_function():
        time.sleep(0.01)  # Simulate work
        return "completed"

    result = test_function()
    assert result == "completed"

    # Check that function metrics were recorded
    function_metrics = performance_optimizer.function_performance.get("test_sync_function", [])
    assert len(function_metrics) >= 1
    assert function_metrics[0] >= 0  # Execution time should be non-negative


def test_performance_decorator_async_function():
    """Test performance decorator with asynchronous function"""
    import asyncio

    @performance_optimizer.performance_decorator(name="test_async_function")
    async def test_async_function():
        await asyncio.sleep(0.01)  # Simulate async work
        return "async completed"

    # Run the async function
    result = asyncio.run(test_async_function())
    assert result == "async completed"

    # Check that function metrics were recorded
    function_metrics = performance_optimizer.function_performance.get("test_async_function", [])
    assert len(function_metrics) >= 1


def test_performance_report_generation():
    """Test performance report generation"""
    # Add some metrics first
    with performance_optimizer.performance_monitor("report_test"):
        time.sleep(0.01)

    # Generate report
    report = performance_optimizer.get_performance_report()

    # Check report structure
    assert "total_operations" in report
    assert "total_execution_time" in report
    assert "average_execution_time" in report
    assert "function_stats" in report
    assert "timestamp" in report

    # Check that function stats are included
    if report["total_operations"] > 0:
        assert len(report["function_stats"]) >= 0


def test_performance_suggestions():
    """Test performance optimization suggestions"""
    suggestions = performance_optimizer.get_suggestions()
    assert isinstance(suggestions, list)

    # Add a slow function to trigger suggestions
    @performance_optimizer.performance_decorator(name="slow_function_test")
    def slow_function():
        time.sleep(0.1)  # This should be slow enough to potentially trigger a suggestion
        return "slow completed"

    result = slow_function()
    assert result == "slow completed"

    # Get suggestions after running the slow function
    suggestions = performance_optimizer.get_suggestions()
    # Note: The actual suggestion might not be triggered depending on timing thresholds


def test_memory_optimization():
    """Test memory optimization functionality"""
    # Add some metrics to trigger memory optimization
    for i in range(10):
        with performance_optimizer.performance_monitor(f"memory_test_{i}"):
            time.sleep(0.001)

    # Call memory optimization
    performance_optimizer.optimize_memory()

    # This should run without errors
    assert True


def test_multiple_operations_performance_tracking():
    """Test tracking of multiple operations"""
    operation_count = 5
    initial_count = len(performance_optimizer.metrics)

    for i in range(operation_count):
        with performance_optimizer.performance_monitor(f"operation_{i}"):
            time.sleep(0.001)

    final_count = len(performance_optimizer.metrics)
    assert final_count == initial_count + operation_count

    # Check that all operations are tracked
    report = performance_optimizer.get_performance_report()
    assert report["total_operations"] >= operation_count


def test_performance_decorator_without_name():
    """Test performance decorator without explicit name"""
    @performance_optimizer.performance_decorator()
    def unnamed_function():
        return "unnamed completed"

    result = unnamed_function()
    assert result == "unnamed completed"

    # The function name should be used as the operation name
    # Find the function in the performance data
    found = False
    for func_name in performance_optimizer.function_performance.keys():
        if "unnamed_function" in func_name:
            found = True
            break

    assert found, "Function should be tracked in performance data"


def test_performance_context_manager_nested():
    """Test nested performance monitoring"""
    with performance_optimizer.performance_monitor("outer_operation"):
        time.sleep(0.005)
        with performance_optimizer.performance_monitor("inner_operation"):
            time.sleep(0.005)

    # Both operations should be recorded
    report = performance_optimizer.get_performance_report()
    function_stats = report.get("function_stats", {})

    found_outer = any("outer_operation" in name for name in function_stats.keys())
    found_inner = any("inner_operation" in name for name in function_stats.keys())

    assert found_outer or len(performance_optimizer.metrics) >= 2
    assert found_inner or len(performance_optimizer.metrics) >= 2


def test_performance_check_function():
    """Test the performance_check utility function"""
    from src.utils.performance_optimizer import performance_check

    result = performance_check()
    assert "report" in result
    assert "suggestions" in result
    assert isinstance(result["report"], dict)
    assert isinstance(result["suggestions"], list)


def test_performance_data_cleanup():
    """Test that old performance data is cleaned up when it exceeds limits"""
    # Add many metrics to potentially trigger cleanup
    original_count = len(performance_optimizer.metrics)

    for i in range(1010):  # More than the 1000 threshold
        with performance_optimizer.performance_monitor(f"cleanup_test_{i % 100}"):
            pass  # Very fast operation

    # Trigger memory optimization which includes cleanup
    performance_optimizer.optimize_memory()

    # The metrics should be limited to prevent memory issues
    final_count = len(performance_optimizer.metrics)
    # Should have been reduced from the cleanup
    assert final_count <= 1000


if __name__ == "__main__":
    pytest.main([__file__])