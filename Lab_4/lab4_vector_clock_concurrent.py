# lab4_vector_clock_concurrent.py
class VectorClock:
	def __init__(self, pid, all_pids):
		self.pid = pid
		self.clock = {p: 0 for p in all_pids}

	def tick(self):
		self.clock[self.pid] += 1
		return dict(self.clock)

	def send(self):
		self.clock[self.pid] += 1
		return dict(self.clock)

	def receive(self, remote_ts):
		for p in self.clock:
			self.clock[p] = max(self.clock[p], remote_ts[p])
		self.clock[self.pid] += 1

	def happens_before(self, ts_a, ts_b) -> bool:
		"""Return True jika ts_a causally precedes ts_b."""
		leq = all(ts_a[p] <= ts_b[p] for p in ts_a)
		lt = any(ts_a[p] < ts_b[p] for p in ts_a)
		return leq and lt

	def concurrent(self, ts_a, ts_b) -> bool:
		return (
			not self.happens_before(ts_a, ts_b)
			and not self.happens_before(ts_b, ts_a)
		)


# Demo concurrent: dua event terjadi tanpa saling mengetahui
pids = ["P1", "P2", "P3"]
vc1 = VectorClock("P1", pids)
vc3 = VectorClock("P3", pids)

# P1 dan P3 sama-sama mengirim event pertama mereka secara independen
ts_p1 = vc1.send()
ts_p3 = vc3.send()

print("ts_p1:", ts_p1)
print("ts_p3:", ts_p3)
print("P1 precedes P3?", vc1.happens_before(ts_p1, ts_p3))
print("P3 precedes P1?", vc1.happens_before(ts_p3, ts_p1))
print("concurrent?", vc1.concurrent(ts_p1, ts_p3))

# Verifikasi tambahan: setelah P2 menerima ts_p1, event berikutnya tidak lagi concurrent
vc2 = VectorClock("P2", pids)
vc2.receive(ts_p1)
ts_p2 = vc2.send()
print("\nts_p2:", ts_p2)
print("P1 precedes P2?", vc1.happens_before(ts_p1, ts_p2))
print("P1 concurrent dengan P2?", vc1.concurrent(ts_p1, ts_p2))
