"""
Table utilities for rendering pandas DataFrames in Tkinter.
Supports both pandastable and ttk.Treeview fallback.
"""

import pandas as pd
import tkinter as tk
from tkinter import ttk
import json
from typing import Optional, List, Any

try:
    from pandastable import Table, TableModel
    PANDAS_TABLE_AVAILABLE = True
except ImportError:
    PANDAS_TABLE_AVAILABLE = False


class DataFrameTable:
    """Wrapper class for displaying pandas DataFrames in Tkinter."""
    
    def __init__(self, parent: tk.Widget, dataframe: Optional[pd.DataFrame] = None):
        self.parent = parent
        self.dataframe = dataframe
        self.table_widget = None
        self._create_table()
    
    def _create_table(self):
        """Create the appropriate table widget based on available libraries."""
        if PANDAS_TABLE_AVAILABLE and self.dataframe is not None:
            self._create_pandastable()
        else:
            self._create_treeview()
    
    def _create_pandastable(self):
        """Create a pandastable widget."""
        try:
            self.table_widget = Table(self.parent, dataframe=self.dataframe)
            self.table_widget.show()
        except Exception as e:
            print(f"Error creating pandastable: {e}")
            self._create_treeview()
    
    def _create_treeview(self):
        """Create a ttk.Treeview widget as fallback."""
        # Create frame with scrollbars
        frame = ttk.Frame(self.parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview
        self.table_widget = ttk.Treeview(frame)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.table_widget.yview)
        h_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.table_widget.xview)
        self.table_widget.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack widgets
        self.table_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        if self.dataframe is not None:
            self._populate_treeview()
    
    def _populate_treeview(self):
        """Populate the Treeview with DataFrame data."""
        if self.dataframe is None:
            return
        
        # Clear existing items
        for item in self.table_widget.get_children():
            self.table_widget.delete(item)
        
        # Configure columns
        columns = list(self.dataframe.columns)
        self.table_widget['columns'] = columns
        self.table_widget['show'] = 'headings'
        
        # Configure column headings and widths
        for col in columns:
            self.table_widget.heading(col, text=str(col))
            self.table_widget.column(col, width=100, minwidth=50)
        
        # Insert data
        for index, row in self.dataframe.iterrows():
            values = []
            for col in columns:
                value = row[col]
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)
                values.append(str(value))
            self.table_widget.insert('', tk.END, values=values)
    
    def update_dataframe(self, dataframe: pd.DataFrame):
        """Update the displayed DataFrame."""
        self.dataframe = dataframe
        if PANDAS_TABLE_AVAILABLE and hasattr(self.table_widget, 'model'):
            # Update pandastable
            self.table_widget.model.df = dataframe
            self.table_widget.redraw()
        else:
            # Update Treeview
            self._populate_treeview()
    
    def get_selected_row(self) -> Optional[int]:
        """Get the index of the selected row."""
        if PANDAS_TABLE_AVAILABLE and hasattr(self.table_widget, 'getSelectedRow'):
            return self.table_widget.getSelectedRow()
        else:
            selection = self.table_widget.selection()
            if selection:
                return self.table_widget.index(selection[0])
        return None
    
    def destroy(self):
        """Destroy the table widget."""
        if self.table_widget:
            self.table_widget.destroy()


def parse_json_columns(dataframe: pd.DataFrame, json_columns: List[str]) -> pd.DataFrame:
    """Parse JSON string columns in a DataFrame."""
    df = dataframe.copy()
    for col in json_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: json.loads(x) if isinstance(x, str) and x.startswith('[') else x)
    return df


def serialize_json_columns(dataframe: pd.DataFrame, json_columns: List[str]) -> pd.DataFrame:
    """Serialize list/dict columns to JSON strings for CSV export."""
    df = dataframe.copy()
    for col in json_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)
    return df


def create_sample_dataframes():
    """Create sample DataFrames for testing."""
    # Students DataFrame
    students_data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson'],
        'program': ['Computer Science', 'Computer Science', 'Electronics', 'Computer Science', 'Electronics'],
        'semester': [3, 3, 5, 1, 5],
        'chosen_courses': [['CS301', 'CS302', 'MATH201'], ['CS301', 'CS303', 'PHYS101'], 
                          ['EE401', 'EE402', 'MATH301'], ['CS101', 'MATH101', 'ENG101'], 
                          ['EE401', 'EE403', 'CS201']],
        'credits_target': [18, 18, 20, 16, 20]
    }
    students_df = pd.DataFrame(students_data)
    
    # Faculty DataFrame
    faculty_data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Dr. Smith', 'Prof. Johnson', 'Dr. Brown', 'Prof. Davis', 'Dr. Wilson'],
        'skills': [['Computer Science', 'Algorithms', 'Data Structures'], 
                  ['Mathematics', 'Calculus', 'Linear Algebra'],
                  ['Electronics', 'Circuit Design', 'Digital Systems'],
                  ['Physics', 'Mechanics', 'Thermodynamics'],
                  ['Computer Science', 'Software Engineering', 'Database Systems']],
        'availability': [['Mon:1-8', 'Tue:1-8', 'Wed:1-8', 'Thu:1-8', 'Fri:1-8'],
                        ['Mon:1-6', 'Tue:1-6', 'Wed:1-6', 'Thu:1-6', 'Fri:1-6'],
                        ['Mon:2-8', 'Tue:2-8', 'Wed:2-8', 'Thu:2-8', 'Fri:2-8'],
                        ['Mon:1-4', 'Tue:1-4', 'Wed:1-4', 'Thu:1-4', 'Fri:1-4'],
                        ['Mon:3-8', 'Tue:3-8', 'Wed:3-8', 'Thu:3-8', 'Fri:3-8']],
        'max_load': [40, 30, 35, 25, 40]
    }
    faculty_df = pd.DataFrame(faculty_data)
    
    # Courses DataFrame
    courses_data = {
        'code': ['CS301', 'CS302', 'CS303', 'CS101', 'CS201', 'MATH201', 'MATH101', 'MATH301', 'PHYS101', 'ENG101', 'EE401', 'EE402', 'EE403'],
        'name': ['Data Structures', 'Algorithms', 'Software Engineering', 'Programming Fundamentals', 
                'Object-Oriented Programming', 'Calculus III', 'Calculus I', 'Linear Algebra', 
                'Physics I', 'Technical Writing', 'Digital Electronics', 'Control Systems', 'Microprocessors'],
        'type': ['Major', 'Major', 'Major', 'Major', 'Major', 'Major', 'Major', 'Major', 'Major', 'Skill', 'Major', 'Major', 'Major'],
        'credits': [4, 4, 3, 4, 3, 4, 4, 3, 4, 2, 4, 4, 3],
        'T_hours': [3, 3, 2, 3, 2, 3, 3, 2, 3, 2, 3, 3, 2],
        'P_hours': [2, 2, 2, 2, 2, 1, 1, 1, 2, 0, 2, 2, 2],
        'program': ['Computer Science', 'Computer Science', 'Computer Science', 'Computer Science', 'Computer Science',
                   'Computer Science', 'Computer Science', 'Electronics', 'Computer Science', 'Computer Science',
                   'Electronics', 'Electronics', 'Electronics'],
        'semester': [3, 3, 3, 1, 2, 3, 1, 5, 1, 1, 5, 5, 5],
        'section': ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A'],
        'duration_slots': [6, 6, 4, 6, 4, 4, 4, 3, 5, 2, 6, 6, 4],
        'room_type': ['Lecture Hall', 'Lecture Hall', 'Computer Lab', 'Computer Lab', 'Computer Lab',
                     'Lecture Hall', 'Lecture Hall', 'Lecture Hall', 'Physics Lab', 'Classroom',
                     'Electronics Lab', 'Electronics Lab', 'Computer Lab'],
        'allowed_days': [[0, 1, 2, 3, 4]] * 13,
        'allowed_start_slots': [[1, 3, 5, 7, 9], [1, 3, 5, 7, 9], [1, 3, 5, 7], [1, 3, 5, 7, 9], [1, 3, 5, 7],
                               [1, 3, 5, 7], [1, 3, 5, 7], [1, 3, 5], [1, 3, 5, 7], [1, 3, 5, 7],
                               [1, 3, 5, 7, 9], [1, 3, 5, 7, 9], [1, 3, 5, 7]],
        'faculty_pool': [[1, 5], [1, 5], [5], [1, 5], [5], [2], [2], [2], [4], [1, 2, 3, 4, 5], [3], [3], [3, 5]]
    }
    courses_df = pd.DataFrame(courses_data)
    
    # Rooms DataFrame
    rooms_data = {
        'id': [1, 2, 3, 4, 5, 6, 7, 8],
        'name': ['Lecture Hall A', 'Lecture Hall B', 'Computer Lab 1', 'Computer Lab 2', 
                'Physics Lab', 'Electronics Lab', 'Classroom 101', 'Classroom 102'],
        'capacity': [100, 80, 30, 30, 25, 20, 40, 40],
        'type': ['Lecture Hall', 'Lecture Hall', 'Computer Lab', 'Computer Lab', 
                'Physics Lab', 'Electronics Lab', 'Classroom', 'Classroom'],
        'availability': [['Mon:1-16', 'Tue:1-16', 'Wed:1-16', 'Thu:1-16', 'Fri:1-16']] * 8
    }
    rooms_df = pd.DataFrame(rooms_data)
    
    return students_df, faculty_df, courses_df, rooms_df


if __name__ == "__main__":
    # Test the table utilities
    root = tk.Tk()
    root.title("Table Utils Test")
    
    # Create sample data
    students_df, faculty_df, courses_df, rooms_df = create_sample_dataframes()
    
    # Test DataFrameTable
    table = DataFrameTable(root, students_df)
    
    root.mainloop()
