from apis.sensitive_api import SensitiveApi


class LCMX(SensitiveApi):
    def __init__(self, path):
        SensitiveApi.__init__(path)
        print("")
