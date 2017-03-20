from django import forms
 
from fileupload.models import UploadFile
 
 
class UploadFileForm(forms.ModelForm):
     
    class Meta:
        model = UploadFile
        fields = ['file','description',]
