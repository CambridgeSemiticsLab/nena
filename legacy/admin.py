from django.contrib import admin
from django.apps import apps

myapp = 'legacy'

class MultiDBModelAdmin(admin.ModelAdmin):
    # A handy constant for the name of the alternate database.
    using = 'legacy'

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super().formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super().formfield_for_manytomany(db_field, request, using=self.using, **kwargs)

admin.site.site_header = 'NENA'
admin.site.site_title = 'NENA models'
admin.site.index_title = 'System administration'

legacyadmin = admin.AdminSite(myapp)
legacyadmin.site_header = 'Legacy NENA'
legacyadmin.site_title = 'Legacy models'
legacyadmin.index_title = 'Legacy NENA administration'
for model in apps.get_app_config(myapp).get_models():
    legacyadmin.register(model, MultiDBModelAdmin)
