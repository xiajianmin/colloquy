'''
Created on Mar 12, 2013

@author: JianMin
'''
from django import forms

class LearnForm(forms.Form):    

    language_name = forms.ChoiceField(choices=())
    
    TUTOR_ABILITY = [('1', 'Poor'),
                    ('2', 'Fair'),
                    ('3', 'Good'),
                    ('4', 'Very Good'),
                    ('5', 'Excellent')]
    
    reading = forms.ChoiceField(choices=TUTOR_ABILITY, initial='3')
    speaking = forms.ChoiceField(choices=TUTOR_ABILITY, initial='3')
    writing = forms.ChoiceField(choices=TUTOR_ABILITY, initial='3')   

    
    
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', None) 
        super(LearnForm, self).__init__(*args, **kwargs)
        
        if choices is not None:            
            self.fields['language_name'].choices = choices  
            
            
class TeacherDetailsForm(forms.Form):
    
    
    teacher_details = forms.ChoiceField(widget = forms.RadioSelect(), choices=[], required = True)
    
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', None) 
        super(TeacherDetailsForm, self).__init__(*args, **kwargs)
        
        if choices is not None:            
            self.fields['teacher_details'].choices = choices  
            
            
class TeacherEvaluationForm(forms.Form):
    
    
    #teacher_details = forms.ChoiceField(widget = forms.RadioSelect(), choices=[], required = True)
    
    def __init__(self, *args, **kwargs):
        attr_list = kwargs.pop('attr_list', None) 
        super(TeacherEvaluationForm, self).__init__(*args, **kwargs)
        
        RATINGS = [("neg_50","-5"), ("neg_40","-4") ,("neg_30","-3") ,("neg_20","-2") ,("neg_10","-1") ,("zero_0","0"),
                   ("pos_50","5"), ("pos_40","4") ,("pos_30","3") ,("pos_20","2") ,("pos_10","1") ]
        
                
        if attr_list  is not None and isinstance(attr_list, list):
            
            for i in attr_list:                
  
                #RATINGS_TEMP = [(str(i[0]) + "_" + x[0],x[1]) if x[1]!="0" else ("zero_0","0") for x in RATINGS]
                    
                self.fields[str(i[2])+ "_" +str(i[0])] = forms.ChoiceField(choices=RATINGS, required = True, initial='zero_0',label=str(i[1]))
                
                
                
                
                
                
            
            
            
                