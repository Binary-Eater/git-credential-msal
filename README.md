# git-credential-msal

This repository contains tooling to help with git over HTTP flows using
Microsoft SSO with OIDC Id tokens. For information on how to configure the
server for this flow, please look at the [related blog
post](https://binary-eater.github.io/posts/git_oidc/).

## Dependencies

Required dependencies

-   `msal-python`
-   `pyjwt`
-   `keyring`
-   `pyxdg`

## Setup

Run the following to have `git` utilize the credential helper.

``` {.bash org-language="sh"}
git config --global --add credential.helper msal
```

If you are only going to use this helper for a select few repos, you could
consider not using the `--global` flag.

You may want to use this helper in combination with another helper that supports
the store action.

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
