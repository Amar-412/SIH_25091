# Vicharak - An Artificial Inteliigent Model for Timetable Generation

A Python-based timetable generator that implements NEP-2020-aligned scheduling using OR-Tools CP-SAT solver. The application provides a comprehensive desktop interface for managing students, faculty, courses, and resources, with automated timetable generation capabilities.

## Features

- **Five-tab Interface**: Students, Faculty, Courses, Resources, and Generate Timetable
- **Data Management**: Load/save CSV/JSON files with full CRUD operations
- **OR-Tools Integration**: Advanced constraint programming for optimal scheduling
- **NEP-2020 Compliance**: Aligned with National Education Policy 2020 requirements
- **Multiple Export Formats**: CSV and Excel export capabilities
- **Calendar View**: Visual timetable display with weekly grid
- **Flexible Constraints**: Configurable time slots, room assignments, and faculty availability

## Installation

1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd tlinker
   ```

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

## Dependencies

- **pandas** (>=1.5.0): Data manipulation and analysis
- **ortools** (>=9.5.0): Google's optimization tools for constraint programming
- **pandastable** (>=0.13.0): Enhanced DataFrame display in Tkinter
- **openpyxl** (>=3.0.0): Excel file support for export functionality

## Project Structure

```
tlinker/
├── app.py                 # Main Tkinter application
├── solver.py             # OR-Tools CP-SAT solver implementation
├── table_utils.py        # DataFrame rendering utilities
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── data/                # Sample data files
    ├── students.csv     # Student information
    ├── faculty.csv      # Faculty information
    ├── courses.csv      # Course catalog
    ├── rooms.csv        # Room/resource information
    └── constraints.json # Scheduling constraints
```

## Usage Guide

### 1. Data Management

#### Students Tab
- **Load Data**: Import student information from CSV/JSON files
- **Add Students**: Create new student records with program and semester details
- **Edit Data**: Modify existing student information directly in the table
- **Save Data**: Export updated data to CSV/JSON format

**Student Data Fields**:
- `id`: Unique student identifier
- `name`: Student's full name
- `program`: Academic program (e.g., Computer Science, Electronics)
- `semester`: Current semester number
- `chosen_courses`: JSON list of selected course codes
- `credits_target`: Target credit hours for the semester

#### Faculty Tab
- **Load Data**: Import faculty information from CSV/JSON files
- **Add Faculty**: Create new faculty records with skills and availability
- **Edit Data**: Modify faculty information and teaching loads
- **Save Data**: Export updated faculty data

**Faculty Data Fields**:
- `id`: Unique faculty identifier
- `name`: Faculty member's full name
- `skills`: JSON list of teaching specializations
- `availability`: JSON list of available time windows
- `max_load`: Maximum teaching load (hours per week)

#### Courses Tab
- **Load Data**: Import course catalog from CSV/JSON files
- **Add Courses**: Create new course entries with scheduling constraints
- **Edit Data**: Modify course requirements and constraints
- **Save Data**: Export updated course catalog

**Course Data Fields**:
- `code`: Course code (e.g., CS301, MATH201)
- `name`: Course title
- `type`: Course type (Major/Minor/Skill/Value-Added)
- `credits`: Credit hours
- `T_hours`: Theory hours per week
- `P_hours`: Practical hours per week
- `program`: Target program
- `semester`: Recommended semester
- `section`: Section identifier
- `duration_slots`: Duration in time slots
- `room_type`: Required room type
- `allowed_days`: JSON list of allowed days (0=Mon, 1=Tue, etc.)
- `allowed_start_slots`: JSON list of allowed start times
- `faculty_pool`: JSON list of eligible faculty IDs

#### Resources Tab
- **Load Data**: Import room and resource information
- **Add Rooms**: Create new room entries with capacity and type
- **Edit Data**: Modify room specifications and availability
- **Save Data**: Export updated resource data

**Room Data Fields**:
- `id`: Unique room identifier
- `name`: Room name or number
- `capacity`: Maximum occupancy
- `type`: Room type (Lecture Hall, Computer Lab, etc.)
- `availability`: JSON list of available time windows

### 2. Timetable Generation

#### Generate Timetable Tab

1. **Course Selection**:
   - Select a student from the dropdown
   - Choose a course from the available options
   - Specify the section (defaults to "A")
   - Optionally assign a specific faculty member
   - Click "Add Selection" to add the course to the selection list

2. **Generate Timetable**:
   - Click "Generate Timetable" to run the OR-Tools solver
   - The system will attempt to find a feasible schedule within the time limit
   - Results are displayed in both tabular and calendar formats

3. **Export Results**:
   - Use "Export CSV" to save the timetable as a CSV file
   - Use "Export Excel" to save the timetable as an Excel file

#### Calendar View
- **Weekly Grid**: Visual representation of the weekly schedule
- **Time Slots**: 30-minute intervals from 8:00 AM to 4:00 PM
- **Course Blocks**: Color-coded blocks showing course, section, and room
- **Multi-slot Courses**: Courses spanning multiple time slots are clearly indicated

## Configuration

### Constraints File (data/constraints.json)

```json
{
  "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
  "slots_per_day": 16,
  "slot_minutes": 30,
  "time_limit_sec": 30,
  "soft_weights": {
    "prefer_morning": 1.0,
    "prefer_afternoon": 0.5,
    "avoid_gaps": 2.0,
    "room_capacity_utilization": 1.5
  }
}
```

**Configuration Parameters**:
- `days`: List of working days
- `slots_per_day`: Number of time slots per day
- `slot_minutes`: Duration of each time slot in minutes
- `time_limit_sec`: Maximum solver time in seconds
- `soft_weights`: Weights for soft constraints (future use)

## Solver Algorithm

The timetable generation uses Google's OR-Tools CP-SAT solver with the following constraints:

### Hard Constraints
1. **Room Availability**: No two courses can use the same room simultaneously
2. **Faculty Availability**: No faculty member can teach multiple courses at the same time
3. **Student Conflicts**: No student can attend multiple courses simultaneously
4. **Time Windows**: Courses must be scheduled within allowed days and time slots
5. **Room Type Matching**: Courses must be assigned to appropriate room types

### Optimization Objective
- **Minimize Total Start Time**: Prefers earlier scheduling when possible
- **Room Utilization**: Efficient use of available resources
- **Faculty Load Balancing**: Distribute teaching load evenly

## Sample Data

The application includes sample data files in the `data/` directory:

- **students.csv**: 5 sample students from Computer Science and Electronics programs
- **faculty.csv**: 5 faculty members with different specializations
- **courses.csv**: 13 courses covering various subjects and programs
- **rooms.csv**: 8 different room types with varying capacities
- **constraints.json**: Default scheduling constraints

## Troubleshooting

### Common Issues

1. **"No solution found"**:
   - Check if all required datasets are loaded
   - Verify that course selections don't have conflicts
   - Increase the time limit in constraints.json
   - Ensure faculty and room availability matches course requirements

2. **Import/Export Errors**:
   - Verify file format (CSV or JSON)
   - Check that JSON columns are properly formatted
   - Ensure all required columns are present

3. **UI Display Issues**:
   - Try refreshing the pickers after loading new data
   - Clear selections and re-add them
   - Restart the application if tables don't update

### Performance Tips

1. **Large Datasets**: For large numbers of students/courses, consider:
   - Grouping students with identical course selections
   - Using shorter time limits for initial testing
   - Breaking down the problem into smaller chunks

2. **Complex Constraints**: If scheduling fails frequently:
   - Simplify course requirements
   - Increase room and faculty availability
   - Adjust time slot granularity

## Extending the System

### Adding New Constraints

The solver can be extended with additional constraints in `solver.py`:

1. **Capacity Constraints**: Ensure room capacity matches enrollment
2. **Faculty Preferences**: Respect faculty day-off preferences
3. **Course Prerequisites**: Schedule prerequisite courses before advanced ones
4. **Lab Equipment**: Ensure specialized equipment availability

### Custom Objectives

Modify the objective function in `_add_objective()` method:
- Minimize gaps between classes
- Maximize room utilization
- Balance faculty workload
- Prefer certain time slots

### Additional Export Formats

Add new export functions in `app.py`:
- ICS calendar format for integration with calendar applications
- PDF reports with formatted timetables
- Database integration for persistent storage

## License

This project is provided as-is for educational and research purposes. Please ensure compliance with OR-Tools licensing requirements for commercial use.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Verify all dependencies are correctly installed
3. Test with the provided sample data first
4. Review the constraint configuration for conflicts

## Future Enhancements

- **Web Interface**: Convert to web-based application
- **Database Integration**: Replace CSV/JSON with proper database
- **Advanced Constraints**: Add more sophisticated scheduling rules
- **Multi-semester Planning**: Support for full academic year planning
- **Real-time Updates**: Live updates when data changes
- **Mobile App**: Companion mobile application for students and faculty

