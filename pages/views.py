from django.views.generic import TemplateView


class Index(TemplateView):
    template_name = 'pages/index.html'


class Todoes(TemplateView):
    template_name = 'pages/todoes.html'


class BizCase(TemplateView):
    template_name = 'pages/bizcase.html'


class ToDo2(TemplateView):
    template_name = 'pages/todo-2.html'
