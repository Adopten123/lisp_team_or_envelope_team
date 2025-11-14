from django.shortcuts import render, redirect
from django.contrib import messages
from main.forms.help_request import HelpRequestForm

REQUEST_ACCEPTED = '✅ Ваш запрос отправлен! Мы ответим вам в ближайшее время.'
REQUEST_ERROR = '❌ Произошла ошибка при отправке'

def help_page(request):
    """
    Страница помощи с формой обратной связи
    """
    if request.method == 'POST':
        form = HelpRequestForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, REQUEST_ACCEPTED)
                return redirect('help_page')
            except Exception as e:
                messages.error(request, f'{REQUEST_ERROR}: {str(e)}')
    else:
        form = HelpRequestForm()

    context = {
        'form': form
    }
    return render(request, 'main/help/help_page.html', context)