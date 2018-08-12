"""Test module: creation of a file."""
from loggers.logger_creation import log


def test_file_creation(parser_of_client_ip,
                       parser_of_client_port,
                       parser_of_client_name,
                       parser_of_client_password,
                       parser_of_server_ip,
                       main_setup_fixture,
                       perm_for_export_creation,
                       session_creation):
    """Test function: creation of a file."""
    log.info("I am in a test_file_creation: file creation")
    log.info("Here is what now is in /etc/exports {}".format(
             perm_for_export_creation[0]))
    stdin, stdout, stderr = session_creation.\
        exec_command("echo {} | sudo -S touch /home/$USER"
                     "/dirForMount/cinema".format(parser_of_client_password))
    log.info("{}".format(stderr.read()))
    log.info("permForExportCreation[1] in test_file_creation: {}".format(
             perm_for_export_creation[1]))
    if "(ro)" == perm_for_export_creation[1]:
        log.info("exit status of creation a file with RO: {}".format(
                 stdout.channel.recv_exit_status()))
        assert stdout.channel.recv_exit_status() == 1
    else:
        log.info("exit status of creation a file with RW: {}".format(
                 stdout.channel.recv_exit_status()))
        assert stdout.channel.recv_exit_status() == 0
