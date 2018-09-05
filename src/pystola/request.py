import requests
from pyquery import PyQuery as pq

class request():

    session = None
    resp = None

    __frmdata = {}
    __fdqrylst = ['input', 'select', 'textarea']

    def __init__(self, render):
        self.r = render

    def get_response(self):
        return self.resp

    def get_data(self):
        return self.__frmdata

    def clear_data(self):
        self.__frmdata = []

    def init_session(self):
        self.session = requests.Session()

    def run(self, cfg):
        self.__run(cfg)
        self.__frmdata = self.__parse_fields()
        self.__parse_unexpect(cfg)
        self.__parse_expect(cfg)

    def __run(self, cfg):
        if self.session is None:
            self.init_session()

        self.r.p('CFG: %s' % cfg)

        frmdata = self.__frmdata
        if 'data' in cfg and len(cfg['data']) > 0:
            frmdata.update(cfg['data'])

        if 'post' in cfg:
            self.resp = self.session.post(cfg['post'], data=frmdata, verify=False)

        elif 'get' in cfg:
            self.resp = self.session.get(cfg['get'], data=frmdata, verify=False)

        self.r.content_type(self.resp.headers['Content-Type'])
        self.r.http_code(self.resp.status_code)
        self.r.header(self.resp.headers)
        self.r.body(self.resp.text)

    def __parse_expect(self, cfg):
        if 'expect' not in cfg:
            return

        d = pq(self.resp.text)
        for msk in cfg['expect']:
            if len(d(msk)) == 0:
                self.r.e('Desired pattern not found: %s' % msk)

    def __parse_unexpect(self, cfg):
        if 'unexpect' not in cfg:
            return

        d = pq(self.resp.text)
        for msk in cfg['unexpect']:
            if len(d(msk)):
                self.r.e('Undesired pattern matched: %s' % msk)

    def __parse_fields(self):
        d = pq(self.resp.text)
        fields = {}
        for tp in self.__fdqrylst:
            for fd in d(tp):
                fields[fd.name] = fd.value

        return fields

