from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from .forms import (
    CrudeOilForm,
    ProductForm,
    ProcessUnitForm,
    ProductionBatchForm,
    RefineryForm,
    RegisterForm,
)
from .models import CrudeOil, Product, ProcessUnit, ProductionBatch, Refinery


def register(request):
    """Регистрация нового пользователя."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация выполнена. Добро пожаловать!')
            return redirect('refining:home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def home(request):
    """Главная страница — простая сводка, как в учебном проекте."""
    batches = ProductionBatch.objects.select_related('refinery', 'crude_oil', 'unit', 'product')
    total_input = batches.aggregate(total=Sum('input_volume'))['total'] or 0
    context = {
        'refineries_count': Refinery.objects.count(),
        'total_input': total_input,
        'recent_batches': batches[:5],
        'by_refinery': (
            batches.values('refinery__name')
            .annotate(total=Sum('input_volume'))
            .order_by('-total')
        ),
    }
    return render(request, 'refining/home.html', context)


# --- Списки и детали ---

class RefineryListView(ListView):
    model = Refinery
    template_name = 'refining/refinery_list.html'
    context_object_name = 'refineries'


class RefineryDetailView(DetailView):
    model = Refinery
    template_name = 'refining/refinery_detail.html'
    context_object_name = 'refinery'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['units'] = self.object.units.all()
        ctx['batches'] = self.object.batches.select_related(
            'crude_oil', 'unit', 'product'
        )[:10]
        return ctx


class CrudeOilListView(ListView):
    model = CrudeOil
    template_name = 'refining/crudeoil_list.html'
    context_object_name = 'crudes'


class CrudeOilDetailView(DetailView):
    model = CrudeOil
    template_name = 'refining/crudeoil_detail.html'
    context_object_name = 'crude'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['batches'] = self.object.batches.select_related(
            'refinery', 'product'
        )[:10]
        return ctx


class ProductListView(ListView):
    model = Product
    template_name = 'refining/product_list.html'
    context_object_name = 'products'


class ProductDetailView(DetailView):
    model = Product
    template_name = 'refining/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['batches'] = self.object.batches.select_related(
            'refinery', 'crude_oil'
        )[:10]
        return ctx


class UnitListView(ListView):
    model = ProcessUnit
    template_name = 'refining/unit_list.html'
    context_object_name = 'units'
    queryset = ProcessUnit.objects.select_related('refinery')


class BatchListView(ListView):
    model = ProductionBatch
    template_name = 'refining/batch_list.html'
    context_object_name = 'batches'
    paginate_by = 15
    queryset = ProductionBatch.objects.select_related(
        'refinery', 'crude_oil', 'unit', 'product'
    )


class BatchDetailView(DetailView):
    model = ProductionBatch
    template_name = 'refining/batch_detail.html'
    context_object_name = 'batch'

    def get_queryset(self):
        return ProductionBatch.objects.select_related(
            'refinery', 'crude_oil', 'unit', 'product', 'created_by'
        )


# --- Формы создания / редактирования (только для авторизованных) ---

FORM_CONFIG = {
    'refinery': (Refinery, RefineryForm, 'refining:refinery_list', 'НПЗ'),
    'crudeoil': (CrudeOil, CrudeOilForm, 'refining:crudeoil_list', 'марку нефти'),
    'unit': (ProcessUnit, ProcessUnitForm, 'refining:unit_list', 'установку'),
    'product': (Product, ProductForm, 'refining:product_list', 'продукт'),
    'batch': (ProductionBatch, ProductionBatchForm, 'refining:batch_list', 'партию переработки'),
}


def _handle_form(request, key, pk=None):
    model, form_class, redirect_url, label = FORM_CONFIG[key]
    obj = get_object_or_404(model, pk=pk) if pk else None

    if request.method == 'POST':
        form = form_class(request.POST, instance=obj)
        if form.is_valid():
            saved = form.save(commit=False)
            if key == 'batch' and saved.created_by_id is None:
                saved.created_by = request.user
            saved.save()
            action = 'обновлена' if obj else 'добавлена'
            messages.success(request, f'{label.capitalize()} успешно {action}.')
            return redirect(redirect_url)
    else:
        form = form_class(instance=obj)

    template = f'refining/{key}_form.html'
    return render(request, template, {
        'form': form,
        'object': obj,
        'title': f'{"Редактировать" if obj else "Добавить"} {label}',
    })


@login_required
def refinery_create(request):
    return _handle_form(request, 'refinery')


@login_required
def refinery_update(request, pk):
    return _handle_form(request, 'refinery', pk)


@login_required
def crudeoil_create(request):
    return _handle_form(request, 'crudeoil')


@login_required
def crudeoil_update(request, pk):
    return _handle_form(request, 'crudeoil', pk)


@login_required
def unit_create(request):
    return _handle_form(request, 'unit')


@login_required
def unit_update(request, pk):
    return _handle_form(request, 'unit', pk)


@login_required
def product_create(request):
    return _handle_form(request, 'product')


@login_required
def product_update(request, pk):
    return _handle_form(request, 'product', pk)


@login_required
def batch_create(request):
    return _handle_form(request, 'batch')


@login_required
def batch_update(request, pk):
    return _handle_form(request, 'batch', pk)


@login_required
def batch_delete(request, pk):
    batch = get_object_or_404(ProductionBatch, pk=pk)
    if request.method == 'POST':
        batch.delete()
        messages.success(request, 'Партия переработки удалена.')
        return redirect('refining:batch_list')
    return render(request, 'refining/batch_confirm_delete.html', {'batch': batch})

