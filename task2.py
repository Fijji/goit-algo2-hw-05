import json
import time
from collections.abc import Iterable
from typing import Set
import hyperloglog
from tabulate import tabulate

class HyperLogLog:
    def __init__(self, error_rate=0.01):
        self.hll = hyperloglog.HyperLogLog(error_rate)

    def add(self, value: str):
        self.hll.add(value)

    def count(self) -> int:
        return len(self.hll)

def parse_log_file(file_path: str) -> Iterable[str]:
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                log_entry = json.loads(line.strip())
                ip = log_entry.get("remote_addr")
                if ip:
                    yield ip
            except json.JSONDecodeError:
                continue

def exact_unique_ip_count(file_path: str) -> int:
    unique_ips: Set[str] = set(parse_log_file(file_path))
    return len(unique_ips)

def approximate_unique_ip_count(file_path: str) -> int:
    hll = HyperLogLog()
    for ip in parse_log_file(file_path):
        hll.add(ip)
    return hll.count()

def compare_methods(file_path: str):
    start_time = time.time()
    exact_count = exact_unique_ip_count(file_path)
    exact_time = time.time() - start_time

    start_time = time.time()
    approx_count = approximate_unique_ip_count(file_path)
    approx_time = time.time() - start_time

    results = [["Точний підрахунок", exact_count, exact_time],
               ["HyperLogLog", approx_count, approx_time]]

    print("Результати порівняння:")
    print(tabulate(results, headers=["Метод", "Унікальні елементи", "Час виконання (сек.)"], tablefmt="grid"))

if __name__ == "__main__":
    log_file = "lms-stage-access.log"
    compare_methods(log_file)
