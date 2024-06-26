import jinja2

from module.directory import Directory


class TemplateRender:
    def __init__(self, template_dir=Directory.TEMPLATES.value):
        self._template_dir = template_dir
        self._env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    
    @property
    def template_dir(self):
        return self._template_dir

    @template_dir.setter
    def template_dir(self, new_template_dir):
        self._template_dir = new_template_dir
        self._env = jinja2.Environment(loader=jinja2.FileSystemLoader(new_template_dir))
    
    def render_template(self, template_name, context={}, **kwargs):
        template = self._env.get_template(template_name)
        if not context:
            context = kwargs
        return template.render(context)
