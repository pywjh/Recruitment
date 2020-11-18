# -*- coding: utf-8 -*-
# ========================================
# Author: wjh
# Date：2020/11/17
# FILE: forms
# ========================================
from django.forms import ModelForm
from jobs.models import Resume


class ResumeForm(ModelForm):
    class Meta:
        model = Resume

        fields = [
            "username", "city", "phone",
            "email", "apply_position", "born_address", "gender",
            "bachelor_school", "master_school", "major", "degree", 'created_date', 'modified_date',
            "candidate_introduction", "work_experience", "project_experience"
        ]
