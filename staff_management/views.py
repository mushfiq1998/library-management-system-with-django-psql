from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Department, StaffMember, Leave, Attendance
from .forms import DepartmentForm, StaffMemberForm, LeaveForm, LeaveActionForm, AttendanceForm

def is_admin_or_librarian(user):
    return user.role in ['ADMIN', 'LIBRARIAN']

@login_required
@user_passes_test(is_admin_or_librarian)
def staff_dashboard(request):
    total_staff = StaffMember.objects.count()
    departments = Department.objects.all()
    pending_leaves = Leave.objects.filter(status='PENDING').count()
    today_attendance = Attendance.objects.filter(date=timezone.now().date()).count()
    
    context = {
        'total_staff': total_staff,
        'departments': departments,
        'pending_leaves': pending_leaves,
        'today_attendance': today_attendance,
    }
    return render(request, 'staff_management/staff_dashboard.html', context)

# Department Views
@login_required
@user_passes_test(is_admin_or_librarian)
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'staff_management/department_list.html', {
        'departments': departments
    })

@login_required
@user_passes_test(is_admin_or_librarian)
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully.')
            return redirect('staff:department_list')
    else:
        form = DepartmentForm()
    
    return render(request, 'staff_management/department_form.html', {
        'form': form,
        'action': 'Create'
    })

@login_required
@user_passes_test(is_admin_or_librarian)
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully.')
            return redirect('staff:department_list')
    else:
        form = DepartmentForm(instance=department)
    
    return render(request, 'staff_management/department_form.html', {
        'form': form,
        'department': department,
        'action': 'Edit'
    })

@login_required
@user_passes_test(is_admin_or_librarian)
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Department deleted successfully.')
        return redirect('staff:department_list')
    return render(request, 'staff_management/department_confirm_delete.html', {
        'department': department
    })

# Staff Member Views
@login_required
@user_passes_test(is_admin_or_librarian)
def staff_member_list(request):
    query = request.GET.get('search', '')
    department = request.GET.get('department', '')
    
    staff_members = StaffMember.objects.all()
    
    if query:
        staff_members = staff_members.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(employee_id__icontains=query)
        )
    
    if department:
        staff_members = staff_members.filter(department_id=department)
    
    context = {
        'staff_members': staff_members,
        'departments': Department.objects.all(),
        'search_query': query,
        'selected_department': department
    }
    return render(request, 'staff_management/staff_member_list.html', context)

@login_required
@user_passes_test(is_admin_or_librarian)
def staff_member_create(request):
    if request.method == 'POST':
        form = StaffMemberForm(request.POST)
        if form.is_valid():
            staff_member = form.save()
            messages.success(request, 'Staff member created successfully.')
            return redirect('staff:staff_member_detail', pk=staff_member.pk)
    else:
        form = StaffMemberForm()
    
    return render(request, 'staff_management/staff_member_form.html', {
        'form': form,
        'action': 'Create'
    })

@login_required
@user_passes_test(is_admin_or_librarian)
def staff_member_detail(request, pk):
    staff_member = get_object_or_404(StaffMember, pk=pk)
    leaves = staff_member.leaves.all().order_by('-created_at')[:5]
    attendance = staff_member.attendance.all().order_by('-date')[:5]
    
    context = {
        'staff_member': staff_member,
        'recent_leaves': leaves,
        'recent_attendance': attendance
    }
    return render(request, 'staff_management/staff_member_detail.html', context)

@login_required
@user_passes_test(is_admin_or_librarian)
def staff_member_edit(request, pk):
    staff_member = get_object_or_404(StaffMember, pk=pk)
    if request.method == 'POST':
        form = StaffMemberForm(request.POST, instance=staff_member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff member updated successfully.')
            return redirect('staff:staff_member_detail', pk=pk)
    else:
        form = StaffMemberForm(instance=staff_member)
    
    return render(request, 'staff_management/staff_member_form.html', {
        'form': form,
        'staff_member': staff_member,
        'action': 'Edit'
    })

@login_required
@user_passes_test(is_admin_or_librarian)
def staff_member_delete(request, pk):
    staff_member = get_object_or_404(StaffMember, pk=pk)
    if request.method == 'POST':
        staff_member.user.delete()  # This will cascade delete the staff member
        messages.success(request, 'Staff member deleted successfully.')
        return redirect('staff:staff_member_list')
    return render(request, 'staff_management/staff_member_confirm_delete.html', {
        'staff_member': staff_member
    })

# Leave Management Views
@login_required
def leave_list(request):
    if request.user.role in ['ADMIN', 'LIBRARIAN']:
        leaves = Leave.objects.all().order_by('-created_at')
    else:
        leaves = Leave.objects.filter(staff_member__user=request.user).order_by('-created_at')
    
    return render(request, 'staff_management/leave_list.html', {'leaves': leaves})

@login_required
def leave_create(request):
    try:
        staff_member = request.user.staff_profile
    except StaffMember.DoesNotExist:
        messages.error(request, 'You must be a staff member to request leave.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.staff_member = staff_member
            leave.save()
            messages.success(request, 'Leave request submitted successfully.')
            return redirect('staff:leave_list')
    else:
        form = LeaveForm()
    
    return render(request, 'staff_management/leave_form.html', {
        'form': form,
        'action': 'Create'
    })

@login_required
def leave_detail(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    if not (request.user.role in ['ADMIN', 'LIBRARIAN'] or leave.staff_member.user == request.user):
        messages.error(request, 'You do not have permission to view this leave request.')
        return redirect('staff:leave_list')
    
    return render(request, 'staff_management/leave_detail.html', {'leave': leave})

@login_required
@user_passes_test(is_admin_or_librarian)
def leave_action(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    if request.method == 'POST':
        form = LeaveActionForm(request.POST, instance=leave)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.approved_by = request.user
            leave.approved_date = timezone.now()
            leave.save()
            messages.success(request, f'Leave request {leave.get_status_display().lower()}.')
            return redirect('staff:leave_detail', pk=pk)
    else:
        form = LeaveActionForm(instance=leave)
    
    return render(request, 'staff_management/leave_action.html', {
        'form': form,
        'leave': leave
    })

@login_required
def leave_edit(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    
    # Only allow editing if the leave request is pending and belongs to the user
    if leave.status != 'PENDING' or leave.staff_member.user != request.user:
        messages.error(request, 'You cannot edit this leave request.')
        return redirect('staff:leave_list')
    
    if request.method == 'POST':
        form = LeaveForm(request.POST, instance=leave)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave request updated successfully.')
            return redirect('staff:leave_detail', pk=pk)
    else:
        form = LeaveForm(instance=leave)
    
    return render(request, 'staff_management/leave_form.html', {
        'form': form,
        'leave': leave,
        'action': 'Edit'
    })

@login_required
def leave_delete(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    
    # Only allow deletion if the leave request is pending and belongs to the user
    if leave.status != 'PENDING' or leave.staff_member.user != request.user:
        messages.error(request, 'You cannot delete this leave request.')
        return redirect('staff:leave_list')
    
    if request.method == 'POST':
        leave.delete()
        messages.success(request, 'Leave request deleted successfully.')
        return redirect('staff:leave_list')
    
    return render(request, 'staff_management/leave_confirm_delete.html', {
        'leave': leave
    })

# Attendance Views
@login_required
@user_passes_test(is_admin_or_librarian)
def attendance_list(request):
    date = request.GET.get('date', timezone.now().date())
    attendance = Attendance.objects.filter(date=date)
    return render(request, 'staff_management/attendance_list.html', {
        'attendance': attendance,
        'selected_date': date,
        'today': timezone.now().date()
    })

@login_required
@user_passes_test(is_admin_or_librarian)
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance recorded successfully.')
            return redirect('staff:attendance_list')
    else:
        form = AttendanceForm()
    
    return render(request, 'staff_management/attendance_form.html', {
        'form': form,
        'action': 'Create'
    })

@login_required
@user_passes_test(is_admin_or_librarian)
def attendance_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    staff_member = request.GET.get('staff_member')
    
    attendance = Attendance.objects.all()
    if start_date:
        attendance = attendance.filter(date__gte=start_date)
    if end_date:
        attendance = attendance.filter(date__lte=end_date)
    if staff_member:
        attendance = attendance.filter(staff_member_id=staff_member)
    
    # Calculate statistics
    present_count = attendance.filter(status='PRESENT').count()
    late_count = attendance.filter(status='LATE').count()
    half_day_count = attendance.filter(status='HALF_DAY').count()
    absent_count = attendance.filter(status='ABSENT').count()
    
    context = {
        'attendance': attendance,
        'staff_members': StaffMember.objects.all(),
        'start_date': start_date,
        'end_date': end_date,
        'selected_staff': staff_member,
        'today': timezone.now().date(),
        'present_count': present_count,
        'late_count': late_count,
        'half_day_count': half_day_count,
        'absent_count': absent_count
    }
    return render(request, 'staff_management/attendance_report.html', context)

@login_required
@user_passes_test(is_admin_or_librarian)
def attendance_edit(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance record updated successfully.')
            return redirect('staff:attendance_list')
    else:
        form = AttendanceForm(instance=attendance)
    
    return render(request, 'staff_management/attendance_form.html', {
        'form': form,
        'attendance': attendance,
        'action': 'Edit'
    })

@login_required
@user_passes_test(is_admin_or_librarian)
def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, 'Attendance record deleted successfully.')
        return redirect('staff:attendance_list')
    
    return render(request, 'staff_management/attendance_confirm_delete.html', {
        'attendance': attendance
    }) 