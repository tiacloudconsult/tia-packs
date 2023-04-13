from st2common.runners.base_action import Action
from jinja2 import FileSystemLoader, Environment, TemplateNotFound
import os
import json
import logging, sys#, ecs_logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
#handler.setFormatter(ecs_logging.StdlibFormatter())
logger.addHandler(handler)


__all__ = [
    'TemplateGenarator'
]

class TemplateGenarator(Action):
	def run(self, template_input, template_source_path, template_files, template_target_path):
		try:
			file_loader = FileSystemLoader(searchpath=template_source_path)
			env = Environment(loader=file_loader, trim_blocks=True, lstrip_blocks=True)

			for source_template_file, target_template_file in template_files.items():
				# Get Jinja template from source directory or file
				print(source_template_file)
				template = env.get_template(source_template_file)

				# Render Jinja template
				rendered_output = template.render(template_input)

				# Write rendered content to a file
				target_file = template_target_path + "/" + target_template_file
				os.makedirs(os.path.dirname(target_file), 0o777, exist_ok=True)
				os.chmod(template_target_path, 0o777)
				with open(target_file, "w+") as file:
					file.write(rendered_output)
			
			response_payload = {
				"action_flag": True
			}    
			return response_payload
		except Exception as e:
			print("Error:", e)
			logger.exception("Error:", e)
			response_payload = {
				"action_flag": False,
				"error_message": e
			}
			return response_payload