# Insert Collector Codes and insertion to AWS

def node(termlock, config):
    try:
        refreshrate = 30
        print(config["HOST"])
        print(config["TELEBOT"])
        while True:
            # Code here

            # Wait for termination command
            if termlock.acquire(timeout=refreshrate):
                break

    except Exception as e:
        termlock.release()
        print("exception raised in Node")
        print(e)
    except KeyboardInterrupt:
        print("Term")
        pass