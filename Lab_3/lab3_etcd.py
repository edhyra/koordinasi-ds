# lab3_etcd.py (pip install etcd3)
import etcd3, threading, time ## error tidak bisa import etcd3

def watch_key(etcd, key):
	"""Watch sebuah key dan print setiap perubahan."""
	print(f"Watching key: {key}")
	events_iterator, cancel = etcd.watch(key)
	for event in events_iterator:
		print(f" Event: {type(event).__name__} | "
			  f"key={event.key.decode()} | "
			  f"value={event.value.decode() if event.value else 'deleted'}")

etcd = etcd3.client(host='localhost', port=2379)

# Start watcher in background
watcher_thread = threading.Thread(
	target=watch_key, args=(etcd, b'/config/threshold'), daemon=True
)
watcher_thread.start()

# Simulate config updates
time.sleep(0.5)
for i in range(5):
	value = f"threshold={80 + i}"
	etcd.put('/config/threshold', value)
	print(f"Updated: {value}")
	time.sleep(1)
	
# Leader election using etcd
print("\n--- Leader Election ---")
election = etcd3.Election(etcd, "my-service") ## error .Election tidak ada di etcd
election.campaign("node-1") # blocks until leader
print("I am the leader!")
