# lab_zk_lock_zESN.py
from kazoo.client import KazooClient
import threading, time

LOCK_PATH = "/lock"

def worker(worker_id):
    zk = KazooClient(hosts='localhost:2181')
    zk.start()
    zk.ensure_path(LOCK_PATH)
    node = zk.create(f"{LOCK_PATH}/node-", ephemeral=True, sequence=True)
    if node is None:
        raise RuntimeError("Gagal membuat node lock")
    print(f"[Worker-{worker_id}] Node dibuat: {node}")

    while True:
        children = zk.get_children(LOCK_PATH) or []
        if not children:
            continue
        children.sort()
        my_node = node.split("/")[-1]
        if my_node == children[0]:
            print(f"[Worker-{worker_id}] Lock diperoleh! Masuk CR.")
            time.sleep(2)
            print(f"[Worker-{worker_id}] Selesai, release lock.")
            zk.delete(node)
            break
        else:
            idx = children.index(my_node)
            prev_node = children[idx - 1]
            event = threading.Event()

            def watch_node(_event):
                event.set()

            stat = zk.exists(f"{LOCK_PATH}/{prev_node}", watch=watch_node)
            if stat is None:
                event.set()
            event.wait()

    zk.stop()

threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
for t in threads: t.start()
for t in threads: t.join()
print("Semua worker selesai!")
