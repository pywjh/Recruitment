from django.contrib import admin
from .models import Candidate
# Register your models here.


class CandidateAdmin(admin.ModelAdmin):
    # 不展示的字段
    exclude = ('creator', 'created_date', 'modified_date')
    # 要展示的字段
    list_display = ('username', 'city', 'bachelor_school', 'first_score', 'first_result', 'first_interviewer_user', 'second_score', 'second_result', 'second_interviewer_user', 'hr_score', 'hr_result', 'hr_interviewer_user')
    # 右侧筛选条件
    list_filter = ('city', 'first_result', 'second_result', 'hr_result', 'first_interviewer_user', 'second_interviewer_user', 'hr_interviewer_user')
    # 查询字段
    search_fields = ('username', 'phone', 'email', 'bachelor_school')
    # 列表页排序字段
    ordering = ('hr_result', 'second_result', 'first_result',)


admin.site.register(Candidate, CandidateAdmin)