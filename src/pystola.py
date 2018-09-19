#!/usr/bin/env python3
# vim: set fileencoding=utf8 :

import sys
import argparse
import json
from datetime import datetime
from syslog import syslog
from Pystola.PystolaException import PystolaException
from Pystola.suite import suite
from Pystola.render.commandline import commandline
from Pystola.request import request

class pystola():

    def __init__(self, render):
        self.r = render

    def run(self, args):
        if args.quiet:
            self.r.set_verbosity_level(-1)
        else:
            self.r.set_verbosity_level(args.verbose)

        lfh = None
        if args.result_file:
            lfh = open(args.result_file, 'w+')

        results = []
        # building cfg list
        for tsuite_path in args.file:
            # send server request
            req = request(self.r, args)

            # build test suite
            tsuite = suite(self.r)
            cfg = None
            cfg = tsuite.parse(tsuite_path)
            cfg['source'] = tsuite_path
            results.append(cfg)

        self.__save(results, args)

        # running list
        for cfg in results:
            cfg['dt_start'] = str(datetime.now())

            # print suite description
            self.r.suite_description(cfg)

            # running suite actions
            for act in cfg['actions']:
                (result, has_error, error_desc) = req.run(act)
                act['result'] = result
                if has_error: 
                    break

            cfg['dt_end'] = str(datetime.now())

        self.__save(results, args)

    def __save(self, results, args):
        if args.result_file:
            with open(args.result_file, 'w') as fh:
                fh.write(json.dumps(results))


class pystola_cmd(pystola):
    def main():
        argp = argparse.ArgumentParser(description='Command line arguments')
        argp.add_argument('file', action='store', nargs='+', help='Test suite file')
        argp.add_argument('-v', '--verbose', action='count', required=False, help='Increase verbose')
        argp.add_argument('-r', '--result-file', action='store', required=False, help='Write result as JSON file')
        argp.add_argument('-R', '--recursive', action='store_true', required=False, 
                help='Parse the document looking up for inner requests')
        argp.add_argument('--check-html', action='store_true', required=False, 
                help='Validate HTML documents using Nu HTML Checker')
        argp.add_argument('--check-css', action='store_true', required=False, 
                help='Validate CSS documents using Nu HTML Checker')
        argp.add_argument('-q', '--quiet', action='store_true', required=False, help='Do not print any message')
        argp.add_argument('--lib-dir', action='store', required=False, help='Pystola third party libs dir',
                default='/opt/pystola/')
        args = argp.parse_args()

        my_pystola = pystola(commandline())
        my_pystola.run(args)

if __name__ == '__main__':
    try:
        pystola_cmd.main()
    except Exception as e:
        print('An error occurred: %s' % e)
        sys.exit(1)

