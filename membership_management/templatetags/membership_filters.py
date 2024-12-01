from django import template

register = template.Library()

@register.filter
def filter_renewed(reminders):
    """Filter reminders to show only renewed ones"""
    return [r for r in reminders if r.response == 'RENEWED']

@register.filter
def filter_expired(reminders):
    """Filter reminders to show only expired memberships"""
    return [r for r in reminders if not r.membership.is_active]

@register.filter
def filter_pending(reminders):
    """Filter reminders to show only pending ones"""
    return [r for r in reminders if r.response == 'PENDING']

@register.filter
def filter_by_type(activities, activity_type):
    """Filter activities by type"""
    return [a for a in activities if a.activity_type == activity_type]
  