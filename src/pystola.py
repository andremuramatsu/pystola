#!/usr/bin/env python3

import os
import sys
import requests
import argparse
import url
import json
from tabulate import tabulate
from termcolor import colored
from tidylib import tidy_document
from html.parser import HTMLParser
from pyquery import PyQuery as pq

class pystola_html_parser(HTMLParser):

    def set_callback(self, callback):
        self.__clbk = callback

    def handle_starttag(self, tag, attr):
        self.__clbk(tag, attr)

class pystola():

    M_POST='POST'
    M_GET='GET'

    rid = 0
    nline = 0
    no_child_verbosity = True
    verbosity_lv = 0
    base_url = None
    target_method = None
    target_url = None
    payload = []

    def __error(self, msg):
        print(colored('ERROR: %s' % msg, 'red'))
        sys.exit(1)

    def __print(self, msg):
        for line in msg.splitlines():
            self.nline = self.nline + 1
            print('%05d%010d: %s' % (self.rid, self.nline, line))

    def __dict_to_list(self, dic):
        lst = []
        for item in dic:
            lst.append([item, dic[item]])

        return lst

    def __get_attr(self, attrlst, attrnm):
        attr = list(filter(lambda x:attrnm in x, attrlst))
        attrvl = None
        if len(attr) > 0:
            attrvl = attr[0][1]
        return attrvl


    def __parse_external_ref_tag(self, tag, attr):
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

    def __parse_external_ref(self, r):
        parser = pystola_html_parser()
        parser.set_callback(self.__parse_external_ref_tag)
        parser.feed(r.text)

    def __parse_http_code(self, r):
        bgc = 'on_blue'
        fgc = 'white'
        if r.status_code != requests.codes.ok:
            bgc = 'on_red'

        return colored('HTTP CODE: %s' % r.status_code, fgc, bgc)

    def __parse_html(self, body):
        return tidy_document(body)

    def __request(self, urldst, is_html = True, cookies = None):
        tmpu = url.parse(urldst)
        if not tmpu.absolute:
            urldst = '%s/%s' % (self.base_url, urldst)

        self.rid = self.rid + 1
        payload = {}
        headers = {}
        timeout = 30

        if cookies is not None:
            print(colored(cookies, 'green'))
            r = requests.get(urldst, verify=False, params=payload, headers=headers, timeout=timeout, cookies=cookies)
        else:
            r = requests.get(urldst, verify=False, params=payload, headers=headers, timeout=timeout)

        return self.__process(r, is_html)

    def __process(self, r, is_html = True):
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

            if self.no_child_verbosity is False:
                self.__parse_external_ref(r)

        return r


    def __parse_fields(self, r):
        q = pq(r.text)
        rlst = dict()
        for fd in q('input'):
            rlst[fd.name] = fd.value

        return rlst

    def __save_cookie(self, fpath, cookies):
        cl = dict()
        for c in cookies:
            cl[c.name] = {'value': c.value, 'domain': c.domain, 'path': c.path}

        with open(fpath, 'w') as f:
            f.write(json.dumps(cl))

    def __load_cookie(self, fpath):
        strcookie = None
        with open(fpath, 'r') as f:
            strcookie = f.read()

        cookies = None
        jar = requests.cookies.RequestsCookieJar()
        if len(strcookie) > 0:
            cookies = json.loads(strcookie)
            for nm in cookies:
                jar.set(nm, cookies[nm]['value'], domain=cookies[nm]['domain'], path=cookies[nm]['path'])

        return jar


    def __is_valid_path(self, fpath):
        if os.path.exists(fpath):
            return True
        elif os.access(os.path.dirname(fpath), os.W_OK):
            return True
        else:
            return False

    def __is_valid_file(self, fpath):
        return os.path.exists(fpath)

    def run(self, args):
        self.verbosity_lv = args.verbose
        self.no_child_verbosity = args.no_child_verbosity

        if args.action:
            self.target_url = args.action

        if args.method:
            self.target_method = args.method

        self.cookies_save = None
        if args.save_cookies_to_file:
            self.cookies_save = args.save_cookies_to_file
            if self.__is_valid_path(self.cookies_save) is False:
                self.__error('Cookies target is an invalid path')

        self.cookies_load = None
        if args.cookies_file:
            self.cookies_load = args.cookies_file
            if self.__is_valid_file(self.cookies_load) is False:
                self.__error('Cookies load target is an invalid path')

        self.target_payload = None
        if args.payload:
            try:
                self.target_payload = json.loads(args.payload)
            except:
                self.__error('Invalid JSON payload')

        tmpu = args.url
        tmpp = url.parse(args.url)
        if len(str(tmpp.path)) > 0:
            tmpu = tmpu[:int(tmpu.find(str(tmpp.path)))]

        saved_cookies=None
        if self.cookies_load is not None:
            saved_cookies = self.__load_cookie(self.cookies_load)
            print(saved_cookies)
           
        self.base_url = tmpu
        r = self.__request(args.url, cookies=saved_cookies)

        if self.cookies_save is not None:
            self.__save_cookie(self.cookies_save, r.cookies)

        frmfdlst = dict()
        if self.target_url:
            frmfdlst = self.__parse_fields(r)

            if self.target_payload:
                for p in self.target_payload:
                    frmfdlst[p] = self.target_payload[p]

            cj = requests.cookies.RequestsCookieJar()
            for c in r.cookies:
                cj.set(c.name, c.value, domain=c.domain)

            r2 = requests.post(self.target_url, data = frmfdlst, verify=False, cookies=cj)
            self.__process(r2)


def main():
    argp = argparse.ArgumentParser(description='Command line arguments')
    argp.add_argument('-u', '--url', action='store', required=True, help='URL to test')
    argp.add_argument('-a', '--action', action='store', required=False, help='Target URL')
    argp.add_argument('-m', '--method', action='store', required=False, help='Submit method', default='POST')
    argp.add_argument('-v', '--verbose', action='count', required=False, help='Increase verbose')
    argp.add_argument('-p', '--payload', action='store', required=False, help='JSON payload')
    argp.add_argument('-c', '--cookies-file', action='store', 
            required=False, help='Use target file content as cookie')
    argp.add_argument('--save-cookies-to-file', action='store', 
            required=False, help='Save session cookies to target file')
    argp.add_argument('--no-child-verbosity', action='count', required=False, help='Ignore verbose level to childs')
    args = argp.parse_args()

    my_pystola = pystola()
    my_pystola.run(args)


if __name__ == '__main__':
    main()
