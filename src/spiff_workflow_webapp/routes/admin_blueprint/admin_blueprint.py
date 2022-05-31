"""APIs for dealing with process groups, process models, and process instances."""
from typing import Any

from flask import Blueprint, render_template
from flask_bpmn.models.db import db
from flask import request

from spiff_workflow_webapp.models.user import UserModel
from spiff_workflow_webapp.services.process_instance_processor import ProcessInstanceProcessor
from spiff_workflow_webapp.services.process_instance_service import ProcessInstanceService
from spiff_workflow_webapp.services.spec_file_service import SpecFileService
from spiff_workflow_webapp.services.process_model_service import ProcessModelService

admin_blueprint = Blueprint("admin", __name__, template_folder='templates', static_folder='static')


@admin_blueprint.route("/process-models/<process_model_id>/run", methods=["GET"])
def process_model_run(process_model_id):
    """Process_model_run."""
    user = find_or_create_user('Mr. Test')  # Fixme - sheesh!
    process_instance = ProcessInstanceService.create_process_instance(process_model_id, user)
    processor = ProcessInstanceProcessor(process_instance)
    processor.do_engine_steps()
    result = processor.get_data()

    process_model = ProcessModelService().get_spec(process_model_id)
    SpecFileService.get_files(process_model)
    bpmn_xml = SpecFileService.get_data(process_model, process_model.primary_file_name)

    return render_template('process_model_show.html', process_model=process_model, bpmn_xml=bpmn_xml, result=result)


@admin_blueprint.route("/process_models/<process_model_id>/edit", methods=["GET"])
def process_model_edit(process_model_id):
    """Edit_bpmn."""
    process_model = ProcessModelService().get_spec(process_model_id)
    SpecFileService.get_files(process_model)
    bpmn_xml = SpecFileService.get_data(process_model, process_model.primary_file_name)

    return render_template('process_model_edit.html', bpmn_xml=bpmn_xml.decode("utf-8"),
                           process_model=process_model)


@admin_blueprint.route("/process-models/<process_model_id>/save", methods=["POST"])
def process_model_save(process_model_id):
    """Process_model_save."""
    process_model = ProcessModelService().get_spec(process_model_id)
    SpecFileService.get_files(process_model, process_model.primary_file_name)
    SpecFileService.update_file(process_model, process_model.primary_file_name, request.get_data())
    bpmn_xml = SpecFileService.get_data(process_model, process_model.primary_file_name)
    return render_template('process_model_edit.html', bpmn_xml=bpmn_xml.decode("utf-8"),
                           process_model=process_model)


@admin_blueprint.route("/process-models/<process_model_id>/<file_id>", methods=["GET"])
def process_model_show_file(process_model_id, file_id):
    """Process_model_show_file."""
    process_model = ProcessModelService().get_spec(process_model_id)
    SpecFileService.get_files(process_model)
    bpmn_xml = SpecFileService.get_data(process_model, file_id)
    return render_template('process_model_show.html', process_model=process_model, bpmn_xml=bpmn_xml)


@admin_blueprint.route("/process-groups/<process_group_id>", methods=["GET"])
def process_group_show(process_group_id):
    """Show_process_group."""
    process_group = ProcessModelService().get_process_group(process_group_id)
    return render_template('process_group_show.html', process_group=process_group)


@admin_blueprint.route("/process-groups", methods=["GET"])
def process_groups_list():
    """Process_groups_list."""
    process_groups = ProcessModelService().get_process_groups()
    return render_template('process_groups_list.html', process_groups=process_groups)


@admin_blueprint.route("/process-models/<process_model_id>", methods=["GET"])
def process_model_show(process_model_id):
    """Show_process_model."""
    process_model = ProcessModelService().get_spec(process_model_id)
    bpmn_xml = SpecFileService.get_data(process_model, process_model.primary_file_name)
    return render_template('process_model_show.html', process_model=process_model, bpmn_xml=bpmn_xml)


def find_or_create_user(username: str = "test_user1") -> Any:
    """Find_or_create_user."""
    user = UserModel.query.filter_by(username=username).first()
    if user is None:
        user = UserModel(username=username)
        db.session.add(user)
        db.session.commit()
    return user
