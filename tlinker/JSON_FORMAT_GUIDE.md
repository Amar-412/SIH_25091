# JSON File Format Guide for Vicharak

This guide explains the exact JSON format for courses and resources (rooms) files that can be uploaded to Vicharak.

## 📚 **Courses JSON Format**

### **Structure:**
```json
[
  {
    "code": "string",           // Course code (e.g., "CS301")
    "name": "string",           // Course name (e.g., "Data Structures")
    "type": "string",           // Course type: "Major", "Minor", "Skill", "Value-Added"
    "credits": number,          // Credit hours (e.g., 4)
    "T_hours": number,          // Theory hours per week (e.g., 3)
    "P_hours": number,          // Practical hours per week (e.g., 2)
    "program": "string",        // Program name (e.g., "Computer Science")
    "semester": number,         // Semester number (e.g., 3)
    "section": "string",        // Section (e.g., "A")
    "duration_slots": number,   // Duration in time slots (e.g., 6)
    "room_type": "string",      // Required room type
    "allowed_days": [array],    // Array of day indices (0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri)
    "allowed_start_slots": [array], // Array of allowed start slot numbers
    "faculty_pool": [array]     // Array of faculty IDs who can teach this course
  }
]
```

### **Example Courses JSON:**
```json
[
  {
    "code": "CS301",
    "name": "Data Structures",
    "type": "Major",
    "credits": 4,
    "T_hours": 3,
    "P_hours": 2,
    "program": "Computer Science",
    "semester": 3,
    "section": "A",
    "duration_slots": 6,
    "room_type": "Lecture Hall",
    "allowed_days": [0, 1, 2, 3, 4],
    "allowed_start_slots": [1, 3, 5, 7, 9],
    "faculty_pool": [1, 5]
  },
  {
    "code": "MATH201",
    "name": "Calculus III",
    "type": "Major",
    "credits": 4,
    "T_hours": 3,
    "P_hours": 1,
    "program": "Computer Science",
    "semester": 3,
    "section": "A",
    "duration_slots": 4,
    "room_type": "Lecture Hall",
    "allowed_days": [0, 1, 2, 3, 4],
    "allowed_start_slots": [1, 3, 5, 7],
    "faculty_pool": [2]
  }
]
```

---

## 🏢 **Resources (Rooms) JSON Format**

### **Structure:**
```json
[
  {
    "id": number,              // Unique room ID (e.g., 1)
    "name": "string",          // Room name (e.g., "Lecture Hall A")
    "capacity": number,        // Room capacity (e.g., 100)
    "type": "string",          // Room type (e.g., "Lecture Hall")
    "availability": [array]    // Array of availability time windows
  }
]
```

### **Example Resources JSON:**
```json
[
  {
    "id": 1,
    "name": "Lecture Hall A",
    "capacity": 100,
    "type": "Lecture Hall",
    "availability": ["Mon:1-16", "Tue:1-16", "Wed:1-16", "Thu:1-16", "Fri:1-16"]
  },
  {
    "id": 2,
    "name": "Computer Lab 1",
    "capacity": 30,
    "type": "Computer Lab",
    "availability": ["Mon:1-16", "Tue:1-16", "Wed:1-16", "Thu:1-16", "Fri:1-16"]
  },
  {
    "id": 3,
    "name": "Physics Lab",
    "capacity": 25,
    "type": "Physics Lab",
    "availability": ["Mon:1-16", "Tue:1-16", "Wed:1-16", "Thu:1-16", "Fri:1-16"]
  }
]
```

---

## 🔧 **Field Explanations**

### **Courses Fields:**

| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| `code` | String | Unique course identifier | "CS301", "MATH201" |
| `name` | String | Full course name | "Data Structures", "Calculus III" |
| `type` | String | NEP-2020 course category | "Major", "Minor", "Skill", "Value-Added" |
| `credits` | Number | Credit hours for the course | 2, 3, 4, 6 |
| `T_hours` | Number | Theory hours per week | 2, 3, 4 |
| `P_hours` | Number | Practical/Lab hours per week | 0, 1, 2, 3 |
| `program` | String | Academic program | "Computer Science", "Electronics" |
| `semester` | Number | Recommended semester | 1, 2, 3, 4, 5, 6, 7, 8 |
| `section` | String | Course section | "A", "B", "C" |
| `duration_slots` | Number | Duration in 30-minute slots | 2, 4, 6, 8 |
| `room_type` | String | Required room type | "Lecture Hall", "Computer Lab", "Physics Lab" |
| `allowed_days` | Array | Days when course can be scheduled | [0, 1, 2, 3, 4] (Mon-Fri) |
| `allowed_start_slots` | Array | Valid start time slots | [1, 3, 5, 7, 9] |
| `faculty_pool` | Array | IDs of faculty who can teach | [1, 2, 5] |

### **Resources Fields:**

| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| `id` | Number | Unique room identifier | 1, 2, 3, 4 |
| `name` | String | Room name or number | "Lecture Hall A", "Lab 101" |
| `capacity` | Number | Maximum occupancy | 20, 30, 50, 100 |
| `type` | String | Room category | "Lecture Hall", "Computer Lab", "Physics Lab", "Classroom" |
| `availability` | Array | Time windows when room is available | ["Mon:1-16", "Tue:1-16"] |

---

## 📅 **Time Format Reference**

### **Day Indices:**
- `0` = Monday
- `1` = Tuesday
- `2` = Wednesday
- `3` = Thursday
- `4` = Friday

### **Time Slots:**
- Each slot = 30 minutes
- Slot 1 = 8:00 AM
- Slot 2 = 8:30 AM
- Slot 3 = 9:00 AM
- ...
- Slot 16 = 3:30 PM

### **Availability Format:**
- Format: `"Day:StartSlot-EndSlot"`
- Example: `"Mon:1-16"` = Monday 8:00 AM to 4:00 PM
- Example: `"Tue:3-10"` = Tuesday 9:00 AM to 1:00 PM

---

## 📝 **Usage Tips**

1. **Array Fields**: Always use square brackets `[]` for arrays
2. **String Fields**: Always use double quotes `""`
3. **Number Fields**: No quotes needed for numbers
4. **Faculty Pool**: Use actual faculty IDs from your faculty data
5. **Room Types**: Must match exactly with available room types
6. **Validation**: The system validates all fields when uploading

---

## 🚀 **How to Use**

1. **Create your JSON file** following the format above
2. **Save with .json extension** (e.g., `my_courses.json`)
3. **Upload in Vicharak** using the "Load CSV/JSON" button
4. **Verify data** appears correctly in the table
5. **Generate timetable** using the loaded data

The system supports both CSV and JSON formats, so choose whichever is more convenient for your data management workflow.
