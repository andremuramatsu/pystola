#!/usr/bin/env python3

import argparse
from pystola.suite import suite
from pystola.render.commandline import commandline
from pystola.request import request

class pystola():

    def __init__(self, render):
        self.r = render

    def run(self, args):

        self.r.set_verbosity_level(args.verbose)

        req = request(self.r)
        for tsuite_path in args.file:
            tsuite = suite(self.r)
            cfg = tsuite.parse(tsuite_path)

            for act in cfg['actions']:
                req.run(act)


class pystola_cmd(pystola):
    def main():
        argp = argparse.ArgumentParser(description='Command line arguments')
        argp.add_argument('file', action='store', nargs=1, help='Test suite file')
        argp.add_argument('-v', '--verbose', action='count', required=False, help='Increase verbose')
        args = argp.parse_args()

        my_pystola = pystola(commandline())
        my_pystola.run(args)

if __name__ == '__main__':
    pystola_cmd.main()
