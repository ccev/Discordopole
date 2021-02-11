import logging
import argparse
import coloredlogs

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", action='store_true', help="Run the script in debug mode")
args = parser.parse_args()

success_level = 25
if args.debug:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

log = logging.getLogger("Discordopole")

logging.addLevelName(success_level, "SUCCESS")
def success(self, message, *args, **kws):
    self._log(success_level, message, args, **kws) 
logging.Logger.success = success

coloredlogs.DEFAULT_LEVEL_STYLES["debug"] = {"color": "blue"}
#coloredlogs.DEFAULT_FIELD_STYLES = {}
coloredlogs.install(level=log_level, logger=log, fmt="[%(asctime)s] [%(module)s] [%(levelname)-1.1s]  %(message)s", datefmt="%H:%M:%S")