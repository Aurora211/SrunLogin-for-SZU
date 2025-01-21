import argparse
parser = argparse.ArgumentParser(description="Compile the SrunLogin for SZU")
parser.add_argument("-v", "--version", type=str, help="Version of the compiled file", default="0.1.0")
args = parser.parse_args()

import os
import logging
import platform
import subprocess

logging.basicConfig(level="INFO", format="[%(asctime)s][%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

logger.info("version: " + args.version)

logger.info("Removing old spec files...")
if os.path.exists("main.spec"):
    os.remove("main.spec")
if os.path.exists("single.spec"):
    os.remove("single.spec")

logger.info("Generating console parameters...")
main_args = [ "main.py", "--onefile", "--clean", "--name=main", "--distpath=dist", "--log-level=WARN", ]
single_args = [ "single.py", "--onefile", "--clean", "--name=single", "--distpath=dist", "--log-level=WARN",]

try:
    logger.info("Compiling main.py...")
    subprocess.run(["pyinstaller"] + main_args)
    logger.info("Compiling single.py...")
    subprocess.run(["pyinstaller"] + single_args)
except Exception as e:
    logger.warning(f"Compile failed: {e}")
    exit(1)
logger.info("Compile finished.")

arch = platform.architecture()[0]
if platform.system().upper() == "WINDOWS":
    logger.info("Microsoft Windows detected.")
    os.rename("dist/main.exe", "dist/Srun_windows_" + arch + "_v" + args.version + ".exe")
    os.rename("dist/single.exe", "dist/SrunLogin_windows_" + arch + "_v" + args.version + ".exe")
    logger.info("Renamed files.")
elif platform.system().upper() == "LINUX":
    logger.info("Linux detected.")
    os.rename("dist/main", "dist/Srun_linux_" + arch + "_v" + args.version)
    os.rename("dist/single", "dist/SrunLogin_linux_" + arch + "_v" + args.version)
    logger.info("Renamed files.")
    os.system("chmod -c 744 dist/Srun_linux_" + arch + "_v" + args.version)
    os.system("chmod -c 744 dist/SrunLogin_linux_" + arch + "_v" + args.version)
    logger.info("Changed file permissions.")
else:
    logger.error("Unsupported OS: " + platform.system())
    logger.error("Please change file names manually.")