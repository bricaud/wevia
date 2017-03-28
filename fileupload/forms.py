from django import forms
 
from fileupload.models import Document
 
 
class UploadFileForm(forms.ModelForm):
     
    class Meta:
        model = Document
        fields = ['file','description',]
