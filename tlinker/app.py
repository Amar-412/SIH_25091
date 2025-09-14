"""
Main Tkinter application for NEP-2020-aligned timetable generator.
Implements a tabbed interface with data management and timetable generation.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import json
import os
from typing import Dict, List, Optional, Any

from table_utils import DataFrameTable, parse_json_columns, serialize_json_columns
from solver import solve_timetable


class TimetableApp:
    """Main application class for the timetable generator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Vicharak - NEP-2020 Timetable Generator")
        self.root.geometry("1200x800")
        
        # Data storage
        self.students_df = pd.DataFrame()
        self.faculty_df = pd.DataFrame()
        self.courses_df = pd.DataFrame()
        self.rooms_df = pd.DataFrame()
        self.constraints = {}
        self.selections_df = pd.DataFrame(columns=['student_id', 'course_code', 'section', 'faculty_id'])
        self.timetable_result = pd.DataFrame()
        
        # JSON columns for each dataset
        self.json_columns = {
            'students': ['chosen_courses'],
            'faculty': ['skills', 'availability'],
            'courses': ['allowed_days', 'allowed_start_slots', 'faculty_pool'],
            'rooms': ['availability']
        }
        
        # UI components
        self.notebook = None
        self.tables = {}
        self.selection_table = None
        self.timetable_table = None
        self.calendar_frame = None
        
        # Comboboxes for selections
        self.student_combo = None
        self.course_combo = None
        self.section_combo = None
        self.faculty_combo = None
        
        self._setup_ui()
        self._load_default_data()
    
    def _setup_ui(self):
        """Set up the main UI with tabs."""
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        
        # Create main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self._create_students_tab()
        self._create_faculty_tab()
        self._create_courses_tab()
        self._create_rooms_tab()
        self._create_generate_tab()
    
    def _create_students_tab(self):
        """Create the Students tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Students")
        
        # Title
        title_label = ttk.Label(tab, text="Student Management", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Toolbar
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(toolbar, text="Load CSV/JSON", command=lambda: self._load_data('students')).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Save CSV/JSON", command=lambda: self._save_data('students')).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Add Row", command=lambda: self._add_row('students')).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Remove Row", command=lambda: self._remove_row('students')).pack(side=tk.LEFT, padx=5)
        
        # Table
        self.tables['students'] = DataFrameTable(tab, self.students_df)
    
    def _create_faculty_tab(self):
        """Create the Faculty tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Faculty")
        
        # Title
        title_label = ttk.Label(tab, text="Faculty Management", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Toolbar
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(toolbar, text="Load CSV/JSON", command=lambda: self._load_data('faculty')).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Save CSV/JSON", command=lambda: self._save_data('faculty')).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Add Row", command=lambda: self._add_row('faculty')).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Remove Row", command=lambda: self._remove_row('faculty')).pack(side=tk.LEFT, padx=5)
        
        # Table
        self.tables['faculty'] = DataFrameTable(tab, self.faculty_df)
    
    def _create_courses_tab(self):
        """Create the Courses tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Courses")
        
        # Title
        title_label = ttk.Label(tab, text="Course Management", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Toolbar
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(toolbar, text="Load CSV/JSON", command=lambda: self._load_data('courses')).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Save CSV/JSON", command=lambda: self._save_data('courses')).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Add Row", command=lambda: self._add_row('courses')).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Remove Row", command=lambda: self._remove_row('courses')).pack(side=tk.LEFT, padx=5)
        
        # Table
        self.tables['courses'] = DataFrameTable(tab, self.courses_df)
    
    def _create_rooms_tab(self):
        """Create the Resources tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Resources")
        
        # Title
        title_label = ttk.Label(tab, text="Room Management", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Toolbar
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(toolbar, text="Load CSV/JSON", command=lambda: self._load_data('rooms')).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Save CSV/JSON", command=lambda: self._save_data('rooms')).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Add Row", command=lambda: self._add_row('rooms')).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Remove Row", command=lambda: self._remove_row('rooms')).pack(side=tk.LEFT, padx=5)
        
        # Table
        self.tables['rooms'] = DataFrameTable(tab, self.rooms_df)
    
    def _create_generate_tab(self):
        """Create the Generate Timetable tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Generate Timetable")
        
        # Title
        title_label = ttk.Label(tab, text="Timetable Generation", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Main content frame
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Selection controls
        left_panel = ttk.LabelFrame(main_frame, text="Course Selection", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Selection controls
        controls_frame = ttk.Frame(left_panel)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Student selection
        ttk.Label(controls_frame, text="Student:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.student_combo = ttk.Combobox(controls_frame, state="readonly", width=20)
        self.student_combo.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Course selection
        ttk.Label(controls_frame, text="Course:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.course_combo = ttk.Combobox(controls_frame, state="readonly", width=20)
        self.course_combo.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Section selection
        ttk.Label(controls_frame, text="Section:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.section_combo = ttk.Combobox(controls_frame, state="readonly", width=20)
        self.section_combo.grid(row=2, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Faculty selection
        ttk.Label(controls_frame, text="Faculty (Optional):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.faculty_combo = ttk.Combobox(controls_frame, state="readonly", width=20)
        self.faculty_combo.grid(row=3, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Refresh Pickers", command=self._refresh_pickers).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Add Selection", command=self._add_selection).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear Selections", command=self._clear_selections).pack(side=tk.LEFT, padx=2)
        
        # Current selections table
        selections_label = ttk.Label(left_panel, text="Current Selections:", style='Header.TLabel')
        selections_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.selection_table = DataFrameTable(left_panel, self.selections_df)
        
        # Right panel - Results
        right_panel = ttk.LabelFrame(main_frame, text="Timetable Results", padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Generation controls
        gen_controls = ttk.Frame(right_panel)
        gen_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(gen_controls, text="Generate Timetable", command=self._generate_timetable).pack(side=tk.LEFT, padx=2)
        ttk.Button(gen_controls, text="Export CSV", command=self._export_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(gen_controls, text="Export Excel", command=self._export_excel).pack(side=tk.LEFT, padx=2)
        
        # Timetable table
        timetable_label = ttk.Label(right_panel, text="Generated Timetable:", style='Header.TLabel')
        timetable_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.timetable_table = DataFrameTable(right_panel, self.timetable_result)
        
        # Calendar view
        calendar_label = ttk.Label(right_panel, text="Calendar View:", style='Header.TLabel')
        calendar_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.calendar_frame = ttk.Frame(right_panel)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True)
    
    def _load_default_data(self):
        """Load default sample data."""
        try:
            # Load constraints
            with open('data/constraints.json', 'r') as f:
                self.constraints = json.load(f)
            
            # Load CSV files
            self.students_df = pd.read_csv('data/students.csv')
            self.faculty_df = pd.read_csv('data/faculty.csv')
            self.courses_df = pd.read_csv('data/courses.csv')
            self.rooms_df = pd.read_csv('data/rooms.csv')
            
            # Parse JSON columns
            self.students_df = parse_json_columns(self.students_df, self.json_columns['students'])
            self.faculty_df = parse_json_columns(self.faculty_df, self.json_columns['faculty'])
            self.courses_df = parse_json_columns(self.courses_df, self.json_columns['courses'])
            self.rooms_df = parse_json_columns(self.rooms_df, self.json_columns['rooms'])
            
            # Update tables
            for table_name, table in self.tables.items():
                if table_name in ['students', 'faculty', 'courses', 'rooms']:
                    df = getattr(self, f'{table_name}_df')
                    table.update_dataframe(df)
            
            # Refresh pickers
            self._refresh_pickers()
            
            print("Default data loaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load default data: {str(e)}")
    
    def _load_data(self, data_type: str):
        """Load data from CSV/JSON file."""
        file_path = filedialog.askopenfilename(
            title=f"Load {data_type.title()} Data",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    df = pd.DataFrame(data)
                else:
                    df = pd.read_csv(file_path)
                
                # Parse JSON columns
                if data_type in self.json_columns:
                    df = parse_json_columns(df, self.json_columns[data_type])
                
                # Update the appropriate DataFrame
                setattr(self, f'{data_type}_df', df)
                
                # Update the table
                self.tables[data_type].update_dataframe(df)
                
                # Refresh pickers if on generate tab
                if data_type in ['students', 'courses', 'faculty']:
                    self._refresh_pickers()
                
                messagebox.showinfo("Success", f"{data_type.title()} data loaded successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {data_type} data: {str(e)}")
    
    def _save_data(self, data_type: str):
        """Save data to CSV/JSON file."""
        file_path = filedialog.asksaveasfilename(
            title=f"Save {data_type.title()} Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                df = getattr(self, f'{data_type}_df')
                
                if file_path.endswith('.json'):
                    # Serialize JSON columns for JSON export
                    if data_type in self.json_columns:
                        df = serialize_json_columns(df, self.json_columns[data_type])
                    df.to_json(file_path, orient='records', indent=2)
                else:
                    # Serialize JSON columns for CSV export
                    if data_type in self.json_columns:
                        df = serialize_json_columns(df, self.json_columns[data_type])
                    df.to_csv(file_path, index=False)
                
                messagebox.showinfo("Success", f"{data_type.title()} data saved successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save {data_type} data: {str(e)}")
    
    def _add_row(self, data_type: str):
        """Add a new row to the specified DataFrame."""
        df = getattr(self, f'{data_type}_df')
        
        if df.empty:
            # Create a new DataFrame with default columns
            if data_type == 'students':
                new_row = {'id': 1, 'name': 'New Student', 'program': 'Computer Science', 
                          'semester': 1, 'chosen_courses': [], 'credits_target': 16}
            elif data_type == 'faculty':
                new_row = {'id': 1, 'name': 'New Faculty', 'skills': [], 'availability': [], 'max_load': 30}
            elif data_type == 'courses':
                new_row = {'code': 'NEW101', 'name': 'New Course', 'type': 'Major', 'credits': 3,
                          'T_hours': 2, 'P_hours': 1, 'program': 'Computer Science', 'semester': 1,
                          'section': 'A', 'duration_slots': 4, 'room_type': 'Classroom',
                          'allowed_days': [0, 1, 2, 3, 4], 'allowed_start_slots': [1, 3, 5, 7],
                          'faculty_pool': []}
            elif data_type == 'rooms':
                new_row = {'id': 1, 'name': 'New Room', 'capacity': 30, 'type': 'Classroom',
                          'availability': [['Mon:1-16', 'Tue:1-16', 'Wed:1-16', 'Thu:1-16', 'Fri:1-16']]}
            
            df = pd.DataFrame([new_row])
        else:
            # Add a new row with default values
            new_row = df.iloc[-1].copy()
            if 'id' in new_row:
                new_row['id'] = df['id'].max() + 1 if not df.empty else 1
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        setattr(self, f'{data_type}_df', df)
        self.tables[data_type].update_dataframe(df)
    
    def _remove_row(self, data_type: str):
        """Remove selected row from the specified DataFrame."""
        table = self.tables[data_type]
        selected_row = table.get_selected_row()
        
        if selected_row is not None:
            df = getattr(self, f'{data_type}_df')
            if not df.empty and 0 <= selected_row < len(df):
                df = df.drop(df.index[selected_row]).reset_index(drop=True)
                setattr(self, f'{data_type}_df', df)
                table.update_dataframe(df)
                
                # Refresh pickers if needed
                if data_type in ['students', 'courses', 'faculty']:
                    self._refresh_pickers()
        else:
            messagebox.showwarning("Warning", "Please select a row to remove.")
    
    def _refresh_pickers(self):
        """Refresh the combobox values from current DataFrames."""
        # Update student combo
        if not self.students_df.empty:
            student_options = [f"{row['id']} - {row['name']}" for _, row in self.students_df.iterrows()]
            self.student_combo['values'] = student_options
            if student_options:
                self.student_combo.set(student_options[0])
        
        # Update course combo
        if not self.courses_df.empty:
            course_options = [f"{row['code']} - {row['name']}" for _, row in self.courses_df.iterrows()]
            self.course_combo['values'] = course_options
            if course_options:
                self.course_combo.set(course_options[0])
        
        # Update section combo
        if not self.courses_df.empty:
            sections = sorted(self.courses_df['section'].unique())
            self.section_combo['values'] = sections
            if sections:
                self.section_combo.set(sections[0])
        
        # Update faculty combo
        if not self.faculty_df.empty:
            faculty_options = [f"{row['id']} - {row['name']}" for _, row in self.faculty_df.iterrows()]
            self.faculty_combo['values'] = faculty_options
            if faculty_options:
                self.faculty_combo.set("")
    
    def _add_selection(self):
        """Add a course selection to the selections DataFrame."""
        student_text = self.student_combo.get()
        course_text = self.course_combo.get()
        section = self.section_combo.get()
        faculty_text = self.faculty_combo.get()
        
        if not student_text or not course_text:
            messagebox.showwarning("Warning", "Please select both student and course.")
            return
        
        # Parse student ID
        student_id = int(student_text.split(' - ')[0])
        
        # Parse course code
        course_code = course_text.split(' - ')[0]
        
        # Parse faculty ID if selected
        faculty_id = None
        if faculty_text:
            faculty_id = int(faculty_text.split(' - ')[0])
        
        # Add to selections
        new_selection = pd.DataFrame([{
            'student_id': student_id,
            'course_code': course_code,
            'section': section,
            'faculty_id': faculty_id
        }])
        
        self.selections_df = pd.concat([self.selections_df, new_selection], ignore_index=True)
        self.selection_table.update_dataframe(self.selections_df)
    
    def _clear_selections(self):
        """Clear all course selections."""
        self.selections_df = pd.DataFrame(columns=['student_id', 'course_code', 'section', 'faculty_id'])
        self.selection_table.update_dataframe(self.selections_df)
    
    def _generate_timetable(self):
        """Generate the timetable using the solver."""
        if self.selections_df.empty:
            messagebox.showwarning("Warning", "Please add some course selections first.")
            return
        
        if self.students_df.empty or self.courses_df.empty or self.rooms_df.empty or self.faculty_df.empty:
            messagebox.showwarning("Warning", "Please load all required datasets first.")
            return
        
        try:
            # Generate timetable
            self.timetable_result = solve_timetable(
                self.students_df, self.courses_df, self.rooms_df, self.faculty_df,
                self.constraints, self.selections_df
            )
            
            # Update the timetable table
            self.timetable_table.update_dataframe(self.timetable_result)
            
            # Update calendar view
            self._update_calendar_view()
            
            messagebox.showinfo("Success", "Timetable generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate timetable: {str(e)}")
    
    def _update_calendar_view(self):
        """Update the calendar grid view."""
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        if self.timetable_result.empty:
            return
        
        # Get constraints
        days = self.constraints.get('days', ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])
        slots_per_day = self.constraints.get('slots_per_day', 16)
        
        # Create calendar grid
        # Headers
        for i, day in enumerate(days):
            label = ttk.Label(self.calendar_frame, text=day, style='Header.TLabel')
            label.grid(row=0, column=i+1, padx=2, pady=2, sticky='ew')
        
        # Time slots
        for slot in range(slots_per_day):
            time_str = f"{8 + slot * 0.5:02.0f}:{int((slot * 0.5) % 1 * 60):02d}"
            time_label = ttk.Label(self.calendar_frame, text=time_str, style='Header.TLabel')
            time_label.grid(row=slot+1, column=0, padx=2, pady=2, sticky='ew')
        
        # Configure grid weights
        for i in range(len(days) + 1):
            self.calendar_frame.columnconfigure(i, weight=1)
        for i in range(slots_per_day + 1):
            self.calendar_frame.rowconfigure(i, weight=1)
        
        # Fill in scheduled courses
        for _, row in self.timetable_result.iterrows():
            day_idx = days.index(row['day'])
            start_slot = row['start']
            end_slot = row['end']
            
            # Create course label
            course_text = f"{row['course']}\n{row['section']}\n{row['room']}"
            course_label = ttk.Label(
                self.calendar_frame, 
                text=course_text, 
                background='lightblue',
                relief='solid',
                borderwidth=1
            )
            
            # Span multiple rows if course lasts multiple slots
            rowspan = max(1, end_slot - start_slot + 1)
            course_label.grid(
                row=start_slot+1, 
                column=day_idx+1, 
                rowspan=rowspan,
                padx=1, pady=1, 
                sticky='nsew'
            )
    
    def _export_csv(self):
        """Export timetable to CSV."""
        if self.timetable_result.empty:
            messagebox.showwarning("Warning", "No timetable to export. Generate a timetable first.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Timetable as CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.timetable_result.to_csv(file_path, index=False)
                messagebox.showinfo("Success", "Timetable exported to CSV successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
    
    def _export_excel(self):
        """Export timetable to Excel."""
        if self.timetable_result.empty:
            messagebox.showwarning("Warning", "No timetable to export. Generate a timetable first.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Timetable as Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.timetable_result.to_excel(file_path, index=False)
                messagebox.showinfo("Success", "Timetable exported to Excel successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export Excel: {str(e)}")


def main():
    """Main function to run the application."""
    root = tk.Tk()
    app = TimetableApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
