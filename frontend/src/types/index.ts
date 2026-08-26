export type AcademicYear = {
  id: number;
  name: string;
  is_current: boolean;
};

export type TimetableSession = {
  id?: number;
  version_id: number;
  subject_id: number;
  faculty_id: number;
  section_id: number;
  batch_id?: number | null;
  room_id?: number | null;
  lab_id?: number | null;
  time_slot_id: number;
};

export type SystemHealth = {
  status: string;
  service: string;
};
