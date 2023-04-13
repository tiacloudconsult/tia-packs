import os

from st2common.runners.base_action import Action

class Jinja2InstallAction(Action):
    def run(self, pip_package_name):
        os.system("pip install %s" % pip_package_name)