from main.utils.placeholder import render_under_development


def applicant_chat_working_off_view(request):
    return render_under_development(
        request,
        title="💬 Чат с абитуриентами",
        message="Раздел чата с абитуриентами находится в разработке.",
        additional_info="В этом разделе вы сможете общаться с абитуриентами в реальном времени."
    )