import sys

from setuptools import setup, find_packages


def get_version() -> str:
    version = {}
    path_to_file_with_version = "time_tracker_api/version.py"
    try:
        with open(path_to_file_with_version) as fp:
            exec(fp.read(), version)
        __version__ = version['__version__']
        return __version__
    except KeyError:
        print(f'Error: No variable ___version___ in {path_to_file_with_version}')
        sys.exit()


setup(
    name="time-tracker-backend",
    version=get_version(),
    packages=find_packages(),
    include_package_data=True,
)
