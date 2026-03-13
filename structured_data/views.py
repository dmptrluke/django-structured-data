class StructuredDataMixin:
    def get_structured_data(self):
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.get_structured_data()
        if data is not None:
            context['structured_data'] = data
        return context
