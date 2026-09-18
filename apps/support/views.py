from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.support.models import SupportTicket, TicketMessage
from apps.core.storage import storage_service
from apps.core.centrifugo import centrifugo_service

@login_required
def ticket_list_view(request):
    tickets = request.user.tickets.all().order_by('-created_at')

    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        first_message = request.POST.get('message', '').strip()

        if subject and first_message:
            ticket = SupportTicket.objects.create(user=request.user, subject=subject, status='open')
            TicketMessage.objects.create(ticket=ticket, sender=request.user, message=first_message)
            messages.success(request, 'تم إنشاء تذكرة الدعم بنجاح! / Support ticket created!')
            return redirect('ticket_detail', ticket_id=ticket.id)
        else:
            messages.error(request, 'يرجى إدخال عنوان ورسالة التذكرة / Please provide a subject and message.')

    return render(request, 'support/ticket_list.html', {'tickets': tickets})

@login_required
def ticket_detail_view(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)

    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        attachment = request.FILES.get('attachment')
        attachment_url = ""

        if attachment:
            object_name = f"tickets/{ticket.id}/{attachment.name}"
            storage_service.upload_file_bytes(attachment.read(), object_name, attachment.content_type)
            attachment_url = storage_service.get_presigned_url(object_name)

        if message_text or attachment_url:
            TicketMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                message=message_text,
                attachment_url=attachment_url
            )
            ticket.status = 'open'
            ticket.save(update_fields=['status'])
            return redirect('ticket_detail', ticket_id=ticket.id)

    return render(request, 'support/ticket_detail.html', {'ticket': ticket})
