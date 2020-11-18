import csv
import logging

from django.contrib import admin
from django.utils import timezone, dateformat
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
from django.utils.safestring import mark_safe

from interview.models import Candidate
from interview import candidate_field as cf
from interview.dingtalk import send
from jobs.models import Resume

logger = logging.getLogger(__name__)

exportable_fields = (
    'username', 'city', 'phone', 'bachelor_school', 'master_school', 'degree', 'first_result', 'first_interviewer_user',
    'second_result', 'second_interviewer_user', 'hr_result', 'hr_score', 'hr_remark', 'hr_interviewer_user')


def get_group_names(user):
    """
    获取当前用户的所有的组
    """
    group_names = []
    group_names.extend(user.groups.values_list('name', flat=True))
    return group_names


# 通知一面面试官面试
def notify_interviewer(model_admin, request, queryset):
    """
    动作菜单，通知对应面试官
    """
    candidates = '、'.join([getattr(rec, 'username', '') for rec in queryset])
    interviewers = '、'.join(
        list(
            set(
                [
                    getattr(rec, 'first_interviewer_user', None) and
                    getattr(rec, 'first_interviewer_user').username or ''
                    for rec in queryset
                ]
            )
        )
    )
    send("候选人 %s 进入面试环节，亲爱的面试官，请准备好面试： %s" % (candidates, interviewers))
    messages.add_message(request, messages.INFO, '已经成功发送面试通知')


notify_interviewer.short_description = '通知一面面试官'
notify_interviewer.allowed_permissions = ('notify', )


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


# 重命名动作菜单的名称
export_model_as_csv.short_description = '导出为CSV文件'
export_model_as_csv.allowed_permissions = ('export', )


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
    actions = (export_model_as_csv, notify_interviewer, )
    # 不展示的字段
    exclude = ('creator', 'created_date', 'modified_date')
    # 要展示的字段
    list_display = (
        'username', 'city', 'bachelor_school', 'get_resume', 'first_score', 'first_result', 'first_interviewer_user', 'second_score',
        'second_result', 'second_interviewer_user', 'hr_score', 'hr_result', 'hr_interviewer_user')
    # 右侧筛选条件
    list_filter = (
        'city', 'first_result', 'second_result', 'hr_result', 'first_interviewer_user', 'second_interviewer_user',
        'hr_interviewer_user')
    # 查询字段
    search_fields = ('username', 'phone', 'email', 'bachelor_school')
    # 默认排序
    ordering = ('hr_result', 'second_result', 'first_result',)

    # 当前用户是否有导出权限
    def has_export_permission(self, request):
        return request.user.has_perm(f'{self.opts.app_label}.{"export"}')

    # 当前用户是否有导出权限
    def has_notify_permission(self, request):
        return request.user.has_perm(f'{self.opts.app_label}.{"notify"}')

    def get_resume(self, obj):
        if not obj.phone:
            return ""
        resumes = Resume.objects.filter(phone=obj.phone).order_by('-modified_date')
        if resumes and len(resumes) > 0:
            return mark_safe(u'<a href="/resume/%s" target="_blank">%s</a>' % (resumes[0].id, "查看简历"))
        return ""

    get_resume.short_description = '查看简历'
    get_resume.allow_tags = True

    def get_fieldsets(self, request, obj=None):
        """
        权限控制： fieldsets
        一面只能看到基础+一面信息
        二面可以看到基础+一面+二面的信息
        hr可以看到基础+一面+二面+hr的信息
        """
        group_names = get_group_names(request.user)

        if 'interviewer' in group_names and obj.first_interviewer_user == request.user:
            return cf.default_fieldsets_first
        elif 'interviewer' in group_names and obj.second_interviewer_user == request.user:
            return cf.default_fieldsets_second
        else:
            return cf.default_fieldsets

    def get_queryset(self, request):
        """
        数据集权限
        出了admin和hr组，其他的人，一面和二面是当前用户的才能看到
        """
        user = request.user
        queryset = super().get_queryset(request)
        group_names = get_group_names(user)

        if user.is_superuser or 'hr' in group_names:
            return queryset
        return queryset.filter(Q(first_interviewer_user=user) | Q(second_interviewer_user=user))

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
