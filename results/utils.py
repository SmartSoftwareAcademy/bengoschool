from .models import *


def calculate_positions(class_obj, term_obj,criteria):
    # Step 1: Retrieve results for the specified class and term
    Class=StudentClass.objects.get(id=class_obj)
    results = Result.objects.filter(current_class=class_obj, term=term_obj)
    # Step 2: Calculate total scores/points earned for each student based on grading criteria
    total_scores = {}
    total_points = {}

    for result in results:
        total_score = result.test_score + result.exam_score
        total_scores[result.student_id] = total_score
        total_points[result.student_id] = result.points_earned

    # Step 3: Sort students based on total scores/points earned
    if criteria=='points':
       sorted_students_by_score = sorted(total_points.items(), key=lambda x: x[1], reverse=True)
    else:
        sorted_students_by_score = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)
    # Step 4: Calculate overall positions for each student
    overall_positions = {}
    for index, (student_id, _) in enumerate(sorted_students_by_score):
        overall_positions[student_id] = index + 1

    # Step 5: Calculate stream positions for each student within their sections
    stream_positions = {}
    sections = Class.sections.all()
    if len(sections)>2:
        for section in sections:
            section_results = results.filter(current_section=section)
            section_scores = {}

            for result in section_results:
                total_score = result.test_score + result.exam_score
                section_scores[result.student_id] = total_score

            sorted_students = sorted(section_scores.items(), key=lambda x: x[1], reverse=True)

            for index, (student_id, _) in enumerate(sorted_students):
                stream_positions[student_id] = index + 1
    else:
        stream_positions=overall_positions
    print(overall_positions,stream_positions)
    return [overall_positions, stream_positions]

