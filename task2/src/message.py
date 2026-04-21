import json
import time


def make_message(seq: int, size: int) -> bytes:
    base = {"s": seq, "t": time.time(), "p": ""}
    raw = json.dumps(base, separators=(",", ":")).encode()
    pad = max(0, size - len(raw))
    base["p"] = "x" * pad
    return json.dumps(base, separators=(",", ":")).encode()


def parse_message(data: bytes) -> tuple[int, float]:
    obj = json.loads(data)
    return int(obj["s"]), float(obj["t"])
