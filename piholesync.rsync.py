#!/usr/bin/python3

import json
from pathlib import Path

from dataclasses import dataclass, field, MISSING

from multiprocessing.pool import ThreadPool
import subprocess


@dataclass
class syncTarget:
    ip:   str = None
    user:  str = None
    folder: str = Path
    dockerContainer: str = None
    restart: int = 0
    gravity: int = 0
    resultFiles = None
    resultGravity: subprocess.CompletedProcess = None
    resultRestart: subprocess.CompletedProcess = None


@dataclass
class syncFile:
    filename: Path = None
    restart: int = 0
    gravity: int = 0


@dataclass
class syncMaster:
    folder: str = None
    files: list[syncFile] = None
    targets: list[syncTarget] = None

    def __init__(self, theFile):
        if isinstance(theFile, Path):
            ...
        elif type(theFile) == str:
            theFile = Path(theFile)
        else:
            raise TypeError(theFile)

        if not theFile.is_file():
            raise FileNotFoundError(theFile)
        contents = json.loads(theFile.read_text())
        self.folder = Path(contents.get("folder"))
        self.files = [syncFile(filename=Path(self.folder).joinpath(f["filename"]), restart=f.get(
            "restart", 0), gravity=f.get("gravity", 0)) for f in contents.get("files")]  # if Path(self.folder).joinpath(f["filename"]).is_file()]
        self.targets = [syncTarget(ip=t.get("ip"), user=t.get("user", "pi"), folder=Path(t.get(
            "folder", self.folder)), dockerContainer=t.get("dockerContainer")) for t in contents.get("targets")]

    def doTheSync(self):

        for t in self.targets:
            print(f'Syncing to {t.ip}')

            t.resultFiles = []
            for f in self.files:
                thisCommand = f"rsync -ai \"{f.filename}\" {t.user}@{t.ip}:\"{t.folder}\""
                if t.user == "root":
                    ...
                else:
                    thisCommand += " --rsync-path=\"sudo rsync\""
                print(thisCommand)
                t.resultFiles.append(subprocess.run(
                    thisCommand.split(), capture_output=True))
                cnt = 1
                t.restart += (f.restart * cnt)
                t.gravity += (f.gravity * cnt)

            # for f in
            # RSYNC_COMMAND=$(rsync - ai $PIHOLEDIR /$FILE $HAUSER @$THIS_PI: $PIHOLEDIR - -rsync-path="sudo rsync")
            # if [[-n "${RSYNC_COMMAND}"]]; then

#           RSYNC_COMMAND=$(rsync -ai $PIHOLEDIR/$FILE $HAUSER@$THIS_PI:$PIHOLEDIR)

        def getTheCommand(thisOne, theCommand):
            if thisOne.user == "root":
                ...
            else:
                theCommand = f"sudo -S {theCommand}"
            return f"ssh {thisOne.user}@{thisOne.ip} \"{theCommand}\""

        def doGravity(thisOne):
            if thisOne.gravity == 0:
                return None

            theCommand = "pihole -g"
            if thisOne.dockerContainer:
                theCommand = f"docker exec {thisOne.dockerContainer} {theCommand}"
            theCommand = getTheCommand(thisOne, theCommand)
            # print(theCommand)
            return subprocess.run(
                theCommand.split(), capture_output=True)

        def doRestart(thisOne):
            if thisOne.restart == 0:
                return None
            if thisOne.dockerContainer:
                theCommand = f"docker restart {thisOne.dockerContainer}"
            else:
                theCommand = "service pihole-FTL restart"
            theCommand = getTheCommand(thisOne, theCommand)
            # print(theCommand)
            return subprocess.run(
                theCommand.split(), capture_output=True)

        def doThisOne(thisOne):
            theDict = {"ix": thisOne[0], "gravity": doGravity(
                thisOne[1]), "restart": doRestart(thisOne[1])}
            return theDict

        numThreads = 3
        results = ThreadPool(numThreads).imap_unordered(
            doThisOne, enumerate(self.targets))
        for r in results:
            ...
            self.targets[r["ix"]].resultGravity = r["gravity"]
            self.targets[r["ix"]].resultRestart = r["restart"]

        print(str(self.targets))

        # print(str(self.targets))
        # print(str(self.targets))

#   if [[ -n "${RSYNC_COMMAND}" ]]; then
#     # rsync copied changes, update GRAVITY
#     ssh $HAUSER@$PIHOLE2 "sudo -S pihole -g"
#     # else
#     # no changes
#   fi

#   if [ $RESTART == "1" ]; then
#     # INSTALL FILES AND RESTART pihole
#     ssh $HAUSER@$PIHOLE2 "sudo -S service pihole-FTL restart"
#   fi


def doFile(theFile):

    this = syncMaster(theFile=theFile)
    this.doTheSync()


if __name__ == '__main__':
    doFile('piholesync.rsync.json')
