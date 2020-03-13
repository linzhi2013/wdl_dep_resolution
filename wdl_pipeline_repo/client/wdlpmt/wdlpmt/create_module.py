#!/usr/bin/env python3
import sys
import os
import re
import argparse

# not finished!!!

def get_para(parser):
    # create a new module
    parser.add_argument('-project_root', metavar='<directory>',
        default='./', required=True,
        help='the project_root directory [%(default)s]')

    parser.add_argument('-module_name', metavar='<file>', required=True, help="module name")

    return parser


def create_module(project_root='./', project_name='my_new_wdl_pipeline'):
    '''
    create project directory structure and some basic files.
    '''
    project_path = os.path.join(project_root, project_name)

    if os.path.exists(project_path):
        sys.exit(project_path + ' exists! Exit!')

    make_project_dirs(project_path)

    create_readme(project_path=project_path)

    create_pkg_info(project_path=project_path)



def main(parser=None, paras=None):

    if not parser:
        parser = argparse.ArgumentParser()

    parser = get_para(parser)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args(paras)

    print(args)

    create_module(
        project_root=args.project_root,
        project_name=args.project_name)

if __name__ == '__main__':
    main(paras=sys.argv[1:])

