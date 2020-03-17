#!/usr/bin/env python3
import re
from semver import Version
from semver import VersionRange
from semver import parse_constraint

from mixology.constraint import Constraint
from mixology.package_source import PackageSource as BasePackageSource
from mixology.range import Range
from mixology.union import Union

from mixology.version_solver import VersionSolver

# see https://github.com/sdispater/mixology

# you need to install poetry_semver and mixology

class Dependency:

    def __init__(self, name, constraint):  # type: (str, str) -> None
        self.name = name
        self.constraint = parse_constraint(constraint)
        self.pretty_constraint = constraint

    def __str__(self):  # type: () -> str
        return self.pretty_constraint


class PackageSource(BasePackageSource):

    def __init__(self):  # type: () -> None
        self._root_version = Version.parse("0.0.0")
        self._root_dependencies = []
        self._packages = {}

        super(PackageSource, self).__init__()

    @property
    def root_version(self):
        return self._root_version

    def add(self, name, version, deps=None):  # type: (str, str, Optional[Dict[str, str]]) -> None
        if deps is None:
            deps = {}

        version = Version.parse(version)
        if name not in self._packages:
            self._packages[name] = {}

        if version in self._packages[name]:
            raise ValueError("{} ({}) already exists".format(name, version))

        dependencies = []
        for dep_name, spec in deps.items():
            dependencies.append(Dependency(dep_name, spec))

        self._packages[name][version] = dependencies

    def root_dep(self, name, constraint):  # type: (str, str) -> None
        self._root_dependencies.append(Dependency(name, constraint))

    def _versions_for(self, package, constraint=None):  # type: (Hashable, Any) -> List[Hashable]
        if package not in self._packages:
            return []

        versions = []
        for version in self._packages[package].keys():
            if not constraint or constraint.allows_any(
                Range(version, version, True, True)
            ):
                versions.append(version)

        return sorted(versions, reverse=True)

    def dependencies_for(self, package, version):  # type: (Hashable, Any) -> List[Any]
        if package == self.root:
            return self._root_dependencies

        return self._packages[package][version]

    def convert_dependency(self, dependency):  # type: (Dependency) -> Constraint
        if isinstance(dependency.constraint, VersionRange):
            constraint = Range(
                dependency.constraint.min,
                dependency.constraint.max,
                dependency.constraint.include_min,
                dependency.constraint.include_max,
                dependency.pretty_constraint,
            )
        else:
            # VersionUnion
            ranges = [
                Range(
                    range.min,
                    range.max,
                    range.include_min,
                    range.include_max,
                    str(range),
                )
                for range in dependency.constraint.ranges
            ]
            constraint = Union.of(ranges)

        return Constraint(dependency.name, constraint)



class PkgDependency(object):
    """docstring for ClassName"""
    def __init__(self, name=None, version=None, deps=None):
        super(PkgDependency, self).__init__()
        self.name = name
        self.version = version
        self.deps = deps

    def __str__(self):
        return self.name


def create_source(query_pkgs=None, all_pkg_deps=None):
    source = PackageSource()
    for pkg in query_pkgs:
        source.root_dep(pkg.name, pkg.version)

    for pkg in all_pkg_deps:
        if pkg.deps:
            source.add(pkg.name, pkg.version, pkg.deps)
        else:
            source.add(pkg.name, pkg.version)

    return source


def read_all_package_info(metadata_file=None):
    all_pkg_deps = []
    with open(metadata_file, 'r') as fh:
        for i in fh:
            i = i.strip()
            if not i:
                continue
            line = re.split(r'\s+', i, 3)
            pkg_id, pkg_name, pkg_version = line[0:3]

            dep_pkgs = {}
            if len(line) == 4:
                dep_str = line[3]
                dep = dep_str.split(',')
                for k in dep:
                    k = k.strip()
                    line2 = re.split(r'\:\s*', k, 1)
                    dep_pkg_name = line2[0]
                    dep_pkg_vesions = '>0.0'
                    if len(line2) == 2:
                        dep_pkg_vesions = line2[1]
                    dep_pkgs[dep_pkg_name] = dep_pkg_vesions

            if len(dep_pkgs) > 0:
                all_pkg_deps.append(PkgDependency(pkg_name, pkg_version, dep_pkgs))
            else:
                all_pkg_deps.append(PkgDependency(pkg_name, pkg_version))

    return all_pkg_deps



def pkg_verison_solver(metadata_file=None, query_pkg_version=None):
    '''
    wdl_package_info content format:
    pkg_id1    hello   1.0 python:=3.7, perl:<6 >5, c:<2
    pkg_id2    c 1.2 python

    query_pkg_version:
        is a dictionary. pkg name is the key, version is the value

    Return:
        A ordered dictionary object. The installing order should be reversed.
    '''

    all_pkg_deps = read_all_package_info(metadata_file)
    query_pkgs = []
    for query_pkg, version in query_pkg_version.items():
        query_pkgs.append(PkgDependency(query_pkg, version))

    source = create_source(query_pkgs, all_pkg_deps)
    solver = VersionSolver(source)
    result = solver.solve()

    return result


if __name__ == '__main__':
    print('Please read the code!')
    #result = pkg_verison_solver(
    #    metadata_file='wdl_package_info.txt',
    #    query_pkg_version={"hic": "1.0"})


    #print(result.decisions)



'''
all_pkg_deps = [
PkgDependency("a", "1.0.0", {"shared": ">=2.0.0 <4.0.0"}),
PkgDependency("b", "1.0.0", {"shared": ">=3.0.0 <5.0.0"}),
PkgDependency("shared", "2.0.0"),
PkgDependency("shared", "3.0.0"),
PkgDependency("shared", "3.6.9"),
PkgDependency("shared", "4.0.0"),
PkgDependency("shared", "5.0.0"),
]

query_pkgs = [
PkgDependency("a", "1.0.0"),
PkgDependency("b", "1.0.0"),
]

source = create_source(query_pkgs, all_pkg_deps)


solver = VersionSolver(source)
result = solver.solve()
print(result.decisions)
# {Package("_root_"): <Version 0.0.0>, 'b': <Version 1.0.0>, 'a': <Version 1.0.0>, 'shared': <Version 3.6.9>}
print(result.attempted_solutions)
# 1
'''
