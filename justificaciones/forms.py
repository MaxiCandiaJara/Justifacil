from django import forms
from .models import Justificacion, Documento


class JustificacionForm(forms.ModelForm):
    class Meta:
        model = Justificacion
        fields = ["fecha_inicio", "fecha_fin", "motivo", "descripcion"]
        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "motivo": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ["archivo"]
        widgets = {
            "archivo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
        help_texts = {
            "archivo": "Adjunta PDF o imagen como respaldo."
        }
