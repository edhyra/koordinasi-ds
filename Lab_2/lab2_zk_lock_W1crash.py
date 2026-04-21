# lab2_zk_lock_W1crash.py
from kazoo.client import KazooClient
from kazoo.recipe.lock import Lock
import threading, time

def worker(worker_id):
    zk = KazooClient(hosts='localhost:2181')
    zk.start()
    lock = Lock(zk, "/myapp/lock")
    print(f"[Worker-{worker_id}] Mencoba acquire lock...")
    try:
        with lock:
            print(f"[Worker-{worker_id}] Lock diperoleh! Masuk CR.")
            if worker_id == 1:
                print(f"[Worker-{worker_id}] CRASH!")
                raise Exception("Simulasi crash.")
            time.sleep(2)
            print(f"[Worker-{worker_id}] Selesai, release lock.")
    except Exception as e:
        print(f"[Worker-{worker_id}] Exception: {e}")
    zk.stop()

threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
for t in threads: t.start()
for t in threads: t.join()
print("Semua worker selesai!")
