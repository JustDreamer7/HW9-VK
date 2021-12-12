import argparse


def createParserServer():
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--worker', nargs='?', default=10)
    parser.add_argument('-k', nargs='?', default=1)

    return parser


def createParserClient():
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--worker', nargs='?', default=10)
    parser.add_argument('-f', '--file', nargs='?', default='urls.txt')

    return parser


def createParserFetcher():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', nargs='?', default=10)
    parser.add_argument('-f', '--filename', nargs='?', default='urls.txt')

    return  parser

def parse_file(filename):
    with open(filename, 'r') as f:
        urls = f.readlines()
    urls = [url.replace('\n', '') for url in urls]

    return urls
