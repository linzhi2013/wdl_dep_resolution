import os
import glob
import sys
import argparse
import subprocess
import platform
from .fetch import fetch_pkgs


def get_para(parser):
    # install
    parser.add_argument('-i', metavar='<file>',
        dest='pkg_info_file', help="pkg_info.txt file")

    parser.add_argument('-j', metavar='<file>',
        dest='pkg_gz_files_listFile', help="a list of the downloaded *.tar.gz files")

    parser.add_argument('-install_root', metavar='<directory>',
        default='./',
        help='the project_root directory [%(default)s]')

    parser.add_argument('-url', metavar='<url>',
        default='http://127.0.0.1:8000/',
        dest='base_url', help='Base url [%(default)s]')

    parser.add_argument('-cache_dir', metavar='<directory>',
        default='_wdl_cache', help='the cache directory [%(default)s]')

    return parser


def deal_single_pkg(pkg_gz_file=None, install_root='./'):
    pkg_gz_file_dir = os.path.dirname(pkg_gz_file)

    cmd = 'tar -zxvf {0} -C {1}'.format(pkg_gz_file, pkg_gz_file_dir)
    subprocess.check_call(cmd, shell=True)

    pkg_dir = pkg_gz_file.replace('.tar.gz', '')
    pkg_name = os.path.basename(pkg_gz_file).split('-', 1)[0]


    # src
    pkg_src_wdl = os.path.join(pkg_dir, 'src', 'wdl')
    project_src_deps = os.path.join(install_root, 'src', 'deps', pkg_name)

    if not os.path.exists(project_src_deps):
        os.makedirs(project_src_deps, exist_ok=True)

    if os.path.exists(pkg_src_wdl):
        cmd = 'cp -r {0}/* {1}'.format(pkg_src_wdl, project_src_deps)
        subprocess.check_call(cmd, shell=True)

    # update import paths
    update_wdl_import_paths(wdl_dir=project_src_deps, pkg_name=pkg_name)


    # doc
    pkg_doc = os.path.join(pkg_dir, 'doc')
    project_doc_deps = os.path.join(install_root, 'doc', 'deps', pkg_name)

    if not os.path.exists(project_doc_deps):
        os.makedirs(project_doc_deps, exist_ok=True)

    if os.path.exists(pkg_doc):
        cmd = 'cp -r {0}/* {1}'.format(pkg_doc, project_doc_deps)
        subprocess.check_call(cmd, shell=True)


    # docker
    pkg_docker = os.path.join(pkg_dir, 'docker')
    project_docker_deps = os.path.join(install_root, 'docker', 'deps', pkg_name)

    if not os.path.exists(project_docker_deps):
        os.makedirs(project_docker_deps, exist_ok=True)

    if os.path.exists(pkg_docker):
        cmd = 'cp -r {0}/* {1}'.format(pkg_docker, project_docker_deps)
        subprocess.check_call(cmd, shell=True)


def update_wdl_import_paths(wdl_dir=None, pkg_name=None):
    wdl_files = glob.glob(wdl_dir + '/**/*.wdl', recursive=True)
    plt = platform.system()
    for f in wdl_files:
        if plt == 'Darwin':
            cmd = "sed -i '' 's#src/wdl/#src/deps/{pkg_name}/#g' {f}".format(pkg_name=pkg_name, f=f)
        else:
            cmd = "sed -i 's#src/wdl/#src/deps/{pkg_name}/#g' {f}".format(pkg_name=pkg_name, f=f)
        print(cmd, flush=True)
        subprocess.check_call(cmd, shell=True)



def install_pkgs(pkg_gz_files=None, install_root='./'):
    '''
    Decompress the pkg gz files, and copy the files to
    install_root directory. Will also replace the 'src/wdl'
    to 'src/deps/pkg-name' for the 'import' parts of WDL files.
    '''

    for pkg_gz_file in pkg_gz_files:
        deal_single_pkg(
            pkg_gz_file=pkg_gz_file,
            install_root=install_root)


def main(parser=None, paras=None):

    if not parser:
        parser = argparse.ArgumentParser()

    parser = get_para(parser)

    if len(sys.argv) == 1 or len(paras) == 0:
        parser.print_help()
        sys.exit()

    args = parser.parse_args(paras)

    args.install_root = os.path.abspath(args.install_root)

    print(args)

    if (not args.pkg_gz_files_listFile) and (not args.pkg_info_file):
        sys.exit('You must specify either -i or -j option!')

    pkg_gz_files = []

    if args.pkg_gz_files_listFile:
        with open(args.pkg_gz_files_listFile, 'r') as fh:
            for i in fh:
                i = i.strip()
                if not i:
                    continue
                pkg_gz_files.append(i)
    else:
        pkg_gz_files = fetch_pkgs(
            base_url=args.base_url,
            cache_dir=args.cache_dir,
            pkg_info_file=args.pkg_info_file)

    install_pkgs(
        pkg_gz_files=pkg_gz_files,
        install_root=args.install_root)

if __name__ == '__main__':
    main(paras=sys.argv[1:])



