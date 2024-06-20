from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("git_credential_msal")
except PackageNotFoundError:
    # package is not installed
    pass
