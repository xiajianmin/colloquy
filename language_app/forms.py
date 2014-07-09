from django import forms

class AddLanguageForm(forms.Form):
    
    country = forms.ChoiceField(widget = forms.Select(), choices=[])
    
    LEVELS = [(i,i) for i in range(0,11)]
    speaking = forms.ChoiceField(widget = forms.Select(), choices=LEVELS)
    reading = forms.ChoiceField(widget = forms.Select(), choices=LEVELS)
    writing = forms.ChoiceField(widget = forms.Select(), choices=LEVELS)
    
    native = forms.BooleanField(label="Native Language", required = False)
    
    ROLES = [("teacher", "Teacher"), ("student","Student"), ("both", "Both")]
    role = forms.ChoiceField(widget = forms.RadioSelect(), choices=ROLES, required = True)
    
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', None) 
        super(AddLanguageForm, self).__init__(*args, **kwargs)
        
        if choices is not None:            
            self.fields['country'].choices = choices        
    

class ModifyLanguageForm(forms.Form):
    
    
    languages = forms.ChoiceField(widget = forms.RadioSelect(), choices=[], required = True)
    
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', None) 
        super(ModifyLanguageForm, self).__init__(*args, **kwargs)
        
        if choices is not None:            
            self.fields['languages'].choices = choices  