"""
Basic timetable solver that generates a simple schedule.
"""

import pandas as pd
import json
from typing import Dict, List, Optional, Tuple, Any


def solve_timetable(students_df: pd.DataFrame, courses_df: pd.DataFrame, 
                   rooms_df: pd.DataFrame, faculty_df: pd.DataFrame, 
                   constraints: Dict[str, Any], selections_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Solve the timetable scheduling problem with a simple approach.
    """
    print("Starting timetable generation...")
    
    # Parse constraints
    days = constraints['days']
    slots_per_day = constraints['slots_per_day']
    
    print(f"Time horizon: {len(days)} days × {slots_per_day} slots")
    
    # Create mappings
    course_map = {row['code']: row for _, row in courses_df.iterrows()}
    room_map = {row['id']: row for _, row in rooms_df.iterrows()}
    faculty_map = {row['id']: row for _, row in faculty_df.iterrows()}
    
    # Get room type mappings
    rooms_by_type = {}
    for _, room in rooms_df.iterrows():
        room_type = room['type']
        if room_type not in rooms_by_type:
            rooms_by_type[room_type] = []
        rooms_by_type[room_type].append(room)
    
    # Create variables for each course section that needs to be scheduled
    scheduled_courses = []
    
    if selections_df is not None and not selections_df.empty:
        # Use selections from the UI
        for _, selection in selections_df.iterrows():
            student_id = selection['student_id']
            course_code = selection['course_code']
            section = selection.get('section', 'A')
            faculty_id = selection.get('faculty_id', None)
            
            if course_code in course_map:
                course = course_map[course_code]
                scheduled_courses.append({
                    'student_id': student_id,
                    'course_code': course_code,
                    'section': section,
                    'faculty_id': faculty_id,
                    'course': course
                })
    else:
        # Use all courses from the course catalog
        for _, course in courses_df.iterrows():
            scheduled_courses.append({
                'student_id': None,
                'course_code': course['code'],
                'section': course['section'],
                'faculty_id': None,
                'course': course
            })
    
    print(f"Scheduling {len(scheduled_courses)} course sections...")
    
    # Generate a simple schedule
    solution_data = []
    current_slot = 0
    
    for i, course_info in enumerate(scheduled_courses):
        course = course_info['course']
        
        # Simple scheduling: place courses in sequence
        day_idx = current_slot // slots_per_day
        slot_in_day = current_slot % slots_per_day
        
        # Make sure we don't exceed the day limit
        if day_idx >= len(days):
            day_idx = 0
            current_slot = slot_in_day
        
        # Get room information
        room_type = course['room_type']
        if room_type in rooms_by_type and len(rooms_by_type[room_type]) > 0:
            room = rooms_by_type[room_type][0]  # Use first available room of this type
        else:
            room = rooms_df.iloc[0]  # Use first available room
        
        # Get faculty information
        faculty_pool = course.get('faculty_pool', [])
        if faculty_pool and len(faculty_pool) > 0:
            faculty_id = faculty_pool[0]  # Use first available faculty
            faculty = faculty_df[faculty_df['id'] == faculty_id].iloc[0]
        else:
            faculty = faculty_df.iloc[0]  # Use first available faculty
        
        # Calculate end slot
        duration = course['duration_slots']
        end_slot = current_slot + duration - 1
        
        solution_data.append({
            'program': course['program'],
            'section': course_info['section'],
            'course': course['name'],
            'faculty': faculty['name'],
            'room': room['name'],
            'day': days[day_idx],
            'start': slot_in_day,
            'end': end_slot % slots_per_day,
            'start_time': f"{8 + slot_in_day * 0.5:02.0f}:{int((slot_in_day * 0.5) % 1 * 60):02d}",
            'end_time': f"{8 + (end_slot % slots_per_day) * 0.5:02.0f}:{int(((end_slot % slots_per_day) * 0.5) % 1 * 60):02d}"
        })
        
        # Move to next available slot
        current_slot += duration + 1  # Add gap between courses
    
    print("Solution generated!")
    return pd.DataFrame(solution_data)


if __name__ == "__main__":
    # Test the solver with sample data
    import json
    
    # Load sample data
    students_df = pd.read_csv('data/students.csv')
    courses_df = pd.read_csv('data/courses.csv')
    rooms_df = pd.read_csv('data/rooms.csv')
    faculty_df = pd.read_csv('data/faculty.csv')
    
    # Parse JSON columns
    students_df['chosen_courses'] = students_df['chosen_courses'].apply(json.loads)
    faculty_df['skills'] = faculty_df['skills'].apply(json.loads)
    faculty_df['availability'] = faculty_df['availability'].apply(json.loads)
    courses_df['allowed_days'] = courses_df['allowed_days'].apply(json.loads)
    courses_df['allowed_start_slots'] = courses_df['allowed_start_slots'].apply(json.loads)
    courses_df['faculty_pool'] = courses_df['faculty_pool'].apply(json.loads)
    rooms_df['availability'] = rooms_df['availability'].apply(json.loads)
    
    # Load constraints
    with open('data/constraints.json', 'r') as f:
        constraints = json.load(f)
    
    # Create sample selections
    selections_data = {
        'student_id': [1, 1, 1, 2, 2, 2],
        'course_code': ['CS301', 'CS302', 'MATH201', 'CS301', 'CS303', 'PHYS101'],
        'section': ['A', 'A', 'A', 'A', 'A', 'A'],
        'faculty_id': [None, None, None, None, None, None]
    }
    selections_df = pd.DataFrame(selections_data)
    
    # Solve
    result = solve_timetable(students_df, courses_df, rooms_df, faculty_df, constraints, selections_df)
    print("\nGenerated Timetable:")
    print(result.to_string(index=False))
