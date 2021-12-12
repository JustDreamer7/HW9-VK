import socket
import sys
import threading
from collections import Counter
from queue import Queue
from select import select
import re
import requests

from parser_tool import createParserServer

regular_expr = r'\w+'
reg_expr_compiled = re.compile(regular_expr)
SYMBOLS_TO_REMOVE = list(r"1234567890=+*|[](){}.,:;-!?$%#&<>/\"'" + '\n')

LOCK = threading.Lock()
urls_fetched = 0

to_monitor = []

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.bind(('localhost', 15000))
server_sock.listen()
print('Listening on http://127.0.0.1:15000')


def accept_conn(server_sock):
    client_sock, addr = server_sock.accept()
    print('Connect', addr)
    to_monitor.append(client_sock)


def finder_top_k_words(url, k):
    data = requests.get(url)
    words = []
    for line in data:
        line = line.decode()
        for item in SYMBOLS_TO_REMOVE:
            line = line.replace(item, '')
        # print(line)
        line = line.lower()
        text_by_words = reg_expr_compiled.findall(line)
        words.extend(text_by_words)

    count = Counter(words)
    top_words = [[word, num] for word, num in sorted(count.items(), key=lambda x: x[1], reverse=True)][:k]
    top_words = dict(top_words)

    return top_words


def master():
    queue = Queue()
    parser = createParserServer()
    params = parser.parse_args(sys.argv[1:])
    print(params)
    n_workers = int(params.worker)
    k_top = int(params.k)
    global urls_fetched
    workers_pool = [threading.Thread(target=fetch, args=(queue, k_top, i)) for i in range(n_workers)]

    for worker in workers_pool:
        worker.start()

    while True:
        to_read, _, _ = select(to_monitor, [], [])
        for sock in to_read:
            if sock is server_sock:
                accept_conn(sock)
            else:
                url = sock.recv(4096).decode()
                if url:
                    queue.put((url, sock))
                else:
                    sock.close()
                    to_monitor.remove(sock)


def fetch(queue, k_top, worker_num):
    while True:
        url, sock = queue.get()
        try:
            response = finder_top_k_words(url, k_top)
            print(f'Worker {worker_num} received url {worker_num}, response {response}')
            sock.send(str(response).encode())

            with LOCK:
                global urls_fetched
                urls_fetched += 1
                print(f'URLs fetched: {urls_fetched}')
        except (ValueError, OSError) as e:
            break


if __name__ == '__main__':
    to_monitor.append(server_sock)
    master()
