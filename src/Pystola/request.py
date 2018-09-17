# vim: set fileencoding=utf8 :

import requests
import sys
from urllib.parse import urlparse, urljoin
from Pystola.libs.vnu import vnu
from Pystola.PystolaException import PystolaException
from pyquery import PyQuery as pq

class request():

    session = None
    resp = None

    __frmdata = {}
    __fdqrylst = ['input', 'select', 'textarea']

    def __init__(self, render, args):
        self.r = render
        self.args = args

    def get_response(self):
        return self.resp

    def get_data(self):
        return self.__frmdata

    def clear_data(self):
        self.__frmdata = []

    def init_session(self):
        self.session = requests.Session()

    def run(self, cfg):
        ret = {'html_check': None, 'error': False, 'detail': 'Success', 'recursive': None}
        try:
            self.__run(cfg)
            self.__frmdata = self.__parse_fields()
            self.__parse_unexpect(cfg)
            self.__parse_expect(cfg)
            if self.args.check_html is True:
                ret['html_check'] = self.__run_vnu()

            if self.args.recursive is True:
                ret['recursive'] = self.__run_recursive()

        except PystolaException as e:
            ret['error'] = True
            ret['detail'] = str(e)

        except Exception as e:
            ret['error'] = True
            ret['detail'] = str(e)
            self.r.e(ret['detail'])

        return (ret, ret['error'], ret['detail'])

    def __run(self, cfg):
        if self.session is None:
            self.r.w('Session initialized')
            self.init_session()

        self.r.p('ACTION: %s' % cfg)
        if 'post' in cfg:
            frmdata = self.__frmdata
            if 'data' in cfg and len(cfg['data']) > 0:
                frmdata.update(cfg['data'])
            self.resp = self.session.post(cfg['post'], data=frmdata, verify=False)

        elif 'get' in cfg:
            frmdata = []
            if 'data' in cfg:
                frmdata = cfg['data']
            self.resp = self.session.get(cfg['get'], data=frmdata, verify=False)

        self.r.content_type(self.resp.headers['Content-Type'])
        self.r.http_code(self.resp.status_code)
        self.r.header(self.resp.headers)
        self.r.body(self.resp.text)

    def __run_recursive(self):
        urlp = self.resp.url
        d = pq(self.resp.text)
        result = []
        for obj in d('img'):
            if 'src' in obj.attrib:
                url = obj.attrib['src']
                result.append(self.__run_isolated_url(urljoin(urlp, url)))

        for obj in d('link'):
            if 'href' in obj.attrib:
                url = obj.attrib['href']
                result.append(self.__run_isolated_url(urljoin(urlp, url)))

        for obj in d('script'):
            if 'src' in obj.attrib:
                url = 'x' +  obj.attrib['src'] 
                result.append(self.__run_isolated_url(urljoin(urlp, url)))

        return result

    def __run_isolated_url(self, url):
        self.r.p('INNER REQUEST: %s' % url)
        req = self.session.get(url, verify=False)
        ret = {'url': url, 'http_code': req.status_code, 'mime': req.headers['Content-Type']}
        self.r.http_code(ret['http_code'])
        self.r.content_type(ret['mime'])
        return ret

    def __run_vnu(self):
        eng = vnu(self.args.lib_dir)
        vnur = eng.validate_html(self.resp.text)
        self.r.vnu(vnur)
        return vnur

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

