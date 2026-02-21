# Simple string replacement template engine for MicroPython
# Usage: render_template(template_str, context_dict)

def render_template(template, context):
    """
    Replace {{key}} in template with context['key'] as string.
    Example:
        template = "Hello, {{name}}!"
        context = {"name": "World"}
        result = render_template(template, context)  # "Hello, World!"
    """
    result = template
    for key, value in context.items():
        result = result.replace("{{" + key + "}}", str(value))
    return result

# Example usage
if __name__ == "__main__":
    tpl = "Temperature: {{temp}} {{unit}}"
    ctx = {"temp": 72, "unit": "F"}
    print(render_template(tpl, ctx))
