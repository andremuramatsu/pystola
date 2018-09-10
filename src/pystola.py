#!/usr/bin/env python3

import sys
import argparse
import json
from pystola.suite import suite
from pystola.render.commandline import commandline
from pystola.request import request
from datetime import datetime

class pystola():

    def __init__(self, render):
        self.r = render

    def run(self, args):
        if args.quiet:
            self.r.set_verbosity_level(-1)
        else:
            self.r.set_verbosity_level(args.verbose)

        lfh = None
        result = []
        if args.result_file:
            lfh = open(args.result_file, 'w')

        for tsuite_path in args.file:
            success=True
            t_det=None
            dt_ini=str(datetime.now())
            try:
                req = request(self.r)
                tsuite = suite(self.r)
                cfg = tsuite.parse(tsuite_path)

                self.r.suite_description(cfg)
                for act in cfg['actions']:
                    req.run(act)

            except Exception as e:
                t_det=str(e)
                success=False
                pass

            if lfh is not None:
                lfh.seek(0)
                cfg_name = None
                if 'name' in cfg:
                    cfg_name = cfg['name']

                cfg_desc = None
                if 'description' in cfg:
                    cfg_desc = cfg['description']

                result.append({
                    'suite': tsuite_path, 
                    'success': success, 
                    't_start': dt_ini,
                    't_end': str(datetime.now()),
                    'name': cfg_name,
                    'description': cfg_desc,
                    'detail': t_det})
                lfh.write(json.dumps(result))
                lfh.flush()



class pystola_cmd(pystola):
    def main():
        argp = argparse.ArgumentParser(description='Command line arguments')
        argp.add_argument('file', action='store', nargs='+', help='Test suite file')
        argp.add_argument('-v', '--verbose', action='count', required=False, help='Increase verbose')
        argp.add_argument('-r', '--result-file', action='store', required=False, help='Target to JSON result')
        argp.add_argument('-q', '--quiet', action='store_true', required=False, help='Do not print any message')
        args = argp.parse_args()

        my_pystola = pystola(commandline())
        my_pystola.run(args)

if __name__ == '__main__':
    try:
        pystola_cmd.main()
    except:
        print('An error occurred')
        sys.exit(1)

