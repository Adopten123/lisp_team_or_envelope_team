from django.shortcuts import render, redirect
from django.contrib import messages
from main.forms.admission_request import AdmissionRequestForm

REQUEST_SUCCESSFUL = '✅ Ваше заявление успешно отправлено! Мы свяжемся с вами в ближайшее время.'
REQUEST_ERROR = '❌ Произошла ошибка при отправке заявления'

def admission_request_page(request):
    """
    Страница подачи заявления на поступление
    """
    if request.method == 'POST':
        form = AdmissionRequestForm(request.POST)
        if form.is_valid():
            try:
                admission_request = form.save()
                messages.success(request,REQUEST_SUCCESSFUL)
                return redirect('admission_request_page')
            except Exception as e:
                messages.error(request, f'{REQUEST_ERROR} {str(e)}')
        else:
            messages.error(request, REQUEST_ERROR)
    else:
        form = AdmissionRequestForm()

    context = {
        'form': form
    }

    return render(request, 'main/requests/admission_request_page.html', context)