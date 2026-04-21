# lab3_etcd.py (pip install etcd3)
import os
import threading
import time

# Workaround for etcd3 generated protobuf stubs with newer protobuf runtime.
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

import etcd3
from etcd3.exceptions import ConnectionFailedError


def watch_key(events_iterator, cancel, stop_event, key):
	"""Watch sebuah key dan print setiap perubahan."""
	print(f"Watching key: {key}")
	try:
		for event in events_iterator:
			if stop_event.is_set():
				break
			event_key = (
				event.key.decode() if isinstance(event.key, (bytes, bytearray)) else str(event.key)
			)
			event_value = (
				event.value.decode() if isinstance(event.value, (bytes, bytearray)) else event.value
			)
			print(
				f"Event: {type(event).__name__} | "
				f"key={event_key} | "
				f"value={event_value if event_value is not None else 'deleted'}"
			)
	except Exception as exc:
		if not stop_event.is_set():
			print(f"Watcher error: {exc}")
	finally:
		cancel()


def main():
	etcd = etcd3.client(host="localhost", port=2379)
	key = "/config/threshold"

	try:
		etcd.status()
	except ConnectionFailedError:
		print("Tidak bisa terhubung ke etcd di localhost:2379.")
		print("Jalankan etcd dulu, contoh:")
		print(
			"docker run -d --name etcd -p 2379:2379 -p 2380:2380 "
			"quay.io/coreos/etcd:v3.5.12 "
			"/usr/local/bin/etcd --name s1 --data-dir /etcd-data "
			"--advertise-client-urls http://0.0.0.0:2379 "
			"--listen-client-urls http://0.0.0.0:2379 "
			"--initial-advertise-peer-urls http://0.0.0.0:2380 "
			"--listen-peer-urls http://0.0.0.0:2380 "
			"--initial-cluster s1=http://0.0.0.0:2380 "
			"--initial-cluster-token tkn --initial-cluster-state new"
		)
		return

	events_iterator, cancel_watch = etcd.watch(key)
	stop_event = threading.Event()
	watcher_thread = threading.Thread(
		target=watch_key,
		args=(events_iterator, cancel_watch, stop_event, key),
		daemon=False,
	)
	watcher_thread.start()

	try:
		# Simulate config updates
		time.sleep(0.5)
		for i in range(5):
			value = f"threshold={80 + i}"
			etcd.put(key, value)
			print(f"Updated: {value}")
			time.sleep(1)

		# Leader election using etcd
		print("\n--- Leader Election ---")
		# etcd3 python client does not expose Election; use a distributed lock for election.
		lock = etcd.lock("election-my-service", ttl=10)
		print("Trying to become leader...")
		if lock.acquire(timeout=5):
			try:
				print("I am the leader!")
				time.sleep(3)
			finally:
				lock.release()
				print("Leadership released.")
		else:
			print("Failed to acquire leadership lock.")
	except ConnectionFailedError:
		print("Koneksi ke etcd terputus saat proses berjalan.")
	finally:
		stop_event.set()
		cancel_watch()
		watcher_thread.join(timeout=2)


if __name__ == "__main__":
	main()