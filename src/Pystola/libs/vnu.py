# vim: set fileencoding=utf8 :

import subprocess
import os
import tempfile
import json

class vnu():

    def __init__(self, lib_dir):
        self.__lib_dir = lib_dir

    def validate_html(self, src):
        vnupath = self.__lib_dir + '/vnu/vnu.jar'
        if os.path.isfile(vnupath) is False:
            raise Exception('vnu.jar not found')

        tmpf = tempfile.NamedTemporaryFile()
        tmpf.write(src.encode('utf-8'))
        proc = subprocess.Popen(
                ['java', '-jar', vnupath, '--errors-only', '--format', 'json', tmpf.name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        resp = proc.communicate()

        ret = []
        if resp[1] is not None:
            ret = json.loads(resp[1].decode('utf-8'))
        return ret

