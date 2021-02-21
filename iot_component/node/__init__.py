# Insert Collector Codes and insertion to AWS

def node(termlock, config):
    refreshrate = 30

    while True:
        # Wait for termination command
        if termlock.acquire(timeout=refreshrate):
            break

