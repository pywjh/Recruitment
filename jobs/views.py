from django.shortcuts import render
from django.http import Http404
from django.views import View
from .models import Job, JobTypes, Cities


def joblist(request):
    jobs = Job.objects.order_by('job_type')
    for job in jobs:
        job.job_city = Cities[job.job_city][1]
        job.job_type = JobTypes[job.job_type][1]
    return render(request, 'joblist.html', locals())


def detail(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
        job.city_name = Cities[job.job_city][1]
    except Job.DoesNotExist:
        raise Http404("Job does not exist")
    return render(request, 'job.html', locals())
