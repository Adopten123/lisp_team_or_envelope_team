from django.shortcuts import render, redirect
from django.contrib import messages
from main.forms.admission_request import AdmissionRequestForm


def admission_request_page(request):
    """Страница подачи заявления на поступление"""
    if request.method == 'POST':
        form = AdmissionRequestForm(request.POST)
        if form.is_valid():
            try:
                admission_request = form.save()
                messages.success(
                    request,
                    '✅ Ваше заявление отправлено! Мы свяжемся с вами в ближайшее время.'
                )
                return redirect('admission_request_page')
            except Exception as e:
                messages.error(
                    request,
                    f'❌ Произошла ошибка при отправке: {str(e)}'
                )
    else:
        form = AdmissionRequestForm()

    return render(request, 'main/admission_request/admission_request_page.html', {
        'form': form
    })