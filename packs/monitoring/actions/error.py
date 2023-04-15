class buildfailed(Exception):
    def __init__(self, m):
        self.message = m

class buildcanceled(Exception):
    def __init__(self, m):
        self.message = m

class pipelinenottriggred(Exception):
    def __init__(self, m):
        self.message = m

class operationfailed(Exception):
    def __init__(self, m):
        self.message = m


