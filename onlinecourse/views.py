from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Course, Lesson, Enrollment, Question, Choice, Submission

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    
    submission = Submission.objects.create(enrollment=enrollment)
    selected_choice_ids = []
    for key in request.POST:
        if key.startswith('choice_'):
            selected_choice_ids.append(int(request.POST[key]))
    
    for choice_id in selected_choice_ids:
        choice = Choice.objects.get(id=choice_id)
        submission.choices.add(choice)
        
    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    total_score = 0
    selected_ids = [choice.id for choice in submission.choices.all()]
    
    for question in course.question_set.all():
        if question.is_get_score(selected_ids):
            total_score += question.grade
            
    grade_percent = int((total_score / course.question_set.count()) * 100) if course.question_set.count() > 0 else 100
    
    context = {
        'course': course,
        'grade': grade_percent,
        'submission': submission
    }
    return render(request, 'onlinecourse/exam_result.html', context)
