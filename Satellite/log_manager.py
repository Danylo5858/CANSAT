from queue import Queue

log_queue = Queue()

def logger():
    while True:
        msg = log_queue.get()
        print(msg)
