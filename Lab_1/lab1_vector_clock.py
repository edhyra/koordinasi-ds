# lab1_vector_clock.py
import threading, queue, time, random

class VCProcess(threading.Thread):
    def __init__(self, pid, all_pids, peers):
        super().__init__(daemon=True)
        self.pid = pid
        self.clock = {p: 0 for p in all_pids}
        self.inbox = queue.Queue()
        self.peers = peers  # dict: pid -> VCProcess

    def _tick(self):
        self.clock[self.pid] += 1

    def _merge(self, remote_ts):
        for p in self.clock:
            self.clock[p] = max(self.clock[p], remote_ts[p])
        self.clock[self.pid] += 1

    def local_event(self, name):
        self._tick()
        print(f" [{self.pid}|{dict(self.clock)}] EVENT '{name}'")

    def send(self, target_pid, message):
        self._tick()
        ts = dict(self.clock)
        print(f" [{self.pid}|{ts}] SEND '{message}' → {target_pid}")
        self.peers[target_pid].inbox.put((ts, self.pid, message))

    def receive(self):
        ts, sender, msg = self.inbox.get()
        self._merge(ts)
        print(f" [{self.pid}|{dict(self.clock)}] RECV '{msg}' ← {sender}")

    def run(self):
        time.sleep(random.uniform(0, 0.2))
        if self.pid == "P1":
            self.local_event("start")
            self.send("P2", "hello")
            self.receive()           # ack dari P2
        elif self.pid == "P2":
            self.receive()           # dari P1
            self.local_event("process")
            self.send("P1", "ack")
            self.send("P3", "data")
        elif self.pid == "P3":
            self.receive()           # dari P2
            self.local_event("done")

pids = ["P1", "P2", "P3"]
vc_processes = {}
for pid in pids:
    vc_processes[pid] = VCProcess(pid, pids, vc_processes)

print("=== Simulasi Vector Clock ===")
for p in vc_processes.values(): p.start()
for p in vc_processes.values(): p.join(timeout=3)
print("=== Selesai ===")
