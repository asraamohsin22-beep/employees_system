from django.contrib import admin
from django import forms
from django.shortcuts import render, redirect
from .models import Employee
import pandas as pd


class UploadFileForm(forms.Form):
    file = forms.FileField(label="رفع ملف Excel")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('upload-excel/', self.upload_excel, name='upload-excel')
        ]
        return custom_urls + urls

    def upload_excel(self, request):

        if request.method == "POST":
            form = UploadFileForm(request.POST, request.FILES)

            if form.is_valid():
                file = request.FILES["file"]
                df = pd.read_excel(file)

                # تنظيف الأعمدة
                df.columns = df.columns.str.strip().str.lower()
                for _, row in df.iterrows():

                    emp_id_value = row.get('emp_id') or row.get('id')

                    if not emp_id_value:
                        continue

                    Employee.objects.update_or_create(
                        emp_id=emp_id_value,
                        defaults={
                            'name': row.get('name'),
                            'base_salary': row.get('base_salary') or row.get('salary') or 0,
                        }
                   )
                self.message_user(request, "تم رفع الملف بنجاح")
                return redirect("../")

        else:
            form = UploadFileForm()

        return render(request, "admin/upload_excel.html", {"form": form})