import bisect
import math
import threading


class Metrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.sent = 0
        self.received = 0
        self.send_errors = 0
        self.recv_errors = 0
        self._latencies: list[float] = []

    def add_latency(self, latency_s: float) -> None:
        with self._lock:
            self._latencies.append(latency_s)

    def snapshot(self) -> dict:
        with self._lock:
            lat = sorted(self._latencies)
        n = len(lat)
        if n == 0:
            return {
                "sent": self.sent,
                "received": self.received,
                "send_errors": self.send_errors,
                "recv_errors": self.recv_errors,
                "avg_latency_ms": 0.0,
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "p99_latency_ms": 0.0,
                "max_latency_ms": 0.0,
            }
        avg = sum(lat) / n

        def pct(p: float) -> float:
            idx = min(n - 1, max(0, math.ceil(p * n) - 1))
            return lat[idx] * 1000.0

        return {
            "sent": self.sent,
            "received": self.received,
            "send_errors": self.send_errors,
            "recv_errors": self.recv_errors,
            "avg_latency_ms": avg * 1000.0,
            "p50_latency_ms": pct(0.50),
            "p95_latency_ms": pct(0.95),
            "p99_latency_ms": pct(0.99),
            "max_latency_ms": lat[-1] * 1000.0,
        }
