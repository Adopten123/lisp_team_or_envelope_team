from django.http import HttpResponse

def applicant_admission_request(request):
    return HttpResponse("Страница подачи заявления на поступление")

def applicant_chat(request):
    return HttpResponse("Страница чата абитуриентов")

def applicant_rating(request):
    return HttpResponse("Страница рейтинга абитуриентов")