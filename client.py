import socket
import sys
import threading
from queue import Queue
from time import time

from parser_tool import createParserClient, parse_file

TCP_IP = '127.0.0.1'
TCP_PORT = 15000


def master():
    parser = createParserClient()
    params = parser.parse_args(sys.argv[1:])
    n_workers = int(params.worker)
    url_file_name = params.file
    urls = parse_file(url_file_name)
    queue = Queue()
    t1 = time()

    for url in urls:
        queue.put(url)

    workers_pool = [Worker(queue, i) for i in range(n_workers)]

    for worker in workers_pool:
        worker.start()

    for worker in workers_pool:
        worker.join()
    print(f'Time = {time() - t1}')


class Worker(threading.Thread):
    def __init__(self, queue, worker_num):
        threading.Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((TCP_IP, TCP_PORT))
        self.queue = queue
        self.worker_num = worker_num

    def run(self):
        while True:
            if self.queue.empty():
                break
            url = self.queue.get()
            self.socket.send(url.encode())
            response = self.socket.recv(4096).decode()
            print(f'Worker {self.worker_num} sent {url}, received {response}')


if __name__ == '__main__':
    master()
