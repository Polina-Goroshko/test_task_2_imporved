"""Own module: runs server commmands"""
import subprocess
import getpass
import shlex


class ServerCmdExecution:
    """Define a method, which runs commands on a server"""

    @staticmethod
    def run_cmd(cmd: str) -> int:
        """Run commands on a server"""
        if getpass.getuser() == 'root':
            cmd.replace('sudo', '')
        proc = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE)
        proc.communicate()
        return_code = proc.wait()
        return return_code
