from pystola.render.Abstract import Abstract
from colored import fore, back, style, fg, bg
from tabulate import tabulate

class commandline(Abstract):

    def __init__(self):
        Abstract.__init__(self)
        pass

    def p(self, msg):
        fgc=fore.WHITE
        bgc=''
        stl=''
        print('%s%s%s%s%s' % (fgc, bgc, stl, msg, style.RESET))

    def d(self, msg):
        if self.level > 1:
            fgc=fg(8)
            bgc=''
            stl=''
            print('%s%s%sDEBUG: %s%s' % (fgc, bgc, stl, msg, style.RESET))

    def w(self, msg):
        fgc=fore.YELLOW
        bgc=''
        stl=style.BOLD
        print('%s%s%sWARNING: %s%s' % (fgc, bgc, stl, msg, style.RESET))

    def e(self, msg, color='red'):
        fgc=fore.WHITE
        bgc=back.RED
        stl=style.BOLD
        print('%s%s%sERROR: %s%s' % (fgc, bgc, stl, msg, style.RESET))
        raise AssertionError("An assertion error has occurred")

    def content_type(self, msg):
        fgc=fg(11)
        bgc=''
        stl=''
        print('%s%s%sContent Type: %s%s' % (fgc, bgc, stl, msg, style.RESET))

    def body(self, msg):
        if self.level > 2:
            fgc=fg(4)
            bgc=''
            stl=''
            print('%s%s%s%s%s' % (fgc, bgc, stl, msg, style.RESET))

    def header(self, header_dict):
        if self.level > 1:
            fgc=fore.YELLOW
            bgc=''
            stl=''
            print('%s%s%s%s%s' %(fgc, bgc, stl, tabulate([[k,v] for k,v in header_dict.items()]), style.RESET))

    def http_code(self, code):
        if int(code) >= 200:
            fgc=fore.WHITE
            bgc=back.GREEN
            stl=style.BOLD

        if int(code) >= 300:
            fgc=fore.GREEN
            bgc=''
            stl=style.BOLD

        if int(code) >= 400:
            fgc=fore.WHITE
            bgc=back.RED
            stl=style.BOLD

        print('%s%s%sHTTP CODE: %d%s' %(fgc, bgc, stl, code, style.RESET))

