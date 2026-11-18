from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import CrudeOil, Product, ProcessUnit, ProductionBatch, Refinery


class StyledFormMixin:
    """Добавляет CSS-класс ко всем полям формы."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class RegisterForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(label='Электронная почта', required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Имя пользователя',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }


class RefineryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Refinery
        fields = ('name', 'location', 'capacity', 'founded', 'description')
        labels = {
            'name': 'Название НПЗ',
            'location': 'Местоположение',
            'capacity': 'Мощность, млн тонн/год',
            'founded': 'Год пуска',
            'description': 'Описание',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class CrudeOilForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CrudeOil
        fields = ('name', 'density', 'sulfur', 'api_gravity', 'description')
        labels = {
            'name': 'Марка нефти',
            'density': 'Плотность, кг/м³',
            'sulfur': 'Содержание серы, %',
            'api_gravity': 'API-плотность',
            'description': 'Описание',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ProcessUnitForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ProcessUnit
        fields = ('refinery', 'name', 'process_type', 'capacity', 'commissioned')
        labels = {
            'refinery': 'НПЗ',
            'name': 'Название установки',
            'process_type': 'Тип процесса',
            'capacity': 'Мощность, тыс. тонн/год',
            'commissioned': 'Год ввода',
        }


class ProductForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'category', 'density', 'description')
        labels = {
            'name': 'Название продукта',
            'category': 'Категория',
            'density': 'Плотность, кг/м³',
            'description': 'Описание',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ProductionBatchForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ProductionBatch
        fields = (
            'refinery', 'crude_oil', 'unit', 'product',
            'input_volume', 'output_volume', 'produced_at', 'notes',
        )
        labels = {
            'refinery': 'НПЗ',
            'crude_oil': 'Марка сырой нефти',
            'unit': 'Технологическая установка',
            'product': 'Получаемый продукт',
            'input_volume': 'Объём сырья, тонн',
            'output_volume': 'Объём продукта, тонн',
            'produced_at': 'Дата переработки',
            'notes': 'Примечание',
        }
        widgets = {
            'produced_at': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        input_volume = cleaned_data.get('input_volume')
        output_volume = cleaned_data.get('output_volume')
        if input_volume is not None and output_volume is not None:
            if output_volume > input_volume:
                self.add_error(
                    'output_volume',
                    'Объём продукта не может превышать объём сырья.',
                )
        return cleaned_data
