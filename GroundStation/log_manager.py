from queue import Queue

log_queue = Queue()

def logger():
    try:
        while True:
            msg = log_queue.get()
            print(msg)
    except KeyboardInterrupt:
        return
