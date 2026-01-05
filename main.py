from multiprocessing import Process, Manager, Event
from options import options
from the_hive import the_hive


if __name__ == "__main__":
    with Manager() as manager:
        state = manager.dict(counter=0, running=True, options_open=False)

        options_event = Event()
        p1 = Process(target=the_hive, args=(state, options_event))
        p2 = Process(target=options, args=(state, options_event))

        p1.start()
        p2.start()

        p1.join()
        p2.join()
