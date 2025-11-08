from django import forms
from .models import Justificacion, Documento
from django.core.exceptions import ValidationError
import os


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

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if not archivo:
            return archivo

        # Validate extension
        name = archivo.name
        ext = os.path.splitext(name)[1].lower()
        allowed = ['.pdf', '.png']
        if ext not in allowed:
            raise ValidationError('Formato no permitido. Solo se aceptan: .pdf, .png')

        # Optional: additional content-type check
        content_type = getattr(archivo, 'content_type', None)
        if content_type:
            if not (content_type == 'application/pdf' or content_type.startswith('image/')):
                raise ValidationError('El archivo debe ser un PDF o una imagen PNG.')

        return archivo
