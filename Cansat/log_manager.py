from queue import Queue

log_queue = Queue()
print("LOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOG INIT")

def logger():
    while True:
        msg = log_queue.get()
        print(msg)
