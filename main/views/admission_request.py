from django.shortcuts import render, redirect
from django.contrib import messages
from main.forms.admission_request import AdmissionRequestForm

def admission_request_page(request):
    """Страница подачи заявления на поступление"""
    if request.method == 'POST':
        form = AdmissionRequestForm(request.POST)
        if form.is_valid():
            try:
                # Сохраняем форму - данные автоматически попадут в базу
                admission_request = form.save()
                messages.success(
                    request,
                    '✅ Ваше заявление успешно отправлено! Мы свяжемся с вами в ближайшее время.'
                )
                return redirect('admission_request_page')
            except Exception as e:
                messages.error(
                    request,
                    f'❌ Произошла ошибка при отправке заявления: {str(e)}'
                )
        else:
            # Если форма невалидна, покажем ошибки
            messages.error(
                request,
                '❌ Пожалуйста, исправьте ошибки в форме.'
            )
    else:
        form = AdmissionRequestForm()

    return render(request, 'main/requests/admission_request_page.html', {
        'form': form
    })