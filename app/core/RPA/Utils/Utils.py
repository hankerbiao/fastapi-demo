import subprocess
from typing import List


def cmd_linux(cmd) -> List:
    """
    执行一条cmd命令
    """
    result = list()
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True)
    try:
        proc.wait(3)
    except Exception as e:
        proc.terminate()
        result.append(str(e))
    out = proc.stdout.readlines()
    for line in out:
        result.append(line.strip() + '\n')
    return result
