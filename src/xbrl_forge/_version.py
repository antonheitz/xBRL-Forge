from importlib.metadata import version, PackageNotFoundError

def retrieve_version():
    try:
        return version(__package__)
    except PackageNotFoundError:
        return "non-packaged"