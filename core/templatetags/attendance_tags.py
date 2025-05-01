from django import template
from django.db.models import QuerySet
from datetime import datetime

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Safely get an item from a dictionary"""
    if not isinstance(dictionary, dict):
        return {}
    return dictionary.get(str(key), {})

@register.filter
def bonus_sum(records):
    try:
        return sum(record.bonus for record in records if hasattr(record, 'bonus'))
    except (TypeError, AttributeError):
        return 0

@register.filter
def exam_score(records):
    try:
        return sum(record.exam_score for record in records if hasattr(record, 'exam_score'))
    except (TypeError, AttributeError):
        return 0

@register.filter
def total_sum(records):
    try:
        total = sum(record.score for record in records if hasattr(record, 'score'))
        total += sum(record.bonus for record in records if hasattr(record, 'bonus'))
        total += sum(record.exam_score for record in records if hasattr(record, 'exam_score'))
        return total
    except (TypeError, AttributeError):
        return 0

@register.filter
def get_attendance(records, student_id):
    """Get attendance records for a student"""
    return records.get(str(student_id), {})

@register.filter
def get_record_for_date(student_records, date):
    """Get record for a specific date"""
    if isinstance(date, datetime):
        date = date.strftime('%Y-%m-%d')
    return student_records.get(str(date))