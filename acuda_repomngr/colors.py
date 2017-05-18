#https://gist.github.com/Sheljohn/68ca3be74139f66dbc6127784f638920

class ColorPrinter:
    """
    Usage:
    cprint = ColorPrinter()
    cprint.cfg('c','m','bux').out('Hello','World!')
    cprint.rst().out('Bye now...')

    See: http://stackoverflow.com/a/21786287/472610
    See: https://en.wikipedia.org/wiki/ANSI_escape_code
    """

    COLCODE = {
        'k': 0,  # black
        'r': 1,  # red
        'g': 2,  # green
        'y': 3,  # yellow
        'b': 4,  # blue
        'm': 5,  # magenta
        'c': 6,  # cyan
        'w': 7   # white
    }

    FMTCODE = {
        'b': 1,  # bold
        'f': 2,  # faint
        'i': 3,  # italic
        'u': 4,  # underline
        'x': 5,  # blinking
        'y': 6,  # fast blinking
        'r': 7,  # reverse
        'h': 8,  # hide
        's': 9,  # strikethrough
    }


    def __init__(self):
        self.rst()


    # ------------------------------
    # Group actions
    # ------------------------------

    def rst(self):
        self.prop = {'st': list(), 'fg': None, 'bg': None}
        return self


    def cfg(self, fg=None, bg=None, st=None):
        return self.rst().st(st).fg(fg).bg(bg)


    # ------------------------------
    # Set individual properties
    # ------------------------------

    def stclear(self):
        self.prop['st'] = list()
        return self

    def st(self, st):
        if isinstance(st, int):
            assert (st >= 0) and (st < 10), 'Style should be in {0 .. 9}.'
            self.prop['st'].append(st)
        elif isinstance(st, str):
            for s in st:
                self.st(self.FMTCODE[s])
        return self


    def fg(self, fg):
        if isinstance(fg, int):
            assert (fg >= 0) and (fg < 8), 'Color should be in {0 .. 7}.'
            self.prop['fg'] = 30 + fg
        elif isinstance(fg, str):
            self.fg(self.COLCODE[fg])
        return self


    def bg(self, bg):
        if isinstance(bg, int):
            assert (bg >= 0) and (bg < 8), 'Color should be in {0 .. 7}.'
            self.prop['bg'] = 40 + bg
        elif isinstance(bg, str):
            self.bg(self.COLCODE[bg])
        return self


    # ------------------------------
    # Format and standard output
    # ------------------------------

    def fmt(self, *args):

        # accept multiple inputs, and concatenate them with spaces
        s = " ".join(map(str, args))

        # get anything that is not None
        w = self.prop['st'] + [self.prop['fg'], self.prop['bg']]
        w = [str(x) for x in w if x is not None]
        # return formatted string
        return '\x1b[%sm%s\x1b[0m' % (';'.join(w), s) if w else s


    def out(self, *args):
        print(self.fmt(*args))

if __name__ == '__main__':

    cprint = ColorPrinter()
    for st in range(0, 10):
        for fg in range(8):
            for bg in range(8):
                print(cprint.cfg(fg, bg, st).fmt('{:^15}'.format(' '.join(['BG', str(bg), 'FG', str(fg)]))), end=' ')
            print()
        print()

