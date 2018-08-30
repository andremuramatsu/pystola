import requests
import argparse
from tabulate import tabulate
from termcolor import colored
from tidylib import tidy_document
from html.parser import HTMLParser

class html_external_resource_parser(HTMLParser):

    def set_callback(self, callback):
        self.__clbk = callback

    def handle_starttag(self, tag, attr):
        if tag.lower() == 'img':
            self.__clbk(tag, attr)

def __dict_to_list(dic):
    lst = []
    for item in dic:
        lst.append([item, dic[item]])

    return lst

def __parse_external_tag(tag, attr):
    print(tag)
    print(attr)

def __parse_external(r):
    parser = html_external_resource_parser()
    parser.set_callback(__parse_external_tag)
    parser.feed(r.text)

def __parse_http_code(r):
    bgc = 'on_blue'
    fgc = 'white'
    if r.status_code != requests.codes.ok:
        bgc = 'on_red'

    return colored('HTTP CODE: %s' % r.status_code, fgc, bgc)

def __parse_html(body):
    return tidy_document(body)


def __run(args):
    payload = {}
    headers = {}
    timeout = 30
    r = requests.get(args.url, verify=False, params=payload, headers=headers, timeout=timeout)

    print(colored('URL: %s' % r.url, 'yellow'))
    print(__parse_http_code(r))

    if args.verbose is not None:
        if args.verbose > 0:
            print(colored('ENCODING: %s' % r.encoding, 'magenta'))
            print(colored('COOKIE: %s' % r.cookies, 'magenta'))
            print(colored(tabulate(__dict_to_list(r.headers)), 'magenta'))

        if args.verbose > 1:
            print(colored(r.text, 'cyan'))

    __parse_external(r)

    html_doc, html_err = __parse_html(r.text)
    if html_err is not None:
        print(colored(html_err, 'red'))




def main():
    argp = argparse.ArgumentParser(description='Command line arguments')
    argp.add_argument('-u', '--url', action='store', required=True, help='URL to test')
    argp.add_argument('-v', '--verbose', action='count', required=False, help='Increase verbose')
    args = argp.parse_args()

    __run(args)

if __name__ == '__main__':
    main()
