import jinja2

def assign_values_to_templates(input_data, template_data, yaml_template, yaml_file):
    # Load the Jinja2 environment
    env = jinja2.Environment(loader=jinja2.BaseLoader())

    # Iterate over the keys in the input data
    for key, values in input_data.items():
        # Skip keys that don't have multiple values
        if not isinstance(values, list) or len(values) < 2:
            continue

        # Iterate over the values and assign them to templates
        for index, value in enumerate(values):
            # Check if the corresponding templates and files exist
            if index < len(yaml_template) and index < len(yaml_file):
                template_name = yaml_template[index]
                file_name = yaml_file[index]

                # Load the template
                template = env.get_template(template_name)

                # Render the template with the current value
                rendered_content = template.render(value=value)

                # Use the rendered content as desired (e.g., write to a file, send as output, etc.)
                print(f"Value: {value}")
                print(f"Template Name: {template_name}")
                print(f"File Name: {file_name}")
                print(f"Rendered Content: {rendered_content}")
                print("-----")

# Example input data
input_data = {
    "teamName": ["prod", "uat", "francis"],
    "environment": "tiacourses-dev",
    "project": "dev"
}

# Example template data
template_data = [
    "Template 1: {{ value }}",
    "Template 2: {{ value }}",
    "Template 3: {{ value }}"
]

# Assign values to templates
assign_values_to_templates(input_data, template_data)
