"""A configuration file."""
import os
import paramiko
import pytest
from time import sleep
from modules.server_cmd_execution import ServerCmdExecution
from loggers.logger_creation import log

global_path = os.path.expanduser("~/dirForTest/")


def pytest_addoption(parser):
    """Register argparse-style options and ini-style config values."""
    parser.addoption("--client_ip", action="store")
    parser.addoption("--client_port", action="store")
    parser.addoption("--client_name", action="store")
    parser.addoption("--client_password", action="store")
    parser.addoption("--server_ip", action="store")


@pytest.fixture(scope='module')
def parser_of_client_ip(request):
    """Parse a --client-ip parameter in a commandline."""
    return request.config.getoption("--client_ip")


@pytest.fixture(scope='module')
def parser_of_client_port(request):
    """Parse a --client-port parameter in a commandline."""
    return request.config.getoption("--client_port")


@pytest.fixture(scope='module')
def parser_of_client_name(request):
    """Parse a --client-name parameter in a commandline."""
    return request.config.getoption("--client_name")


@pytest.fixture(scope='module')
def parser_of_client_password(request):
    """Parse a --client-password parameter in a commandline."""
    return request.config.getoption("--client_password")


@pytest.fixture(scope='module')
def parser_of_server_ip(request):
    """Parse a --server-ip parameter in a commandline."""
    return request.config.getoption("--server_ip")


@pytest.fixture(scope="function")
def dir_on_server_creation():
    """Create a directory on a server."""
    log.info("I am in dir_on_server_creation")
    ServerCmdExecution().run_cmd("sudo mkdir -p {}".format(global_path))


@pytest.fixture(scope="function")
def dir_on_serv_permis_change():
    """Change permissions of a directory on a server."""
    log.info("I am in dir_on_serv_permis_change")
    ServerCmdExecution().run_cmd("sudo chmod ugo+rwx {}".format(global_path))


@pytest.fixture(scope="module")
def session_creation(parser_of_client_ip,
                     parser_of_client_port,
                     parser_of_client_name,
                     parser_of_client_password):
    """Create a session with a client."""
    log.info("I am in session_creation")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=parser_of_client_ip,
                   port=int(parser_of_client_port),
                   username=parser_of_client_name,
                   password=parser_of_client_password)
    return client


@pytest.fixture(scope="function")
def dir_on_client_creation(session_creation):
    """Create a directory on a client."""
    log.info("I am in dir_on_client_creation")
    log.info("client {}".format(session_creation))
    session_creation.exec_command('mkdir -p /home/$USER/dirForMount/')


@pytest.fixture(scope="function")
def etc_exports_on_serv_clean():
    """Clean /etc/exports on a server."""
    log.info("I am in etc_exports_on_serv_clean")
    return ServerCmdExecution().run_cmd("sudo cp /dev/null /etc/exports")


@pytest.fixture(scope="function", params=["(rw)", "(ro)"])
def perm_for_export_creation(request, parser_of_client_ip):
    """Create a variable with permissions on import on a server."""
    dir_for_export_name = global_path
    log.info("I am in perm_for_export_creation")
    perm_for_export = "".\
        join([dir_for_export_name, " ", parser_of_client_ip, request.param])
    var = request.param
    return perm_for_export, var


@pytest.fixture(scope="function")
def file_perm_for_export_creation(perm_for_export_creation):
    """Create a file with permissions on import."""
    log.info("I am in file_perm_for_export_creation")
    with open(os.path.join(global_path, "fileWithPermForExport"), "w") as f:
        f.write(perm_for_export_creation[0])
    return f


@pytest.fixture(scope="function")
def file_perm_export_copy():
    """Copy permissions on import to /etc/exports."""
    log.info("I am in file_perm_export_copy")
    ServerCmdExecution().run_cmd("sudo cp {} /etc/exports".
                                 format(os.path.join(global_path,
                                                     "fileWithPermForExport")))


@pytest.fixture(scope="function")
def update_etc_exports():
    """Update of a NFS-export table."""
    log.info("I am in update_etc_exports")
    ServerCmdExecution().run_cmd("sudo exportfs -a")


@pytest.fixture(scope="function")
def mount_dir(session_creation,
              parser_of_client_password,
              parser_of_server_ip):
    """Mount of a directory on a client."""
    log.info("I am in mount_dir")
    session_creation.exec_command("echo {} | sudo -S mount {}:{} "
                                  "/home/$USER/dirForMount/".
                                  format(parser_of_client_password,
                                         parser_of_server_ip,
                                         global_path))
    sleep(1)


@pytest.fixture(scope="function")
def main_setup_fixture(request, parser_of_client_password,
                       dir_on_server_creation,
                       dir_on_serv_permis_change,
                       session_creation,
                       dir_on_client_creation,
                       etc_exports_on_serv_clean,
                       perm_for_export_creation,
                       file_perm_for_export_creation,
                       file_perm_export_copy,
                       update_etc_exports,
                       mount_dir):
    """Manage the order of setup fixtures."""
    log.info("I am in main_setup_fixture")

    def main_teardown_finalizer():
        """Clean the environment which was created."""
        log.info("I am in main_teardown_finalizer")
        ServerCmdExecution().run_cmd("sudo rm -rf {}".format(global_path))
        log.info("/home/polina/dirForTest/ is removed on server")
        stdin, stdout, stderr = \
            session_creation.exec_command('echo {} | sudo -S rm -rf'
                                          ' /home/$USER/dirForMount/'.
                                          format(parser_of_client_password))
        log.info("{}".format(stderr.read()))
        log.info("/home/$USER/dirForMount/ is removed on client")
        log.info("client {}".format(session_creation))

    def unmount_dir():
        """Unmount a directory on a client."""
        log.info("I am in unmount_dir")
        stdin, stdout, stderr = \
            session_creation.exec_command("echo {} | sudo -S umount"
                                          " /home/$USER/dirForMount/".
                                          format(parser_of_client_password))
        log.info("{}".format(stderr.read()))

    request.addfinalizer(main_teardown_finalizer)
    request.addfinalizer(unmount_dir)
    return 0
