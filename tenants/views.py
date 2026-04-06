from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Hospital


@login_required
def hospital_list(request):
    hospitals = Hospital.objects.all().order_by('name')
    context = {'hospitals': hospitals}
    return render(request, 'tenants/hospital_list.html', context)


@login_required
def hospital_detail(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    context = {'hospital': hospital}
    return render(request, 'tenants/hospital_detail.html', context)
