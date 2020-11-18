from django.contrib import admin
from django.utils import timezone
from django.contrib import messages

from jobs.models import Job, Resume
from interview.models import Candidate


def enter_interview_process(model_admin, request, queryset):
    """
    将简历添加到招聘内容中，激活面试流程
    """
    candidate_names = []
    for resume in queryset:
        candidate = Candidate()
        # 把 obj 对象中的所有属性拷贝到 candidate 对象中:
        candidate.__dict__.update(resume.__dict__)
        candidate.created_date = timezone.now()
        candidate.modified_date = timezone.now()
        candidate_names.append(candidate.username)
        candidate.creator = request.user.username
        candidate.save()
    messages.add_message(
        request=request,
        level=messages.INFO,
        message='候选人: %s 已成功进入面试流程' % ('、'.join(candidate_names)),
    )


enter_interview_process.short_description = '进入面试流程'


class JobAdmin(admin.ModelAdmin):
    exclude = ('creator', 'created_date', 'modified_date')
    list_display = ('job_name', 'job_type', 'job_city', 'creator', 'created_date', 'modified_date')

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        super().save_model(request, obj, form, change)


class ResumeAdmin(admin.ModelAdmin):
    actions = (enter_interview_process, )

    list_display = (
        'username', 'applicant', 'city', 'apply_position', 'bachelor_school', 'master_school', 'major', 'created_date')

    readonly_fields = ('applicant', 'created_date', 'modified_date',)

    fieldsets = (
        (None, {'fields': (
            ("applicant", "phone"), ("username", "city"),
            ("email", "apply_position"), ("born_address", "gender",),
            ("bachelor_school", "master_school"), ("major", "degree"), ('created_date', 'modified_date'),
            "candidate_introduction", "work_experience", "project_experience",)}),
    )

    def save_model(self, request, obj, form, change):
        obj.applicant = request.user
        super().save_model(request, obj, form, change)


# Register your models here.
admin.site.register(Job, JobAdmin)
admin.site.register(Resume, ResumeAdmin)
