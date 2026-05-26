from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role_display', 'phone', 'company_name','followers_count' ,'following_count','created_at')
    list_filter = ('user__role',)
    search_fields = ('user_email', 'user_first_name', 'company_name')
    readonly_fields = ('created_at', 'updated_at')

    def role_display(self, obj):
        return obj.user.role
    role_display.short_description = 'Role'

    def followers_count(self, obj):
        return obj.user.followers_set.count()
    followers_count.short_description = 'Followers'

    def following_count(self, obj):
        return obj.user.following_set.count()
    following_count.short_description = 'Following'
