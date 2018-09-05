import os
import json
import string

class suite():

    def __init__(self, render):
        self.r = render

    def __parse_env_str(self, mstr):
        try:
            mstr = string.Template(mstr).substitute(os.environ)
        except KeyError as e:
            self.r.e('Environment variable %s is undefined' % e)

        return mstr

    def __parse_env(self, lst):
        for act in lst:
            if 'get' in act:
                act['get'] = self.__parse_env_str(act['get'])

            if 'post' in act:
                act['post'] = self.__parse_env_str(act['post'])

            if 'data' in act:
                for p in act['data']:
                    if isinstance(act['data'][p], str):
                        act['data'][p] = self.__parse_env_str(act['data'][p])

        return lst

    def __load(self, fpath):
        if os.path.isfile(fpath) is False:
            raise FileNotFoundError('File %s not found' % fpath)

        if os.access(fpath, os.R_OK) is False:
            raise PermissionError('Forbidden file %s' % fpath)

        suitestr = None
        with open(fpath) as fh:
            suitestr = fh.read()

        suite = json.loads(suitestr)
        _clst = []

        if 'actions' not in suite:
            return []

        for act in suite['actions']:
            if 'execute' in act:
                tmpsuite = self.__load(act['execute'])
                if len(tmpsuite) > 0 and 'actions' in tmpsuite:
                    _clst = _clst + tmpsuite['actions']
            else:
                _clst.append(act)

        suite['actions'] = self.__parse_env(_clst)
        return suite

    def parse(self, fpath):
        return self.__load(fpath)
