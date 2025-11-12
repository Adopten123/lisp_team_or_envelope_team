from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Sum, Avg, Count
from ..models import Applicant, ApplicantExam

def applicant_chat(request):
    return HttpResponse("Страница чата абитуриентов")

def applicant_rating(request):
    """Рейтинг абитуриентов на основе существующих моделей"""

    # Получаем абитуриентов с подсчитанным общим баллом
    applicants_with_scores = Applicant.objects.select_related('person').prefetch_related('exams').annotate(
        total_score=Sum('exams__score'),
        exams_count=Count('exams')
    ).filter(exams_count__gt=0).order_by('-total_score')

    # Добавляем позиции в рейтинге
    ranked_applicants = []
    for position, applicant in enumerate(applicants_with_scores, 1):
        ranked_applicants.append({
            'position': position,
            'applicant': applicant,
            'total_score': applicant.total_score or 0,
            'exams': applicant.exams.all()  # prefetched экзамены
        })

    # Общая статистика
    total_applicants = applicants_with_scores.count()

    # Статистика по экзаменам
    exam_stats = ApplicantExam.objects.aggregate(
        avg_score=Avg('score'),
        total_exams=Count('id'),
        max_score=Sum('score')
    )

    # Статистика по типам экзаменов
    exam_types = ApplicantExam.objects.values('exam_type').annotate(
        count=Count('id'),
        avg_score=Avg('score')
    )

    context = {
        'ranked_applicants': ranked_applicants,
        'total_applicants': total_applicants,
        'exam_stats': exam_stats,
        'exam_types': exam_types,
    }

    return render(request, 'main/applicant_rating/applicant_rating.html', context)