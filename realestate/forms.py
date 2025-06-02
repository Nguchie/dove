from django import forms
from django.utils.safestring import mark_safe

class MultipleFileInput(forms.ClearableFileInput):
    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs['multiple'] = 'multiple'
        return super().render(name, value, attrs, renderer)

class BulkImageUploadForm(forms.Form):
    images = forms.FileField(
        widget=MultipleFileInput(),
        label="Upload multiple images",
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['images'].widget.attrs.update({'class': 'file-upload'})

    def clean_images(self):
        files = self.files.getlist('images')
        if not files:
            raise forms.ValidationError("Please upload at least one image.")
        for file in files:
            if not file.content_type.startswith('image/'):
                raise forms.ValidationError("Only image files are allowed.")
        return files


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=False)
    description = forms.CharField(widget=forms.Textarea)