import unittest, os
from unittest import mock , TestCase
from mock import patch
from st2client.client import Client
from st2tests.base import BaseActionTestCase
from generate_template import TemplateGenarator

__all__ = [
    'TemplateGenaratorTestCase'
]

template_input = {
        "business_unit":"R&D Tech",
        "solution_group":"Emerging Tech, Architecture, & AI",
        "product_family":"Quality Engineering & Design",
        "product_name":"DevSecOps",
        "azure_organization":"DevOps-RD",
        "azure_projects":"Pipeline Generator - QED DevSecOps",
        "project_identifier":"sprint64_test_4",
        "tech_stack":"java",
        "stack_build_tool":"maven",
        "stack_unittest_tool":"pytest",
        "docker_build":"True",
        "azure_artifacts":"True",
        "deployment_tool":"kubernetes",
        "functional_test_tool":"torchbearer",
        "performance_test_tool":"jmeter",
        "api_test_tool":"postman",
        "security_test_tool":"owasp_zap",
        "sonarqube":"True",
        "sonarqube_project_key":"sprint64_test4",
        "blackduck":"True",
        "trivy_repo_scan":"False",
        "trivy_image_scan":"True",
        "ms_teams_notification":"True",
        "publish_test_metrics":"True",
        "github_target_repository_branch":"main",
        "ms_team_webhook_url":"none",
        "existing_github_repository":"none",
        "pipegen_acr_registry":"pipegenframework.azurecr.io",
        "blackduck_project":"rd-sprint64_test_4",
        "existing_blackduck_project_version":"v1.0.0"
    }
template_source_path = "/opt/stackstorm/packs/jinja/templates/pipegen"
template_files = {
        "azure-pipeline.j2": ".cicd/azure-pipeline.yaml",
        "publish_tag.j2": ".cicd/publish_tag.yaml",
        "deployment.j2": ".cicd/deployment.yaml",
        "testing_capability.j2": ".cicd/testing_capability.yaml",
        "composition_analysis.j2": ".cicd/composition_analysis.yaml",
        "static_code_analysis.j2": ".cicd/static_code_analysis.yaml",
        "teams_notification.j2": ".cicd/teams_notification.yaml",
        "variables.j2": ".cicd/variables.yaml",
        "readme.j2": ".cicd/README.md",
        "sonar-project.properties.j2": ".cicd/sonar-project.properties"
    }
template_target_path = "/packs-workdir/pipegen/pipelinefiles"

class TemplateGenaratorTestCase(BaseActionTestCase):
    action_cls = TemplateGenarator
    def test_run_generate_template(self):
       result = self.get_action_instance().run(template_input, template_source_path, template_files, template_target_path)
       expected = { "action_flag": True }
       self.assertEqual(result, expected)
    # def test_run_generate_template(self):
    #     with patch('actions.generate_template.TemplateGenarator') as mock:
    #         instance = mock.return_value
    #         instance.run.return_value = { "action_flag": True }
    #         actual = instance.run(template_input, template_source_path, template_files, template_target_path)
    #         self.assertEqual(actual, instance.run.return_value)