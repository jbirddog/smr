"""Test_authentication."""
import base64
import json

import requests
from flask.app import Flask
from keycloak.authorization import Authorization  # type: ignore
from keycloak.keycloak_openid import KeycloakOpenID  # type: ignore
from keycloak.uma_permissions import AuthStatus  # type: ignore
from tests.spiffworkflow_backend.integration.base_test import BaseTest


class TestAuthentication(BaseTest):
    """TestAuthentication."""

    # def test_get_basic_token(self, app: Flask) -> None:
    #     for user_id in ('user_1', 'user_2', 'admin_1', 'admin_2'):
    #         basic_token = self.get_public_access_token(user_id, user_id)
    #         assert isinstance(basic_token, dict)
    #         assert 'access_token' in basic_token
    #         assert isinstance(basic_token['access_token'], str)
    #         assert 'refresh_token' in basic_token
    #         assert isinstance(basic_token['refresh_token'], str)
    #         assert 'token_type' in basic_token
    #         assert basic_token['token_type'] == 'Bearer'
    #         assert 'scope' in basic_token
    #         assert isinstance(basic_token['scope'], str)

    def test_get_token_script(self, app: Flask) -> None:
        """Test_get_token_script."""
        print("Test Get Token Script")

        (
            keycloak_server_url,
            keycloak_client_id,
            keycloak_realm_name,
            keycloak_client_secret_key,
        ) = self.get_keycloak_constants(app)
        keycloak_user = "ciuser1"
        keycloak_pass = "ciuser1"

        print(f"Test Get Token Script: keycloak_server_url: {keycloak_server_url}")
        print(f"Test Get Token Script: keycloak_client_id: {keycloak_client_id}")
        print(f"Test Get Token Script: keycloak_realm_name: {keycloak_realm_name}")
        print(
            f"Test Get Token Script: keycloak_client_secret_key: {keycloak_client_secret_key}"
        )

        frontend_client_id = "spiffworkflow-frontend"

        print(f"Test Get Token Script: frontend_client_id: {frontend_client_id}")

        # Get frontend token
        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        post_data = {
            "grant_type": "password",
            "username": keycloak_user,
            "password": keycloak_pass,
            "client_id": frontend_client_id,
        }
        print(f"Test Get Token Script: request_url: {request_url}")
        print(f"Test Get Token Script: headers: {headers}")
        print(f"Test Get Token Script: post_data: {post_data}")

        frontend_response = requests.post(
            request_url, headers=headers, json=post_data, data=post_data
        )
        frontend_token = json.loads(frontend_response.text)

        print(f"Test Get Token Script: frontend_response: {frontend_response}")
        print(f"Test Get Token Script: frontend_token: {frontend_token}")

        # assert isinstance(frontend_token, dict)
        # assert isinstance(frontend_token["access_token"], str)
        # assert isinstance(frontend_token["refresh_token"], str)
        # assert frontend_token["expires_in"] == 300
        # assert frontend_token["refresh_expires_in"] == 1800
        # assert frontend_token["token_type"] == "Bearer"

        # Get backend token
        BACKEND_BASIC_AUTH_STRING = f"{keycloak_client_id}:{keycloak_client_secret_key}"
        BACKEND_BASIC_AUTH_BYTES = bytes(BACKEND_BASIC_AUTH_STRING, encoding="ascii")
        BACKEND_BASIC_AUTH = base64.b64encode(BACKEND_BASIC_AUTH_BYTES)

        request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {BACKEND_BASIC_AUTH.decode('utf-8')}",
        }
        data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "client_id": keycloak_client_id,
            "subject_token": frontend_token["access_token"],
            "audience": keycloak_client_id,
        }
        print(f"Test Get Token Script: request_url: {request_url}")
        print(f"Test Get Token Script: headers: {headers}")
        print(f"Test Get Token Script: data: {data}")

        backend_response = requests.post(request_url, headers=headers, data=data)
        json_data = json.loads(backend_response.text)
        backend_token = json_data["access_token"]
        print(f"Test Get Token Script: backend_response: {backend_response}")
        print(f"Test Get Token Script: backend_token: {backend_token}")

        if backend_token:
            # Getting resource set
            auth_bearer_string = f"Bearer {backend_token}"
            headers = {
                "Content-Type": "application/json",
                "Authorization": auth_bearer_string,
            }

            # URI_TO_TEST_AGAINST = "%2Fprocess-models"
            URI_TO_TEST_AGAINST = "/status"
            request_url = (
                f"{keycloak_server_url}/realms/{keycloak_realm_name}/authz/protection/resource_set?"
                + f"matchingUri=true&deep=true&max=-1&exactName=false&uri={URI_TO_TEST_AGAINST}"
            )
            # f"uri={URI_TO_TEST_AGAINST}"
            print(f"Test Get Token Script: request_url: {request_url}")
            print(f"Test Get Token Script: headers: {headers}")

            resource_result = requests.get(request_url, headers=headers)
            print(f"Test Get Token Script: resource_result: {resource_result}")

            json_data = json.loads(resource_result.text)
            resource_id_name_pairs = []
            for result in json_data:
                if "_id" in result and result["_id"]:
                    pair_key = result["_id"]
                    if "name" in result and result["name"]:
                        pair_value = result["name"]
                        # pair = {{result['_id']}: {}}
                    else:
                        pair_value = "no_name"
                        # pair = {{result['_id']}: }
                    pair = [pair_key, pair_value]
                    resource_id_name_pairs.append(pair)
            print(
                f"Test Get Token Script: resource_id_name_pairs: {resource_id_name_pairs}"
            )

            # Getting Permissions
            for resource_id_name_pair in resource_id_name_pairs:
                resource_id = resource_id_name_pair[0]
                resource_id_name_pair[1]

                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {BACKEND_BASIC_AUTH.decode('utf-8')}",
                }

                post_data = {
                    "audience": keycloak_client_id,
                    "permission": resource_id,
                    "subject_token": backend_token,
                    "grant_type": "urn:ietf:params:oauth:grant-type:uma-ticket",
                }
                print(f"Test Get Token Script: headers: {headers}")
                print(f"Test Get Token Script: post_data: {post_data}")
                print(f"Test Get Token Script: request_url: {request_url}")

                permission_result = requests.post(
                    request_url, headers=headers, data=post_data
                )
                print(f"Test Get Token Script: permission_result: {permission_result}")

        print("test_get_token_script")

    # def test_auth_endpoint(self, app: Flask) -> None:
    #     keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = self.get_keycloak_constants(app)
    #     request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/auth"


# class TestOtherStuff(BaseTest):
#
#     # def test_get_backend_token(self, app: Flask) -> None:
#     #     frontend_client_id = 'spiffworkflow-frontend'
#     #     keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = self.get_keycloak_constants(app)
#     #     keycloak_user = 'ciuser1'
#     #     keycloak_pass = 'ciuser1'
#     #
#     #     request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"
#     #     headers = {"Content-Type": "application/x-www-form-urlencoded"}
#     #     post_data = {'grant_type': 'password',
#     #                  'username': keycloak_user,
#     #                  'password': keycloak_pass,
#     #                  'client_id': frontend_client_id
#     #                  }
#     #
#     #     r = requests.post(request_url, headers=headers, json=post_data, data=post_data)
#     #     front_end_token = json.loads(r.text)
#     #
#     #
#     #     BACKEND_CLIENT_SECRET = "JXeQExm0JhQPLumgHtIIqf52bDalHz0q"  # noqa: S105
#     #     BACKEND_BASIC_AUTH = base64.b64encode(bytes(f"{keycloak_client_id}:{BACKEND_CLIENT_SECRET}", encoding='UTF-8'))
#     #     # BACKEND_BASIC_AUTH = f"{keycloak_client_id}:{BACKEND_CLIENT_SECRET}"
#     #
#     #     request_url = f"{keycloak_server_url}/realms/{keycloak_realm_name}/protocol/openid-connect/token"
#     #
#     #     headers = {
#     #         "Content-Type": "application/x-www-form-urlencoded",
#     #         "Authorization": f"Basic {BACKEND_BASIC_AUTH}"}
#     #     post_data = {'grant_type': "urn:ietf:params:oauth:grant-type:token-exchange",
#     #                  'client_id': keycloak_client_id,
#     #                  'subject_token': front_end_token['access_token'],
#     #                  'audience': keycloak_client_id
#     #                  }
#     #     # result =$(curl - s - X POST "$KEYCLOAK_URL" "$INSECURE" \
#     #     #     -H "Content-Type: application/x-www-form-urlencoded" \
#     #     #     --data-urlencode 'grant_type=urn:ietf:params:oauth:grant-type:token-exchange' \
#     #     #     -d "client_id=$BACKEND_CLIENT_ID" \
#     #     #     -d "subject_token=${frontend_token}" \
#     #     #     -H "Authorization: Basic $BACKEND_BASIC_AUTH" \
#     #     #     -d "audience=${BACKEND_CLIENT_ID}" \
#     #     #           )
#     #
#     #     r = requests.post(request_url, headers=headers, data=post_data)
#     #     token = json.loads(r.text)
#     #
#     #     print("test_get_backend_token: ")
#
# # >>> import requests
# # >>> r = requests.post('http://httpbin.org/post', json={"key": "value"})
# # >>> r.status_code
# # 200
# # >>> r.json()
# # {'args': {},
# #  'data': '{"key": "value"}',
# #  'files': {},
# #  'form': {},
# #  'headers': {'Accept': '*/*',
# #              'Accept-Encoding': 'gzip, deflate',
# #              'Connection': 'close',
# #              'Content-Length': '16',
# #              'Content-Type': 'application/json',
# #              'Host': 'httpbin.org',
# #              'User-Agent': 'python-requests/2.4.3 CPython/3.4.0',
# #              'X-Request-Id': 'xx-xx-xx'},
# #  'json': {'key': 'value'},
# #  'origin': 'x.x.x.x',
# #  'url': 'http://httpbin.org/post'}
#
#     def test_get_keycloak_openid_client(self, app: Flask) -> None:
#         """Test_get_keycloak_openid_client."""
#         keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = self.get_keycloak_constants(app)
#         keycloak_openid_client = KeycloakAuthenticationService.get_keycloak_openid(
#             keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key
#         )
#         assert isinstance(keycloak_openid_client, KeycloakOpenID)
#         assert isinstance(keycloak_openid_client.authorization, Authorization)
#         assert keycloak_openid_client.client_id == keycloak_client_id
#         assert keycloak_openid_client.realm_name == keycloak_realm_name
#
#     def test_get_keycloak_token(self, app: Flask) -> None:
#         """Test_get_keycloak_token."""
#         keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = self.get_keycloak_constants(app)
#         keycloak_openid = KeycloakAuthenticationService.get_keycloak_openid(
#             keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key
#         )
#         token = keycloak_openid.token('ciadmin1', 'ciadmin1')
#         token = keycloak_openid.refresh_token(token['refresh_token'])
#         assert isinstance(token, dict)
#         assert isinstance(token["access_token"], str)
#         assert isinstance(token["refresh_token"], str)
#         assert token["expires_in"] == 300
#         assert token["refresh_expires_in"] == 1800
#         assert token["token_type"] == "Bearer"
#
#     # def test_get_permission_by_token(self, app: Flask) -> None:
#     #     """Test_get_permission_by_token."""
#     #     keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = self.get_keycloak_constants(app)
#     #     keycloak_openid = AuthenticationService.get_keycloak_openid(
#     #         keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key
#     #     )
#     #     keycloak_openid.load_authorization_config(
#     #         "bin/spiffworkflow-realm.json"
#     #     )
#     #     token = keycloak_openid.token(user, password)
#     #
#     #     permissions = AuthenticationService.get_permission_by_token(keycloak_openid, token)
#     #     # TODO: permissions comes back as None. Is this right?
#     #     print(f"test_get_permission_by_token: {permissions}")
#
#     def test_get_uma_permissions_by_token(self, app: Flask) -> None:
#         """Test_get_uma_permissions_by_token."""
#         keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = self.get_keycloak_constants(app)
#         keycloak_openid = KeycloakAuthenticationService.get_keycloak_openid(
#             keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key
#         )
#         for user_id in ('ciadmin1', 'ciuser1'):
#             token = keycloak_openid.token(user_id, user_id)
#             uma_permissions = KeycloakAuthenticationService.get_uma_permissions_by_token(
#                 keycloak_openid, token
#             )
#             assert isinstance(uma_permissions, list)
#             # assert len(uma_permissions) == 2
#             for permission in uma_permissions:
#                 assert "rsname" in permission
#                 if permission["rsname"] == "View Account Resource":
#                     assert "scopes" in permission
#                     assert isinstance(permission["scopes"], list)
#                     assert len(permission["scopes"]) == 1
#                     assert permission["scopes"][0] == "account:view"
#
# def test_get_uma_permissions_by_token_for_resource_and_scope(self, app: Flask) -> None:
#     """Test_get_uma_permissions_by_token_for_resource_and_scope."""
#     keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = self.get_keycloak_constants(app)
#     keycloak_openid = KeycloakAuthenticationService.get_keycloak_openid(
#         keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key
#     )
#     token = keycloak_openid.token('admin_1', 'admin_1')
#     resource = "Process Groups"
#     scope = "read"
#
#     permissions = (
#         KeycloakAuthenticationService.get_uma_permissions_by_token_for_resource_and_scope(
#             keycloak_openid, token, resource, scope
#         )
#     )
#     assert isinstance(permissions, list)
#     # assert len(permissions) == 1
#     assert isinstance(permissions[0], dict)
#     permission = permissions[0]
#     assert "rsname" in permission
#     assert permission["rsname"] == resource
#     assert "scopes" in permission
#     assert isinstance(permission["scopes"], list)
#     assert len(permission["scopes"]) == 1
#     assert permission["scopes"][0] == scope
#
#     print("test_get_uma_permissions_by_token_for_resource_and_scope")
#
#     def test_get_auth_status_for_resource_and_scope_by_token(self, app: Flask) -> None:
#         """Test_get_auth_status_for_resource_and_scope_by_token."""
#         keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = self.get_keycloak_constants(app)
#         keycloak_openid = KeycloakAuthenticationService.get_keycloak_openid(
#             keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key
#         )
#         for user in ('ciuser1', 'ciadmin1'):
#             token = keycloak_openid.token(user, user)
#             resource = "everything"
#             scope = "read"
#             auth_status = KeycloakAuthenticationService.get_auth_status_for_resource_and_scope_by_token(
#                 keycloak_openid, token, resource, scope
#             )
#             assert isinstance(auth_status, AuthStatus)
#             assert auth_status.is_logged_in is True
#             # assert auth_status.is_authorized is True
# #
# #     def test_get_keycloak_admin(self, app: Flask) -> None:
# #         admin_user = 'ciadmin1'
# #         keycloak_admin = AuthenticationService.get_keycloak_admin(admin_user)
# #         print(f"test_get_keycloak_admin: {keycloak_admin}")
# # #
# # #
# # # # def test_keycloak_admin(app: Flask, client: FlaskClient) -> None:
# # # #     realm = 'stackoverflow-demo'
# # # #     result = app.get(f"/{realm}/authentication/client-authenticator-providers")
# # # #     print(f"test_keycloak_admin: {result}")
# #
# #     def test_my_new_idea(self, app: Flask) -> None:
# #         keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key = self.get_keycloak_constants(app)
# #         keycloak_openid = AuthenticationService.get_keycloak_openid(
# #             keycloak_server_url, keycloak_client_id, keycloak_realm_name, keycloak_client_secret_key
# #         )
# #         token = keycloak_openid.token('ciadmin1', 'ciadmin1')
# #         # token = keycloak_openid.refresh_token(token['refresh_token'])
# #         userinfo = keycloak_openid.userinfo(token['access_token'])
# #
# #         rpt = keycloak_openid.entitlement(token['access_token'], 'spiffworkflow-backend')
# #         token_info = keycloak_openid.introspect(token['access_token'])
# #
# #         print("test_my_new_idea")
