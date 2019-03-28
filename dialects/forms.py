from django import forms

from dialects.models import DialectFeature

class DialectFeatureForm(forms.ModelForm):
    category = forms.ChoiceField(required=False)

    class Meta:
        model  = DialectFeature
        fields = ('is_absent', 'category', 'introduction', 'comment')

    def __init__(self, *args, **kwargs):
        category_list = kwargs.get('instance').feature.category_list
        if category_list:
            choices = ((x, x) for x in category_list.split('|'))
        else:
            choices = (('', 'No category'),)
        self.base_fields['category'].choices = choices
        super(DialectFeatureForm, self).__init__(*args, **kwargs)
