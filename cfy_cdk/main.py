import sys
import argparse
import subprocess
import pkg_resources

from aws import DEFAULT_BP_PATH

CDK_INIT_FILE = 'main_init.py'


class CloudifyCDKError(Exception):
    pass


def run(command, stdin=u'', stdout=None, ignore_failures=False):
    if isinstance(stdin, str):
        stdin = stdin.encode('utf-8')
    stdout = stdout or subprocess.PIPE
    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=stdout,
                            stderr=subprocess.PIPE)
    proc.aggr_stdout, proc.aggr_stderr = proc.communicate(input=stdin)
    if proc.aggr_stdout is not None:
        proc.aggr_stdout = proc.aggr_stdout.decode('utf-8')
    if proc.aggr_stderr is not None:
        proc.aggr_stderr = proc.aggr_stderr.decode('utf-8')
    if proc.returncode != 0:
        if not ignore_failures:
            msg = 'Failed running command: {0} ({1}).'.format(
                command, proc.aggr_stderr)
            err = CloudifyCDKError(msg, proc.returncode)
            err.aggr_stdout = proc.aggr_stdout
            err.aggr_stderr = proc.aggr_stderr
            raise err
    return proc


def verify_cfy_is_present():
    try:
        run(['command', '-v', 'cfy'])
        return True
    except CloudifyCDKError:
        raise CloudifyCDKError('Cloudify CLI is not present is '
                               'required for installing the blueprint.')


def init_file():
    init_file_path = pkg_resources.resource_filename('cfy_cdk', 'init_file.py')
    run(['sudo', 'cp', init_file_path, CDK_INIT_FILE])


def synth_instance(output_path):
    run(['python', CDK_INIT_FILE])
    print('Blueprint was saved to {0}'.format(output_path))


def install_instance(output_path, unique_id):
    verify_cfy_is_present()
    synth_instance(output_path)
    run(['cfy', 'install', output_path, '-d', unique_id, '-b', unique_id],
        stdout=sys.stdout)


def add_output_path_arg(parser):
    parser.add_argument('-o', '--output',
                        action='store',
                        help='The local path to save the blueprint to. ' 
                             'Default: ./{0}'.format(DEFAULT_BP_PATH),
                        default=DEFAULT_BP_PATH)


def main():
    parser = argparse.ArgumentParser(description='Cloudify CDK')

    subparsers = parser.add_subparsers(help='Cloudify CDK action',
                                       dest='action')

    synth_args = subparsers.add_parser('synth', help='Create a blueprint.')
    add_output_path_arg(synth_args)

    install_args = subparsers.add_parser(
        'install',  help='Create and install a blueprint.')

    add_output_path_arg(install_args)
    install_args.add_argument('--id',
                              help='The blueprint and deployment ID. '
                                   'Default: Cloudify-CDK',
                              default='Cloudify-CDK')

    subparsers.add_parser('init', help='Create an init file.')

    args = parser.parse_args()

    if args.action == 'synth':
        synth_instance(args.output)

    elif args.action == 'install':
        install_instance(args.output, args.id)

    elif args.action == 'init':
        init_file()
