# lab3_etcd_new_modified.py (pip install etcd3)
import os
import threading
import time

os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

import etcd3
from etcd3.exceptions import ConnectionFailedError


def decode_value(value):
	if isinstance(value, (bytes, bytearray)):
		return value.decode()
	return value


def watch_key(events_iterator, cancel, stop_event, key, label):
	"""Watch sebuah key dan print setiap perubahan."""
	print(f"Watching key [{label}]: {key}")
	try:
		for event in events_iterator:
			if stop_event.is_set():
				break
			print(
				f"[{label}] Event: {type(event).__name__} | "
				f"key={decode_value(event.key)} | "
				f"value={decode_value(event.value) if event.value else 'deleted'}"
			)
	except Exception as exc:
		if not stop_event.is_set():
			print(f"Watcher [{label}] error: {exc}")
	finally:
		cancel()


def campaign_for_leadership(node_name, ready_event, result_lock, result_holder):
	client = etcd3.client(host="localhost", port=2379)
	lock = client.lock("election-my-service", ttl=10)
	ready_event.wait()
	print(f"[{node_name}] campaign dimulai")
	acquired = False
	try:
		acquired = lock.acquire(timeout=5)
	except Exception as exc:
		print(f"[{node_name}] gagal campaign: {exc}")
		return
	if acquired:
		try:
			with result_lock:
				if result_holder["winner"] is None:
					result_holder["winner"] = node_name
			print(f"[{node_name}] menang dan menjadi leader")
			time.sleep(2)
		finally:
			lock.release()
			print(f"[{node_name}] melepaskan leadership")
	else:
		print(f"[{node_name}] kalah pada round ini")


def main():
	etcd = etcd3.client(host="localhost", port=2379)

	try:
		etcd.status()
	except ConnectionFailedError:
		print("Tidak bisa terhubung ke etcd di localhost:2379.")
		print("Jalankan etcd dulu sebelum menjalankan script ini.")
		return

	print("--- Parallel Watchers ---")
	stop_event = threading.Event()
	watcher_threads = []
	for key, label in (("/config/threshold", "threshold"), ("/config/timeout", "timeout")):
		events_iterator, cancel_watch = etcd.watch(key)
		thread = threading.Thread(
			target=watch_key,
			args=(events_iterator, cancel_watch, stop_event, key, label),
			daemon=True,
		)
		thread.start()
		watcher_threads.append(thread)

	time.sleep(0.5)
	updates = (
		("/config/threshold", "threshold=80"),
		("/config/timeout", "timeout=30s"),
		("/config/threshold", "threshold=81"),
		("/config/timeout", "timeout=45s"),
	)
	for key, value in updates:
		etcd.put(key, value)
		print(f"Updated: {key} -> {value}")
		time.sleep(0.5)

	print("\n--- Leader Election 2 Node ---")
	ready_event = threading.Event()
	result_lock = threading.Lock()
	result_holder = {"winner": None}
	node_threads = [
		threading.Thread(
			target=campaign_for_leadership,
			args=("node-A", ready_event, result_lock, result_holder),
			daemon=False,
		),
		threading.Thread(
			target=campaign_for_leadership,
			args=("node-B", ready_event, result_lock, result_holder),
			daemon=False,
		),
	]
	for thread in node_threads:
		thread.start()

	time.sleep(0.2)
	ready_event.set()
	for thread in node_threads:
		thread.join()

	print("\n--- Hasil ---")
	print(f"Pemenang leader election: {result_holder['winner']}")
	print(
		"Catatan: pemenang bisa berubah antar eksekusi karena dua node "
		"mengirim request lock pada waktu yang sangat berdekatan."
	)

	stop_event.set()
	for thread in watcher_threads:
		thread.join(timeout=1)


if __name__ == "__main__":
	main()