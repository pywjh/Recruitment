import csv
import logging

from django.contrib import admin
from .models import Candidate
from django.utils import timezone, dateformat
from django.http import HttpResponse

logger = logging.getLogger(__name__)

exportable_fields = (
    'username', 'city', 'phone', 'bachelor_school', 'master_school', 'degree', 'first_result', 'first_interviewer_user',
    'second_result', 'second_interviewer_user', 'hr_result', 'hr_score', 'hr_remark', 'hr_interviewer_user')


def get_group_names(user):
    """
    获取当前用户的所有的组
    """
    group_names = []
    for g in user.groups.all():
        group_names.append(g.name)
    return group_names


def export_model_as_csv(model_admin, request, queryset):
    """
    导出数据，并会添加到动作中
    """
    response = HttpResponse(content_type='text/csv')
    field_list = exportable_fields
    response['Content-Disposition'] = 'attachment; filename=%s-list-%s.csv' % (
        'recruitment-candidates',
        dateformat.DateFormat(timezone.now()).format('Ymd'),
    )
    # 写入表头
    writer = csv.writer(response)
    writer.writerow(
        [
            queryset.model._mseta.get_field(f).verbose_name.title()
            for f in field_list
        ],
    )
    for obj in queryset:
        # 单行 的记录（各个字段的值）， 根据字段对象，从当前实例 (obj) 中获取字段值
        csv_line_values = []
        for field in field_list:
            # 确认字段属于该模型
            field_object = queryset.model._meta.get_field(field)
            # 取值
            field_value = field_object.value_from_object(obj)
            csv_line_values.append(field_value)
        writer.writerow(csv_line_values)
    logger.error(" %s has exported %s candidate records" % (request.user.username, len(queryset)))

    return response


# 汉化动作菜单的名称
export_model_as_csv.short_description = '导出为CSV文件'


def get_list_editable(request):
    """
    通过用户来控制行内编辑的权限
    只有hr可以行内编辑面试官
    """
    group_names = get_group_names(request.user)

    if request.user.is_superuser or 'hr' in group_names:
        return 'first_interviewer_user', 'second_interviewer_user'
    return ()


class CandidateAdmin(admin.ModelAdmin):
    # 自定义动作
    actions = (export_model_as_csv,)
    # 不展示的字段
    exclude = ('creator', 'created_date', 'modified_date')
    # 要展示的字段
    list_display = (
        'username', 'city', 'bachelor_school', 'first_score', 'first_result', 'first_interviewer_user', 'second_score',
        'second_result', 'second_interviewer_user', 'hr_score', 'hr_result', 'hr_interviewer_user')
    # 右侧筛选条件
    list_filter = (
        'city', 'first_result', 'second_result', 'hr_result', 'first_interviewer_user', 'second_interviewer_user',
        'hr_interviewer_user')
    # 查询字段
    search_fields = ('username', 'phone', 'email', 'bachelor_school')
    # 默认排序
    ordering = ('hr_result', 'second_result', 'first_result',)

    fieldsets = (
        (None, {'fields': ("userid", ("username", "city", "phone"), ("email", "apply_position", "born_address"),
                           ("gender", "candidate_remark", "bachelor_school"),
                           ("master_school", "doctor_school", "major"), "degree",
                           ("test_score_of_general_ability", "paper_score"),)}),
        ('第一轮面试', {'fields': (
            "first_interviewer_user", "first_score", ("first_learning_ability", "first_professional_competency"),
            "first_advantage", "first_disadvantage", "first_result", "first_recommend_position", "first_remark",)}),
        ('第二轮面试', {'fields': ("second_interviewer_user", (
            "second_learning_ability", "second_professional_competency", "second_pursue_of_excellence"),
                              ("second_communication_ability", "second_pressure_score", "second_score"),
                              "second_advantage", "second_disadvantage", "second_result", "second_recommend_position",
                              "second_remark",)}),
        ('第三轮面试', {'fields': ("hr_interviewer_user", ("hr_score", "hr_responsibility", "hr_communication_ability"),
                              ("hr_logic_ability", "hr_potential", "hr_stability"), "hr_advantage", "hr_disadvantage",
                              "hr_result", "hr_remark", "last_editor",)}),
    )

    # 全局的，达不到效果
    # list_editable = ('first_interviewer_user', 'second_interviewer_user',)

    def get_changelist_instance(self, request):
        """
        此方法进入列表页就会被调用
        在此处触发更新列表编辑的逻辑
        """
        self.list_editable = get_list_editable(request)
        return super().get_changelist_instance(request)

    def get_readonly_fields(self, request, obj=None):
        """
        重写获取只读字段逻辑
        如果在interviewer组里面，则一面面试官和二面面试官字段只读
        """
        group_names = get_group_names(request.user)

        readonly_fields = ()

        if 'interviewer' in group_names:
            logger.info("interviewer is in user's group for %s" % request.user.username)
            readonly_fields = ('first_interviewer_user', 'second_interviewer_user',)
        return readonly_fields

    def save_model(self, request, obj, form, change):
        """
        重写保存逻辑，自动更新修改人，修改时间
        """
        obj.last_editor = request.user.username
        if not obj.creator:
            obj.creator = request.user.username
        obj.modified_date = timezone.localtime()
        return super().save_model(request, obj, form, change)


admin.site.register(Candidate, CandidateAdmin)
