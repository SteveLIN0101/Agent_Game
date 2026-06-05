"""Task scheduler — distributes tasks across workers."""


def schedule_tasks(n: int) -> list[int]:
    """Schedule n tasks and return their assigned worker IDs (0-indexed).

    BUG: range(0, n) only generates n-1 tasks, not n.
    """
    workers = [0, 1, 2, 3]  # 4 workers, round-robin
    tasks = []
    for i in range(0, n):  # BUG: should be range(1, n+1) or range(n)
        worker = workers[i % len(workers)]
        tasks.append(worker)
    return tasks


def get_worker_loads(n: int) -> dict[int, int]:
    """Return number of tasks assigned to each worker."""
    assignments = schedule_tasks(n)
    loads = {}
    for w in assignments:
        loads[w] = loads.get(w, 0) + 1
    return loads
