import yaml
from yaml.loader import SafeLoader
from st2common.runners.base_action import Action

from error import Operationfailed

import logging,sys
import ecs_logging

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(ecs_logging.StdlibFormatter())
logger.addHandler(handler)

class UpdateChartVersion(Action):
        
    def chart_version(self, gitpush_repo_name):

        """
            Function will read the previous version from Chart.yaml file and increase the version by 0.1
            It will update the Chart.yaml with new version value
        """
        try:
            with open('/packs-workdir/observability_logstash_framework/'+gitpush_repo_name+'/Chart.yaml') as f:
                data = yaml.load(f, Loader=SafeLoader)

            data['version'] += 0.1
            data['version'] = round(data['version'],1)
            
            with open('/packs-workdir/observability_logstash_framework/'+gitpush_repo_name+'/Chart.yaml', 'w') as f:
                data = yaml.dump(data, f, sort_keys=False, default_flow_style=False)

            logger.info("Chart version updated.")
        except Exception as e:
            logger.exception(e)
            raise Operationfailed("Error, chart version update failed.")

    def run(self, gitpush_repo_name):

            """main function
            """

            self.chart_version(gitpush_repo_name)


