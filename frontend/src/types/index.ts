export type AcademicYear = {
  id: number;
  name: string;
  is_current: boolean;
};

export type SystemHealth = {
  status: string;
  service: string;
};

// ==============================================================================
// PHYSICAL RESOURCES TYPES
// ==============================================================================
export type RoomAvailability = {
  id?: number;
  room_id?: number;
  day_of_week: number; // 0=Mon, 5=Sat
  start_time: string;
  end_time: string;
  is_available: boolean;
};

export type Room = {
  id: number;
  institution_id: number;
  name: string;
  building?: string | null;
  capacity: number;
  room_type: string; // LECTURE_HALL, SEMINAR_HALL, AUDITORIUM
  is_active: boolean;
  availabilities?: RoomAvailability[];
};

export type LabAvailability = {
  id?: number;
  lab_id?: number;
  day_of_week: number;
  start_time: string;
  end_time: string;
  is_available: boolean;
};

export type Lab = {
  id: number;
  institution_id: number;
  name: string;
  building?: string | null;
  capacity: number; // workstations count
  count: number; // physical lab rooms count
  lab_type: string; // COMPUTER, ELECTRONICS, MECHANICAL, CIVIL, PHYSICS, CHEMISTRY
  availabilities?: LabAvailability[];
};

export type LabSubjectMapping = {
  id: number;
  subject_id: number;
  lab_id: number;
  subject_name?: string | null;
  subject_code?: string | null;
  lab_name?: string | null;
};

// ==============================================================================
// SECTION & BATCH CALCULATION TYPES
// ==============================================================================
export type CalculatedSectionItem = {
  name: string;
  student_count: number;
  room_id?: number | null;
  stream_id?: number | null;
  cycle_group?: string | null;
};

export type SectionCalculationResult = {
  student_count: number;
  room_capacity: number;
  calculated_section_count: number;
  actual_section_count: number;
  is_override: boolean;
  sections: CalculatedSectionItem[];
};

export type Section = {
  id: number;
  branch_id: number;
  semester_id: number;
  name: string;
  student_count: number;
  room_id?: number | null;
  stream_id?: number | null;
  cycle_group?: string | null;
  is_override: boolean;
};

export type CalculatedBatchItem = {
  name: string;
  student_count: number;
  lab_id?: number | null;
};

export type BatchCalculationResult = {
  section_students: number;
  lab_capacity: number;
  calculated_batch_count: number;
  actual_batch_count: number;
  is_override: boolean;
  batches: CalculatedBatchItem[];
};

export type Batch = {
  id: number;
  section_id: number;
  name: string;
  student_count: number;
  lab_id?: number | null;
};

// ==============================================================================
// TIME SLOT & CONFIG TYPES
// ==============================================================================
export type SlotBreak = {
  name: string;
  start_time: string;
  end_time: string;
  slot_type: string;
};

export type SlotConfig = {
  id?: number;
  institution_id: number;
  name: string;
  theory_duration_minutes: number;
  lab_duration_minutes: number;
  working_days: number[];
  day_start_time: string;
  day_end_time: string;
  breaks: SlotBreak[];
  lunch_break?: SlotBreak | null;
  non_teaching_periods: SlotBreak[];
};

export type TimeSlot = {
  id: number;
  day_of_week: number;
  period_index: number;
  start_time: string;
  end_time: string;
  slot_type: string;
  label?: string | null;
};

// ==============================================================================
// TIMETABLE MATRIX GRID PRESENTATION TYPES
// ==============================================================================
export type GridCellSession = {
  session_id: number;
  subject_id: number;
  subject_code: string;
  subject_name: string;
  subject_type: string;
  faculty_id: number;
  faculty_name: string;
  section_id: number;
  section_name: string;
  batch_id?: number | null;
  batch_name?: string | null;
  room_id?: number | null;
  room_name?: string | null;
  lab_id?: number | null;
  lab_name?: string | null;
  stream_id?: number | null;
  stream_name?: string | null;
  cycle_group?: string | null;
  paired_slot_group?: string | null;
  has_conflict: boolean;
  conflict_messages: string[];
};

export type GridCell = {
  day_of_week: number;
  period_index: number;
  time_slot_id: number;
  time_slot_label: string;
  start_time: string;
  end_time: string;
  slot_type: string;
  sessions: GridCellSession[];
  has_conflict: boolean;
  conflict_details: Record<string, any>[];
};

export type GridRow = {
  day_of_week: number;
  day_name: string;
  cells: GridCell[];
};

export type PairedSlotGroupItem = {
  paired_slot_group: string;
  day_of_week: number;
  day_name: string;
  period_index: number;
  time_slot_label: string;
  sessions: GridCellSession[];
};

export type TimetableMatrixResponse = {
  timetable_id: number;
  version_id?: number | null;
  view_type: string; // SECTION, FACULTY, ROOM, LAB, BATCH, FIRST_YEAR_CYCLE
  filter_applied: Record<string, any>;
  periods_header: {
    period_index: number;
    label: string;
    start_time: string;
    end_time: string;
    slot_type: string;
  }[];
  rows: GridRow[];
  paired_slot_groups: PairedSlotGroupItem[];
  conflicts: Record<string, any>[];
  total_sessions: number;
};
