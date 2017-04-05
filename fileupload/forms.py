from django import forms
 
from fileupload.models import Document
from classif.models import Cluster
from django.utils import timezone

 
class UploadFileForm(forms.ModelForm):

	class Meta:
		model = Document
		fields = ['file','description',]

class DocModifForm(forms.ModelForm):
	#cluster=forms.ModelMultipleChoiceField(queryset=Cluster.objects.all(), widget=forms.CheckboxSelectMultiple())
	class Meta:
		model = Document
		fields = ['name','text_date', 'description', 'cluster', 'text',]
	name = forms.CharField(widget=forms.TextInput(attrs={'size': '50','readonly':'readonly'}))#disabled=True
	text_date = forms.DateField(widget=forms.SelectDateWidget(
		years=list(range(1970,timezone.now().year+1))),required=False)