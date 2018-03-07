from multiprocessing import Process, Queue
import time

def f(q):
    print "sdfsdf"
    q.put([42, None, 'hello'])
    print "sdfssdfsdfsddf"
    q.put("sdf")

if __name__ == '__main__':
    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    time.sleep(1)
    print q.empty()

