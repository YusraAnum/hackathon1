"""
Performance Testing Utilities
This module provides utilities for performance testing and monitoring.
"""
import time
import asyncio
import requests
import statistics
from typing import List, Dict, Callable, Any
from contextlib import contextmanager
from src.utils.logging import get_logger


logger = get_logger(__name__)


class PerformanceTester:
    """
    Utility class for performance testing of API endpoints
    """
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []

    @contextmanager
    def timer(self):
        """
        Context manager to time code execution
        """
        start_time = time.time()
        yield
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        logger.debug(f"Execution time: {execution_time:.2f}ms")
        return execution_time

    async def test_endpoint_performance(self, endpoint: str, method: str = "GET",
                                     payload: Dict = None, num_requests: int = 10) -> Dict[str, Any]:
        """
        Test the performance of a specific endpoint

        Args:
            endpoint: API endpoint to test (e.g., "/api/textbook/chapters")
            method: HTTP method (GET, POST, etc.)
            payload: Request payload for POST/PUT requests
            num_requests: Number of requests to make for the test

        Returns:
            Dictionary containing performance metrics
        """
        response_times = []
        errors = 0

        logger.info(f"Testing performance of {method} {endpoint} with {num_requests} requests...")

        for i in range(num_requests):
            try:
                start_time = time.time()

                if method.upper() == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}")
                elif method.upper() == "POST":
                    response = requests.post(f"{self.base_url}{endpoint}", json=payload)
                elif method.upper() == "PUT":
                    response = requests.put(f"{self.base_url}{endpoint}", json=payload)
                elif method.upper() == "DELETE":
                    response = requests.delete(f"{self.base_url}{endpoint}")
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                response_times.append(response_time)

                if response.status_code >= 400:
                    errors += 1
                    logger.warning(f"Request {i+1} failed with status {response.status_code}")

            except Exception as e:
                errors += 1
                logger.error(f"Request {i+1} failed with error: {e}")

            # Small delay between requests to avoid overwhelming the server
            await asyncio.sleep(0.1)

        # Calculate metrics
        if response_times:
            metrics = {
                "endpoint": endpoint,
                "method": method,
                "total_requests": num_requests,
                "successful_requests": num_requests - errors,
                "failed_requests": errors,
                "error_rate": errors / num_requests if num_requests > 0 else 0,
                "response_times_ms": response_times,
                "avg_response_time_ms": statistics.mean(response_times),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times),
                "p50_response_time_ms": self._percentile(response_times, 50),
                "p90_response_time_ms": self._percentile(response_times, 90),
                "p95_response_time_ms": self._percentile(response_times, 95),
                "p99_response_time_ms": self._percentile(response_times, 99)
            }
        else:
            metrics = {
                "endpoint": endpoint,
                "method": method,
                "total_requests": num_requests,
                "successful_requests": 0,
                "failed_requests": num_requests,
                "error_rate": 1.0,
                "response_times_ms": [],
                "avg_response_time_ms": 0,
                "min_response_time_ms": 0,
                "max_response_time_ms": 0,
                "p50_response_time_ms": 0,
                "p90_response_time_ms": 0,
                "p95_response_time_ms": 0,
                "p99_response_time_ms": 0
            }

        self.test_results.append(metrics)
        logger.info(f"Performance test completed for {endpoint}")
        return metrics

    def _percentile(self, data: List[float], percentile: float) -> float:
        """
        Calculate percentile of a list of values
        """
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[min(int(index) + 1, len(sorted_data) - 1)]
            fraction = index - int(index)
            return lower + fraction * (upper - lower)

    def run_comprehensive_performance_test(self) -> Dict[str, Any]:
        """
        Run comprehensive performance tests on key endpoints
        """
        logger.info("Starting comprehensive performance tests...")

        # Define key endpoints to test
        endpoints_to_test = [
            {"endpoint": "/api/textbook/chapters", "method": "GET"},
            {"endpoint": "/api/textbook/chapters/1", "method": "GET"},
            {"endpoint": "/api/ai/validate", "method": "POST", "payload": {"question": "What is Physical AI?", "context": "test context"}},
            {"endpoint": "/health", "method": "GET"}
        ]

        results = {
            "timestamp": time.time(),
            "base_url": self.base_url,
            "tests": []
        }

        for endpoint_config in endpoints_to_test:
            endpoint = endpoint_config["endpoint"]
            method = endpoint_config["method"]
            payload = endpoint_config.get("payload", None)

            # Run test with 5 requests for each endpoint
            test_result = asyncio.run(
                self.test_endpoint_performance(endpoint, method, payload, num_requests=5)
            )
            results["tests"].append(test_result)

        logger.info("Comprehensive performance tests completed")
        return results

    def generate_performance_report(self) -> str:
        """
        Generate a performance report from collected test results
        """
        if not self.test_results:
            return "No performance test results available."

        report_lines = [
            "Performance Test Report",
            "=" * 50
        ]

        for test_result in self.test_results:
            report_lines.extend([
                f"Endpoint: {test_result['endpoint']} ({test_result['method']})",
                f"  Total Requests: {test_result['total_requests']}",
                f"  Successful: {test_result['successful_requests']}",
                f"  Failed: {test_result['failed_requests']}",
                f"  Error Rate: {test_result['error_rate']:.2%}",
                f"  Avg Response Time: {test_result['avg_response_time_ms']:.2f}ms",
                f"  Min Response Time: {test_result['min_response_time_ms']:.2f}ms",
                f"  Max Response Time: {test_result['max_response_time_ms']:.2f}ms",
                f"  P95 Response Time: {test_result['p95_response_time_ms']:.2f}ms",
                f"  P99 Response Time: {test_result['p99_response_time_ms']:.2f}ms",
                ""
            ])

        return "\n".join(report_lines)


# Example usage function
async def run_performance_tests():
    """
    Run example performance tests
    """
    tester = PerformanceTester()
    results = tester.run_comprehensive_performance_test()

    report = tester.generate_performance_report()
    print(report)

    return results


if __name__ == "__main__":
    # This would typically be run as a separate script or as part of a CI/CD pipeline
    asyncio.run(run_performance_tests())