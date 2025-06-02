from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from .models import Post, PostSection

class LimitedSectionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if len([form for form in self.forms if not form.cleaned_data.get('DELETE', False)]) > 4:
            raise ValidationError("You can only add up to 4 sections per post.")

class PostSectionInline(admin.StackedInline):
    model = PostSection
    extra = 0
    max_num = 4
    formset = LimitedSectionInlineFormSet

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published', 'created_at')
    list_filter = ('published', 'created_at')
    search_fields = ('title',)
    inlines = [PostSectionInline]
