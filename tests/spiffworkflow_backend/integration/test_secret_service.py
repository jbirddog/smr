from flask.app import Flask
from flask.testing import FlaskClient

from spiffworkflow_backend.models.secret_model import SecretModel, SecretAllowedProcessPathModel
from spiffworkflow_backend.services.file_system_service import FileSystemService
from spiffworkflow_backend.services.process_model_service import ProcessModelService
from spiffworkflow_backend.services.secret_service import SecretService
from tests.spiffworkflow_backend.helpers.base_test import BaseTest


class TestSecretService(BaseTest):

    test_service = 'test_service'
    test_client = 'test_client'
    test_key = '1234567890'

    def add_test_secret(self, user):
        return SecretService().add_secret(self.test_service, self.test_client, self.test_key, user.id)

    def test_add_secret(self, app: Flask, with_db_and_bpmn_file_cleanup: None):
        user = self.find_or_create_user()
        test_secret = self.add_test_secret(user)

        assert test_secret is not None
        assert test_secret.service == self.test_service
        assert test_secret.client == self.test_client
        assert test_secret.key == self.test_key
        assert test_secret.creator_user_id == user.id

    def test_get_secret(self, app: Flask, with_db_and_bpmn_file_cleanup: None):
        user = self.find_or_create_user()
        self.add_test_secret(user)

        secret = SecretService().get_secret(self.test_service, self.test_client)
        assert secret is not None
        assert secret == self.test_key

    def test_get_secret_bad_service(self, app: Flask, with_db_and_bpmn_file_cleanup: None):
        user = self.find_or_create_user()
        self.add_test_secret(user)

        bad_secret = SecretService().get_secret('bad_service', self.test_client)
        assert bad_secret is None

    def test_get_secret_bad_client(self, app: Flask, with_db_and_bpmn_file_cleanup: None):
        user = self.find_or_create_user()
        self.add_test_secret(user)

        bad_secret = SecretService().get_secret(self.test_service, 'bad_client')
        assert bad_secret is None

    def test_secret_add_allowed_process(self, app: Flask, client: FlaskClient, with_db_and_bpmn_file_cleanup: None):
        process_group_id = "test"
        process_group_display_name = "My Test Process Group"

        user = self.find_or_create_user()
        self.create_process_group(
            client, user, process_group_id, display_name=process_group_display_name
        )

        process_model_id = "make_cookies"
        process_model_display_name = "Cooooookies"
        process_model_description = "Om nom nom delicious cookies"
        self.create_process_model(
            client,
            process_group_id=process_group_id,
            process_model_id=process_model_id,
            process_model_display_name=process_model_display_name,
            process_model_description=process_model_description,
        )

        process_model_info = ProcessModelService().get_process_model(process_model_id, process_group_id)
        process_model_relative_path = FileSystemService.process_model_relative_path(process_model_info)

        test_secret = self.add_test_secret(user)
        allowed_process_model = SecretService().add_allowed_process(secret_id=test_secret.id,
                                                                    allowed_relative_path=process_model_relative_path)
        assert allowed_process_model is not None
        assert isinstance(allowed_process_model, SecretAllowedProcessPathModel)
        assert allowed_process_model.secret_id == test_secret.id
        assert allowed_process_model.allowed_relative_path == process_model_relative_path

        assert len(test_secret.allowed_processes) == 1
        assert test_secret.allowed_processes[0] == allowed_process_model

    def test_update_secret(self):
        ...

    def test_delete_secret(self):
        ...
