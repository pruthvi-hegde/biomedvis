from django.views.generic import TemplateView


class Docs(TemplateView):

    def docs(self):
        print("Documents need to be written!!")

        return ""
