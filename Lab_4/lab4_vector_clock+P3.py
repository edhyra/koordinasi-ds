# lab4_vector_clock+P3.py
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
		self.clock[self.pid] += 1  # increment setelah merge

	def happens_before(self, ts_a, ts_b) -> bool:
		"""Return True jika ts_a causally precedes ts_b."""
		leq = all(ts_a[p] <= ts_b[p] for p in ts_a)
		lt = any(ts_a[p] < ts_b[p] for p in ts_a)
		return leq and lt

	def concurrent(self, ts_a, ts_b) -> bool:
		return (not self.happens_before(ts_a, ts_b) and
				not self.happens_before(ts_b, ts_a))


# Demo: P2 dan P3 kirim pesan ke P1 secara bersamaan
pids = ["P1", "P2", "P3"]
vc1 = VectorClock("P1", pids)
vc2 = VectorClock("P2", pids)
vc3 = VectorClock("P3", pids)

# Dua event send yang saling independent (concurrent)
ts_p2 = vc2.send()  # P2 -> P1
ts_p3 = vc3.send()  # P3 -> P1 (bersamaan dengan P2)

print("ts_p2:", ts_p2)
print("ts_p3:", ts_p3)
print("p2 -> p3?", vc1.happens_before(ts_p2, ts_p3))
print("p3 -> p2?", vc1.happens_before(ts_p3, ts_p2))
print("concurrent (p2, p3)?", vc1.concurrent(ts_p2, ts_p3))  # True

# P1 menerima kedua pesan (urutan terima bisa berbeda)
vc1.receive(ts_p2)
vc1.receive(ts_p3)

ts_p1 = vc1.send()  # Setelah merge, P1 mengirim event baru
print("\nts_p1 setelah menerima dari P2 & P3:", ts_p1)
print("p2 -> p1?", vc1.happens_before(ts_p2, ts_p1))  # True
print("p3 -> p1?", vc1.happens_before(ts_p3, ts_p1))  # True
