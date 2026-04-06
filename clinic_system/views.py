# Views for clinic_system app
# Landing page functionality has been removed - root URL now redirects to login

from django.http import HttpResponse, Http404


def serve_firestore_pdf(request, subfolder, filename):
    """Serve a PDF stored in Cloudflare R2 as a downloadable HTTP response."""
    from clinic_system.gdrive_utils import get_pdf_from_r2

    pdf_bytes = get_pdf_from_r2(subfolder, filename)
    if pdf_bytes is None:
        raise Http404('PDF not found.')

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
