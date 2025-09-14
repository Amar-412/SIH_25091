"""
Web-based timetable generator using Flask.
Converts the Tkinter app to a web application for hosting.
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
import pandas as pd
import json
import os
from io import BytesIO
import base64
from werkzeug.utils import secure_filename
from solver import solve_timetable
from table_utils import parse_json_columns, serialize_json_columns

app = Flask(__name__)
app.secret_key = 'vicharak-timetable-generator-2024'  # Change this in production

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Global data storage
students_df = pd.DataFrame()
faculty_df = pd.DataFrame()
courses_df = pd.DataFrame()
rooms_df = pd.DataFrame()
constraints = {}
selections_df = pd.DataFrame(columns=['student_id', 'course_code', 'section', 'faculty_id'])
timetable_result = pd.DataFrame()

# JSON columns for each dataset
json_columns = {
    'students': ['chosen_courses'],
    'faculty': ['skills', 'availability'],
    'courses': ['allowed_days', 'allowed_start_slots', 'faculty_pool'],
    'rooms': ['availability']
}

def load_default_data():
    """Load default sample data."""
    global students_df, faculty_df, courses_df, rooms_df, constraints
    
    try:
        # Load constraints
        with open('data/constraints.json', 'r') as f:
            constraints = json.load(f)
        
        # Load CSV files
        students_df = pd.read_csv('data/students.csv')
        faculty_df = pd.read_csv('data/faculty.csv')
        courses_df = pd.read_csv('data/courses.csv')
        rooms_df = pd.read_csv('data/rooms.csv')
        
        # Parse JSON columns
        students_df = parse_json_columns(students_df, json_columns['students'])
        faculty_df = parse_json_columns(faculty_df, json_columns['faculty'])
        courses_df = parse_json_columns(courses_df, json_columns['courses'])
        rooms_df = parse_json_columns(rooms_df, json_columns['rooms'])
        
        print("Default data loaded successfully!")
        
    except Exception as e:
        print(f"Failed to load default data: {str(e)}")

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/api/debug')
def debug_data():
    """Debug endpoint to check data loading."""
    global students_df, faculty_df, courses_df, rooms_df, constraints
    
    return jsonify({
        'students_count': len(students_df),
        'faculty_count': len(faculty_df),
        'courses_count': len(courses_df),
        'rooms_count': len(rooms_df),
        'constraints_loaded': bool(constraints),
        'students_empty': students_df.empty,
        'faculty_empty': faculty_df.empty,
        'courses_empty': courses_df.empty,
        'rooms_empty': rooms_df.empty
    })

@app.route('/api/data/<data_type>')
def get_data(data_type):
    """Get data for a specific type."""
    global students_df, faculty_df, courses_df, rooms_df
    
    if data_type == 'students':
        df = students_df
    elif data_type == 'faculty':
        df = faculty_df
    elif data_type == 'courses':
        df = courses_df
    elif data_type == 'rooms':
        df = rooms_df
    else:
        return jsonify({'error': 'Invalid data type'}), 400
    
    # Convert to JSON-serializable format
    df_json = df.to_json(orient='records')
    return jsonify(json.loads(df_json))

@app.route('/api/data/<data_type>', methods=['POST'])
def update_data(data_type):
    """Update data for a specific type."""
    global students_df, faculty_df, courses_df, rooms_df
    
    data = request.get_json()
    df = pd.DataFrame(data)
    
    # Parse JSON columns
    if data_type in json_columns:
        df = parse_json_columns(df, json_columns[data_type])
    
    # Update the appropriate DataFrame
    if data_type == 'students':
        students_df = df
    elif data_type == 'faculty':
        faculty_df = df
    elif data_type == 'courses':
        courses_df = df
    elif data_type == 'rooms':
        rooms_df = df
    else:
        return jsonify({'error': 'Invalid data type'}), 400
    
    return jsonify({'success': True})

@app.route('/api/upload/<data_type>', methods=['POST'])
def upload_file(data_type):
    """Handle file upload for data."""
    global students_df, faculty_df, courses_df, rooms_df
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Load the file based on extension
            if filename.endswith('.json'):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:  # CSV
                df = pd.read_csv(filepath)
            
            # Parse JSON columns
            if data_type in json_columns:
                df = parse_json_columns(df, json_columns[data_type])
            
            # Update the appropriate DataFrame
            if data_type == 'students':
                students_df = df
            elif data_type == 'faculty':
                faculty_df = df
            elif data_type == 'courses':
                courses_df = df
            elif data_type == 'rooms':
                rooms_df = df
            else:
                return jsonify({'error': 'Invalid data type'}), 400
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify({'success': True, 'message': f'{data_type.title()} data loaded successfully!'})
            
        except Exception as e:
            return jsonify({'error': f'Error loading file: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Invalid file type. Please upload CSV or JSON files.'}), 400

@app.route('/api/add_row/<data_type>', methods=['POST'])
def add_row(data_type):
    """Add a new row to the specified dataset."""
    global students_df, faculty_df, courses_df, rooms_df
    
    try:
        if data_type == 'students':
            if students_df.empty:
                new_row = {'id': 1, 'name': 'New Student', 'program': 'Computer Science', 
                          'semester': 1, 'chosen_courses': [], 'credits_target': 16}
                students_df = pd.DataFrame([new_row])
            else:
                new_row = students_df.iloc[-1].copy()
                new_row['id'] = students_df['id'].max() + 1 if not students_df.empty else 1
                new_row['name'] = 'New Student'
                students_df = pd.concat([students_df, pd.DataFrame([new_row])], ignore_index=True)
                
        elif data_type == 'faculty':
            if faculty_df.empty:
                new_row = {'id': 1, 'name': 'New Faculty', 'skills': [], 'availability': [], 'max_load': 30}
                faculty_df = pd.DataFrame([new_row])
            else:
                new_row = faculty_df.iloc[-1].copy()
                new_row['id'] = faculty_df['id'].max() + 1 if not faculty_df.empty else 1
                new_row['name'] = 'New Faculty'
                faculty_df = pd.concat([faculty_df, pd.DataFrame([new_row])], ignore_index=True)
                
        elif data_type == 'courses':
            if courses_df.empty:
                new_row = {'code': 'NEW101', 'name': 'New Course', 'type': 'Major', 'credits': 3,
                          'T_hours': 2, 'P_hours': 1, 'program': 'Computer Science', 'semester': 1,
                          'section': 'A', 'duration_slots': 4, 'room_type': 'Classroom',
                          'allowed_days': [0, 1, 2, 3, 4], 'allowed_start_slots': [1, 3, 5, 7],
                          'faculty_pool': []}
                courses_df = pd.DataFrame([new_row])
            else:
                new_row = courses_df.iloc[-1].copy()
                new_row['code'] = f'NEW{len(courses_df) + 101}'
                new_row['name'] = 'New Course'
                courses_df = pd.concat([courses_df, pd.DataFrame([new_row])], ignore_index=True)
                
        elif data_type == 'rooms':
            if rooms_df.empty:
                new_row = {'id': 1, 'name': 'New Room', 'capacity': 30, 'type': 'Classroom',
                          'availability': [['Mon:1-16', 'Tue:1-16', 'Wed:1-16', 'Thu:1-16', 'Fri:1-16']]}
                rooms_df = pd.DataFrame([new_row])
            else:
                new_row = rooms_df.iloc[-1].copy()
                new_row['id'] = rooms_df['id'].max() + 1 if not rooms_df.empty else 1
                new_row['name'] = 'New Room'
                rooms_df = pd.concat([rooms_df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            return jsonify({'error': 'Invalid data type'}), 400
        
        return jsonify({'success': True, 'message': f'New row added to {data_type}'})
        
    except Exception as e:
        return jsonify({'error': f'Error adding row: {str(e)}'}), 500

@app.route('/api/remove_row/<data_type>', methods=['POST'])
def remove_row(data_type):
    """Remove a row from the specified dataset."""
    global students_df, faculty_df, courses_df, rooms_df
    
    try:
        data = request.get_json()
        row_index = data.get('index')
        
        if row_index is None:
            return jsonify({'error': 'No row index provided'}), 400
        
        if data_type == 'students':
            if not students_df.empty and 0 <= row_index < len(students_df):
                students_df = students_df.drop(students_df.index[row_index]).reset_index(drop=True)
            else:
                return jsonify({'error': 'Invalid row index'}), 400
        elif data_type == 'faculty':
            if not faculty_df.empty and 0 <= row_index < len(faculty_df):
                faculty_df = faculty_df.drop(faculty_df.index[row_index]).reset_index(drop=True)
            else:
                return jsonify({'error': 'Invalid row index'}), 400
        elif data_type == 'courses':
            if not courses_df.empty and 0 <= row_index < len(courses_df):
                courses_df = courses_df.drop(courses_df.index[row_index]).reset_index(drop=True)
            else:
                return jsonify({'error': 'Invalid row index'}), 400
        elif data_type == 'rooms':
            if not rooms_df.empty and 0 <= row_index < len(rooms_df):
                rooms_df = rooms_df.drop(rooms_df.index[row_index]).reset_index(drop=True)
            else:
                return jsonify({'error': 'Invalid row index'}), 400
        else:
            return jsonify({'error': 'Invalid data type'}), 400
        
        return jsonify({'success': True, 'message': f'Row removed from {data_type}'})
        
    except Exception as e:
        return jsonify({'error': f'Error removing row: {str(e)}'}), 500

@app.route('/api/selections', methods=['GET', 'POST'])
def handle_selections():
    """Handle course selections."""
    global selections_df
    
    if request.method == 'GET':
        return jsonify(selections_df.to_dict('records'))
    
    elif request.method == 'POST':
        data = request.get_json()
        if 'action' in data:
            if data['action'] == 'add':
                new_selection = pd.DataFrame([{
                    'student_id': data['student_id'],
                    'course_code': data['course_code'],
                    'section': data.get('section', 'A'),
                    'faculty_id': data.get('faculty_id', None)
                }])
                selections_df = pd.concat([selections_df, new_selection], ignore_index=True)
            elif data['action'] == 'clear':
                selections_df = pd.DataFrame(columns=['student_id', 'course_code', 'section', 'faculty_id'])
        
        return jsonify({'success': True, 'selections': selections_df.to_dict('records')})

@app.route('/api/generate', methods=['POST'])
def generate_timetable():
    """Generate timetable."""
    global timetable_result
    
    try:
        if selections_df.empty:
            return jsonify({'error': 'No course selections found. Please add some course selections first.'}), 400
        
        if students_df.empty or courses_df.empty or rooms_df.empty or faculty_df.empty:
            missing = []
            if students_df.empty:
                missing.append('students')
            if courses_df.empty:
                missing.append('courses')
            if rooms_df.empty:
                missing.append('rooms')
            if faculty_df.empty:
                missing.append('faculty')
            
            return jsonify({
                'error': f'Required datasets not loaded: {", ".join(missing)}. Please load the data files first.',
                'debug_info': {
                    'students_count': len(students_df),
                    'courses_count': len(courses_df),
                    'rooms_count': len(rooms_df),
                    'faculty_count': len(faculty_df)
                }
            }), 400
        
        # Generate timetable
        timetable_result = solve_timetable(
            students_df, courses_df, rooms_df, faculty_df,
            constraints, selections_df
        )
        
        return jsonify({
            'success': True,
            'timetable': timetable_result.to_dict('records')
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating timetable: {str(e)}'}), 500

@app.route('/api/export/<format>')
def export_timetable(format):
    """Export timetable."""
    global timetable_result
    
    if timetable_result.empty:
        return jsonify({'error': 'No timetable to export'}), 400
    
    if format == 'csv':
        output = BytesIO()
        timetable_result.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, mimetype='text/csv', as_attachment=True, 
                        download_name='timetable.csv')
    
    elif format == 'excel':
        output = BytesIO()
        timetable_result.to_excel(output, index=False)
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        as_attachment=True, download_name='timetable.xlsx')
    
    return jsonify({'error': 'Invalid format'}), 400

# Load default data when the module is imported
load_default_data()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
