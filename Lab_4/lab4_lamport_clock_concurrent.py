# lab4_lamport_clock_concurrent.py
class LamportClock:
	def __init__(self, pid):
		self.pid = pid
		self.time = 0

	def tick(self):
		self.time += 1
		return self.time

	def send(self):
		self.time += 1
		return self.time

	def receive(self, remote_ts):
		self.time = max(self.time, remote_ts) + 1
		return self.time


# Demo: dua event concurrent menurut vector clock sebelumnya
l1 = LamportClock("P1")
l2 = LamportClock("P2")
l3 = LamportClock("P3")

# P1 dan P3 sama-sama mengirim event pertama mereka secara independen
ts_l1 = l1.send()
ts_l3 = l3.send()

print("ts_l1:", ts_l1)
print("ts_l3:", ts_l3)
print("L1 < L3?", ts_l1 < ts_l3)
print("L3 < L1?", ts_l3 < ts_l1)

if ts_l1 == ts_l3:
	print("Lamport: timestamps equal — scalar timestamps cannot reliably show causality.")
elif ts_l1 < ts_l3:
	print("Lamport orders L1 before L3, but that ordering may NOT reflect causality (Lamport cannot detect concurrency).")
else:
	print("Lamport orders L3 before L1, but that ordering may NOT reflect causality (Lamport cannot detect concurrency).")

# Extra illustration: P2 receives ts_l1 then sends — now ordering with L1 is causal
l2.receive(ts_l1)
ts_l2 = l2.send()
print("\nAfter P2 receives from P1 and sends:")
print("ts_l2:", ts_l2)
print("L1 < L2?", ts_l1 < ts_l2)
print("Note: Lamport preserves causal ordering (if a->b then L(a)<L(b)), but the converse is false.")
