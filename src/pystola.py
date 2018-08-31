import sys
import requests
import argparse
import url
from tabulate import tabulate
from termcolor import colored
from tidylib import tidy_document
from html.parser import HTMLParser

class pystola_html_parser(HTMLParser):

    def set_callback(self, callback):
        self.__clbk = callback

    def handle_starttag(self, tag, attr):
        self.__clbk(tag, attr)

class pystola():

    rid = 0
    nline = 0
    no_child_verbosity = True
    csrf_id = None
    verbosity_lv = 0
    base_url = None

    def __print(self, msg):
        for line in msg.splitlines():
            self.nline = self.nline + 1
            print('%05d%010d: %s' % (self.rid, self.nline, line))

    def __dict_to_list(self, dic):
        lst = []
        for item in dic:
            lst.append([item, dic[item]])

        return lst

    def __parse_tag_attr_vl(self, attrlst, attrnm):
        attr = list(filter(lambda x:attrnm in x, attrlst))
        attrvl = None
        if len(attr) > 0:
            attrvl = attr[0][1]
        return attrvl


    def __parse_tag(self, tag, attr):

        attrnm = None
        is_html = False

        if tag in ['frame', 'iframe']:
            is_html = True
            attrnm = 'target'

        elif tag in ['script']:
            attrnm = 'src'

        elif tag in ['link']:
            attrnm = 'href'

        elif tag in ['img']:
            attrnm = 'src'

        if attrnm is not None:
            attrvl = list(filter(lambda x:attrnm in x, attr))
            if len(attrvl) > 0:
                tgt = attrvl[0][1]
                if len(tgt) > 0:
                    self.__request(tgt, is_html)

    def __parse_external(self, r):
        parser = pystola_html_parser()
        parser.set_callback(self.__parse_tag)
        parser.feed(r.text)

    def __parse_http_code(self, r):
        bgc = 'on_blue'
        fgc = 'white'
        if r.status_code != requests.codes.ok:
            bgc = 'on_red'

        return colored('HTTP CODE: %s' % r.status_code, fgc, bgc)

    def __parse_html(self, body):
        return tidy_document(body)

    def __request(self, urldst, is_html = True):

        tmpu = url.parse(urldst)
        if not tmpu.absolute:
            urldst = '%s/%s' % (self.base_url, urldst)

        self.rid = self.rid + 1
        payload = {}
        headers = {}
        timeout = 30
        r = requests.get(urldst, verify=False, params=payload, headers=headers, timeout=timeout)

        self.__print(colored('URL: %s' % r.url, 'yellow'))
        self.__print(colored('Content-Type: %s' % r.headers['Content-Type'], 'yellow'))
        self.__print(self.__parse_http_code(r))

        if self.verbosity_lv is not None:
            if self.verbosity_lv > 0:
                self.__print(colored('ENCODING: %s' % r.encoding, 'magenta'))
                self.__print(colored('COOKIE: %s' % r.cookies, 'magenta'))
                self.__print(colored(tabulate(self.__dict_to_list(r.headers)), 'magenta'))

            if self.verbosity_lv > 1:
                self.__print(colored(r.text, 'cyan'))

        if is_html:
            html_doc, html_err = self.__parse_html(r.text)
            if html_err is not None:
                self.__print(colored(html_err, 'red'))
            self.__parse_external(r)

    def run(self, args):
        self.verbosity_lv = args.verbose
        self.no_child_verbosity = args.no_child_verbosity
        self.csrf_id = args.csrf_token_id

        tmpu = args.url
        tmpp = url.parse(args.url)
        if len(str(tmpp.path)) > 0:
            tmpu = tmpu[:int(tmpu.find(str(tmpp.path)))]

        self.base_url = tmpu
        self.__request(args.url)


def main():
    argp = argparse.ArgumentParser(description='Command line arguments')
    argp.add_argument('-u', '--url', action='store', required=True, help='URL to test')
    argp.add_argument('-v', '--verbose', action='count', required=False, help='Increase verbose')
    argp.add_argument('--no-child-verbosity', action='count', required=False, help='Ignore verbose level to childs')
    argp.add_argument('--csrf-token-id', action='store', required=False, help='CSRF token input element id or name')
    argp.add_argument('--get-payload', action='store', required=False, help='JSON dictionary to GET query')
    argp.add_argument('--post-payload', action='store', required=False, help='JSON dictionary to POST query')
    args = argp.parse_args()

    my_pystola = pystola()
    my_pystola.run(args)


if __name__ == '__main__':
    main()
