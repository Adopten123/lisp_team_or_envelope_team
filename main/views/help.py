from django.shortcuts import render, redirect
from django.contrib import messages
from main.forms.help_request import HelpRequestForm


def help_page(request):
    """Страница помощи с формой обратной связи"""
    if request.method == 'POST':
        form = HelpRequestForm(request.POST)
        if form.is_valid():
            try:
                help_request = form.save()
                messages.success(
                    request,
                    '✅ Ваш запрос отправлен! Мы ответим вам в ближайшее время.'
                )
                return redirect('help_page')
            except Exception as e:
                messages.error(
                    request,
                    f'❌ Произошла ошибка при отправке: {str(e)}'
                )
    else:
        form = HelpRequestForm()

    return render(request, 'main/help/help_page.html', {
        'form': form
    })