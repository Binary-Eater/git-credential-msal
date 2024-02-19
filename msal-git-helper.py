# Given the client ID and tenant ID for an app registered in Azure,
# provide a <ms-entra-id> access token and a refresh token.

# If the caller is not already signed in to Azure, the caller's
# web browser will prompt the caller to sign in first.

# pip install msal
from msal import PublicClientApplication
from msal import SerializableTokenCache
import sys

# You can hard-code the registered app's client ID and tenant ID here,
# or you can provide them as command-line arguments to this script.
client_id = '<client-id>'
tenant_id = '<tenant-id>'

# Do not modify this variable. It represents the programmatic ID for
# Azure Databricks along with the default scope of '/.default'.
scopes = [ 'email openid User.Read' ]

# Check for too few or too many command-line arguments.
if (len(sys.argv) > 1) and (len(sys.argv) != 3):
  print("Usage: msal-git-helper.py <client ID> <tenant ID>")
  exit(1)

# If the registered app's client ID and tenant ID are provided as
# command-line variables, set them here.
if len(sys.argv) > 1:
  client_id = sys.argv[1]
  tenant_id = sys.argv[2]

cache = SerializableTokenCache()

app = PublicClientApplication(
  client_id = client_id,
  authority = "https://login.microsoftonline.com/" + tenant_id,
  token_cache = cache
)

acquire_tokens_result = app.acquire_token_interactive(
  scopes = scopes
)

if 'error' in acquire_tokens_result:
  print("Error: " + acquire_tokens_result['error'], file=sys.stderr)
  print("Description: " + acquire_tokens_result['error_description'], file=sys.stderr)
else:
  accounts = app.get_accounts()
  account = accounts[0]

  # OIDC Id token
  id_token = cache.find(cache.CredentialType.ID_TOKEN, query={
                       "home_account_id": account['home_account_id'],
                   })[0]['secret']

  print(id_token, end='')
