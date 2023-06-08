import shutil
from st2common.runners.base_action import Action
from error import Operationfailed

import logging,sys
import ecs_logging

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(ecs_logging.StdlibFormatter())
logger.addHandler(handler)

class CleanAction(Action):

    def clean_action(self):
                """It will will clean/remove all the unwanted files and folders
                """
                try:
                        shutil.rmtree("/packs-workdir/observability_logstash_framework/")

                        logger.info("Cleanup Successful")

                except Exception as e:
                        logger.exception(e)
                        raise Operationfailed(e)

    def run(self):

            """main function
            """

            self.clean_action()