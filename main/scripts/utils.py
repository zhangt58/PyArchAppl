import json
import sys
from types import SimpleNamespace


class SimpleNamespaceEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SimpleNamespace):
            return vars(obj)
        return super().default(obj)


def get_dependency_version(package_name: str) -> str | None:
    """Get the version of a dependency package, compatible with Python 3.9-3.13."""
    try:
        if sys.version_info >= (3, 8):
            try:
                from importlib.metadata import version, PackageNotFoundError
            except ImportError:
                from importlib_metadata import version, PackageNotFoundError  # type: ignore
            return version(package_name)
        else:
            import pkg_resources
            return pkg_resources.get_distribution(package_name).version
    except Exception:
        return None


def get_essential_deps_info() -> list[tuple[str, str]]:
    """ Return a list of essential dependencies and their versions."""
    essential_packages = [
        'pandas',
        'numpy',
        'openpyxl',
        'tables',
        'protobuf'
    ]

    deps = []
    for pkg in essential_packages:
        version = get_dependency_version(pkg)
        if version is not None:
            deps.append((pkg, version))
        else:
            deps.append((pkg, 'Not installed'))

    return deps


def print_deps():
    deps = get_essential_deps_info()
    print("Essential dependencies:")
    print(json.dumps(dict(deps), indent=2))


def print_site_config():
    from archappl.config import SITE_CONFIG
    print(f"Site configuration:")
    print(json.dumps(SITE_CONFIG, indent=2))
