from django.shortcuts import render, redirect, reverse
from django.http import Http404
from django.views import View

from jobs.models import Job, Resume
from jobs.forms import ResumeForm


def joblist(request):
    jobs = Job.objects.order_by('job_type')
    for job in jobs:
        job.job_city = job.get_job_city_display()
        job.job_type = job.get_job_type_display()
    return render(request, 'joblist.html', locals())


def detail(request, job_id):
    try:
        job = Job.objects.get(pk=job_id)
        job.city_name = job.get_job_city_display()
    except Job.DoesNotExist:
        raise Http404("Job does not exist")
    return render(request, 'job.html', locals())


class ResumeView(View):

    def get(self, request, *args, **kwargs):
        if not request.user.is_active:
            return redirect('/accounts/login/')
        form = ResumeForm()
        for x in self.request.GET:
            form.initial[x] = self.request.GET[x]
        return render(request, 'resume_form.html', locals())

    def post(self, request):
        form = ResumeForm(request.POST)
        if form.is_valid():
            resume = Resume()
            for v, k in form.cleaned_data.items():
                setattr(resume, v, k)
            resume.applicant = request.user
            resume.save()
        return redirect(reverse('jobs:joblist'))


