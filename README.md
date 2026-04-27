# git-credential-msal

This repository contains tooling to help with git over HTTP flows using
Microsoft SSO with OIDC Id tokens. For information on how to configure the
server for this flow, please look at the [related blog
post](https://binary-eater.github.io/posts/git_oidc/).

## Dependencies

### Must be manually installed by the user

-   `git>=2.54`
    - [Installation instructions](https://git-scm.com/downloads)
      - [Linux/UNIX](https://git-scm.com/downloads/linux)
      - [Windows](https://git-scm.com/downloads/win)
      - [macOS](https://git-scm.com/downloads/mac)
    - Support for SSO authentication via the credential helper protocol was
      initially added with
      [commit c5c9acf77d](https://github.com/git/git/commit/c5c9acf77d9bced87c758e8c8aba13a438d34802),
      which first appears in
      [Git v2.46](https://github.com/git/git/blob/b31fb630c0fc6869a33ed717163e8a1210460d94/Documentation/RelNotes/2.46.0.txt#L10-L12);
      however, a bug prevented it working correctly. This bug was fixed by
      [commit ed0f7a62f7](https://github.com/git/git/commit/ed0f7a62f75232896eccb622bfaf9fe56903a261),
      which first appears in
      [Git v2.54](https://github.com/git/git/blob/94f057755b7941b321fd11fec1b2e3ca5313a4e0/Documentation/RelNotes/2.54.0.adoc?plain=1#L334-L336).

### Handled by the installation process

-   `msal-python`
-   `pyjwt`
-   `keyring`
-   `pyxdg`

## Installation

### Installing from source

``` {.bash org-language="sh"}
cd git-credential-msal
python3 -m pipx install .
```

If you run into issues with the above, first verify that the latest version of
`pipx` is installed. To avoid a conflict with the system's package manager,
installing a newer version of `pipx` in the user site-packages is recommended.

``` {.bash org-language="sh"}
python3 -m pipx install --upgrade --user pipx
```

## Setup

Run the following to have `git` utilize the credential helper.

``` {.bash org-language="sh"}
git config --global --add credential.helper msal
```

If you are only going to use this helper for a select few repos, you could
consider not using the `--global` flag.

You may want to use this helper in combination with another helper that supports
the store action. This is especially helpful if your system does not have a
keyring provider present, so you can use the auxiliary credential helper to
minimize Microsoft SSO prompts during a development session. The order is
important since you want the `cache` credential helper checked before `msal`.

**NOTE:** This does not store the cache related to the OAuth2.0 refresh token
that is stored in the keyring. This cache is useful for not needing to
re-authenticate for up to 90 days. Have a look at the Device Authorization Grant
section of the documentation for more details.

``` {.bash org-language="sh"}
git config --global --add credential.helper cache
git config --global --add credential.helper msal
```

In the situation where you are using `git` on a headless device, you may want to
use OAuth 2.0 Device Authorization Grant to do the authentication flow on a
different system. `git-credential-msal` can easily be configured to do so by
using the `-d` / `--device-code` in your `.gitconfig`.

``` conf
[credential]
    helper = msal -d
```

Many headless setups will likely not have a keyring provider such as GNOME
Keyring or KDE Wallet since such providers on Linux are heavily tied into
desktop environments. If wishing to persist the Microsoft Authentication cache
(which enables authentication persistence for up to 90 days), use the `-i` /
`--insecure` flag along with the device code flag in your `.gitconfig`.

* https://learn.microsoft.com/en-us/entra/identity-platform/refresh-tokens#token-lifetime
* https://learn.microsoft.com/en-us/entra/identity-platform/refresh-tokens#token-revocation

``` conf
[credential]
    helper = msal -d -i
```

To configure the Microsoft Entra Id application client id and tenant id that
`git-credential-msal` will use for SSO, the following commands can be used.

``` {.bash org-language="sh"}
git config --global credential.https://git.example.com.msalClientId <MSFT Entra Id App Client Id>
git config --global credential.https://git.example.com.msalTenantId <MSFT Entra Id App Tenant Id>
```

In special cases where your git server can provide a `WWW-Authenticate` HTTP
response header like below, the `git config` above will not be necessary. The
`git config` values take precedence over what is advertised by the server.

    WWW-Authenticate: Bearer msal-client-id=<MSFT Entra Id App Client Id>,msal-tenant-id=<MSFT Entra Id App Tenant Id>

`git` will feed the above HTTP header to the credential helper program to
consume.

**NOTE:** the server does need to at minimum advertise `WWW-Authenticate:
Bearer` in its initial 401 response for `git-credential-msal` to consider
forwarding the bearer token to the server.
