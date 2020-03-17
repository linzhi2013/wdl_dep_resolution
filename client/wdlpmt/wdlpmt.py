#!/usr/bin/env python3
import argparse
import sys

from fetch import main as fetch_main
from install import main as install_main
from submit import main as submit_main
from create_module import main as create_module_main
from create_project import main as create_project_main
from distribute import main as distribute_main


def get_para():
    parser = argparse.ArgumentParser(description='wmlpmt tool. By Guanliang Meng')

    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')

    fetch_parser = subparsers.add_parser('fetch',
        help='fetch the dependencies')

    install_parser = subparsers.add_parser('install',
        help='install the dependencies')

    submit_parser = subparsers.add_parser('submit',
        help='submit a package to the remote repo')

    create_project_parser = subparsers.add_parser('create_project',
        help='create a basic project directory')

    create_module_parser = subparsers.add_parser('create_module',
        help='create basic directory for a module')

    distribute_parser = subparsers.add_parser('distribute',
        help='package your project')


    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    if sys.argv[1] == 'fetch':
        fetch_main(fetch_parser, sys.argv[2:])

    elif sys.argv[1] == 'install':
        install_main(install_parser, sys.argv[2:])

    elif sys.argv[1] == 'submit':
        submit_main(submit_parser, sys.argv[2:])

    elif sys.argv[1] == 'create_project':
        create_project_main(create_project_parser, sys.argv[2:])

    elif sys.argv[1] == 'create_module':
        create_module_main(create_module_parser, sys.argv[2:])

    elif sys.argv[1] == 'distribute':
        distribute_main(distribute_parser, sys.argv[2:])



if __name__ == '__main__':
    get_para()

