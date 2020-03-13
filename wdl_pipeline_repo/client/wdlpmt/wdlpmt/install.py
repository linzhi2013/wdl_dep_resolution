import os
import glob
import sys
import argparse


def get_para(parser):
    # install
    parser.add_argument('-i', metavar='<file>', required=True,
        dest='pkg_gz_files_listFile', help="pkg_gz_files_listFile")


    parser.add_argument('-install_root', metavar='<directory>',
        default='./', required=True,
        help='the project_root directory [%(default)s]')

    return parser


def deal_single_pkg(pkg_gz_file, install_root='./'):
    pkg_gz_file_dir = os.path.dirname(pkg_gz_file)

    cmd = 'tar -zxvf {0} -C {1}'.format(pkg_gz_file, pkg_gz_file_dir)
    subprocess.check_call(cmd, shell=True)

    pkg_dir = pkg_gz_file.replace('.tar.gz', '')
    pkg_name = os.path.basename(pkg_gz_file).split('-', 1)[0]


    # src
    pkg_src_wdl = os.path.join(pkg_dir, 'src', 'wdl')
    project_src_deps = os.path.join(install_root, 'src', 'deps', pkg_name)

    if not os.path.exists(project_src_deps):
        os.makedirs(project_src_deps)

    if os.path.exists(pkg_src_wdl):
        cmd = 'cp -r {0}/* {1}'.format(pkg_src_wdl, project_src_deps)
        subprocess.check_call(cmd, shell=True)

    # update import paths
    update_wdl_import_paths(wdl_dir=project_src_deps, pkg_name=pkg_name)


    # doc
    pkg_doc = os.path.join(pkg_dir, 'doc')
    project_doc_deps = os.path.join(install_root, 'doc', 'deps', pkg_name)

    if not os.path.exists(project_doc_deps):
        os.makedirs(project_doc_deps)

    if os.path.exists(pkg_doc):
        cmd = 'cp -r {0}/* {1}'.format(pkg_doc, project_doc_deps)
        subprocess.check_call(cmd, shell=True)


    # docker
    pkg_docker = os.path.join(pkg_dir, 'docker')
    project_docker_deps = os.path.join(install_root, 'docker', 'deps', pkg_name)

    if not os.path.exists(project_docker_deps):
        os.makedirs(project_docker_deps)

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
            pkg_gz_file=pkg_gz_files,
            install_root=install_root)


def main(parser=None, paras=None):

    if not parser:
        parser = argparse.ArgumentParser()

    parser = get_para(parser)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args(paras)

    print(args)

    pkg_gz_files = []
    with open(args.pkg_gz_files_listFile, 'r') as fh:
        for i in fh:
            i = i.strip()
            if not i:
                continue
            pkg_gz_files.append(i)

    install_pkgs(
        pkg_gz_files=pkg_gz_files,
        install_root=args.install_root)

if __name__ == '__main__':
    main(paras=sys.argv[1:])



