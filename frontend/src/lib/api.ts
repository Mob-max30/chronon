const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export async function checkBackendHealth(): Promise<{ status: string; service?: string }> {
  try {
    const res = await fetch(`${API_BASE}/health`, {
      method: "GET",
      cache: "no-store",
    });
    if (!res.ok) {
      return { status: "error", service: "backend" };
    }
    const json = await res.json();
    return json.data || { status: "ok", service: "chronon-api" };
  } catch {
    return { status: "offline", service: "chronon-api" };
  }
}

// ==============================================================================
// ACADEMIC YEARS & LIFECYCLE (PRANAV)
// ==============================================================================

export async function getAcademicYears() {
  const res = await fetch(`${API_BASE}/academic-years`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch academic years");
  const json = await res.json();
  return json.data || [];
}

export async function getCurrentAcademicYear() {
  const res = await fetch(`${API_BASE}/academic-years/current`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch current academic year");
  const json = await res.json();
  return json.data;
}
export const fetchCurrentAcademicYear = getCurrentAcademicYear;

export async function getHistoricalAcademicYears() {
  const res = await fetch(`${API_BASE}/academic-years/historical`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch historical academic years");
  const json = await res.json();
  return json.data || [];
}
export const fetchHistoricalAcademicYears = getHistoricalAcademicYears;

export async function createAcademicYear(data: { name: string; is_current?: boolean; start_date?: string; end_date?: string }) {
  const res = await fetch(`${API_BASE}/academic-years`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create academic year");
  const json = await res.json();
  return json.data;
}

export async function setCurrentAcademicYear(yearId: number) {
  const res = await fetch(`${API_BASE}/academic-years/${yearId}/set-current`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to set current academic year");
  const json = await res.json();
  return json.data;
}

export async function validateSemesterSelection(data: {
  academic_year_id: number;
  institution_type: string;
  year_level: number;
  term_type: string;
  semester_number: number;
  is_first_year_joint?: boolean;
}) {
  const res = await fetch(`${API_BASE}/academic-years/validate-semester`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Semester validation failed");
  const json = await res.json();
  return json.data;
}

// ==============================================================================
// CURRICULUM, OCR & INGESTION (UJWAL)
// ==============================================================================

export async function fetchBranches() {
  try {
    const res = await fetch(`${API_BASE}/branches`, { cache: "no-store" });
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

export async function fetchStreams() {
  try {
    const res = await fetch(`${API_BASE}/branches/streams`, { cache: "no-store" });
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

export async function fetchSubjects(semesterId?: number) {
  try {
    const url = semesterId ? `${API_BASE}/subjects?semester_id=${semesterId}` : `${API_BASE}/subjects`;
    const res = await fetch(url, { cache: "no-store" });
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

export async function fetchFaculty() {
  try {
    const res = await fetch(`${API_BASE}/faculty`, { cache: "no-store" });
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

// ==============================================================================
// GENERATION & ORCHESTRATION (PRANAV / PRUTHVIK)
// ==============================================================================

export async function triggerGeneration(data: {
  timetable_id: number;
  academic_year_id?: number;
  semester_ids?: number[];
  is_joint_first_year?: boolean;
  max_solver_time_seconds?: number;
  notes?: string;
}) {
  const res = await fetch(`${API_BASE}/generation/trigger`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to trigger generation run");
  const json = await res.json();
  return json.data;
}
export const triggerGenerationRun = triggerGeneration;

export async function getGenerationRunStatus(runId: number) {
  const res = await fetch(`${API_BASE}/generation/runs/${runId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch run status");
  const json = await res.json();
  return json.data;
}

export async function cancelGenerationRun(runId: number) {
  const res = await fetch(`${API_BASE}/generation/runs/${runId}/cancel`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to cancel run");
  const json = await res.json();
  return json.data;
}

// ==============================================================================
// VERSIONS & HISTORICAL DIFFS (PRANAV)
// ==============================================================================

export async function getTimetableVersions(timetableId: number) {
  const res = await fetch(`${API_BASE}/versions/${timetableId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch timetable versions");
  const json = await res.json();
  return json.data || [];
}
export const fetchTimetableVersions = getTimetableVersions;

export async function getVersionDetail(timetableId: number, versionId: number) {
  const res = await fetch(`${API_BASE}/versions/${timetableId}/version/${versionId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch version details");
  const json = await res.json();
  return json.data;
}

export async function setActiveVersion(timetableId: number, versionId: number) {
  const res = await fetch(`${API_BASE}/versions/${timetableId}/version/${versionId}/set-active`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to set active version");
  const json = await res.json();
  return json.data;
}

export async function compareVersions(timetableId: number, fromVersionId: number, toVersionId: number) {
  const res = await fetch(
    `${API_BASE}/versions/${timetableId}/diff?from_version_id=${fromVersionId}&to_version_id=${toVersionId}`,
    { cache: "no-store" }
  );
  if (!res.ok) throw new Error("Failed to fetch version diff");
  const json = await res.json();
  return json.data;
}
export const fetchVersionDiff = compareVersions;

// ==============================================================================
// RESOURCES & DETERMINISTIC MATH (NIVISH)
// ==============================================================================

export async function calculateSectionsAPI(payload: {
  student_count: number;
  room_capacity: number;
  naming_pattern?: string | null;
  manual_count?: number | null;
  stream_id?: number | null;
  cycle_group?: string | null;
  balance_distribution?: boolean;
}) {
  const res = await fetch(`${API_BASE}/resources/sections/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to calculate sections");
  const json = await res.json();
  return json.data;
}

export async function calculateBatchesAPI(payload: {
  section_students: number;
  lab_capacity: number;
  naming_pattern?: string | null;
  manual_count?: number | null;
  prefix?: string;
  balance_distribution?: boolean;
}) {
  const res = await fetch(`${API_BASE}/resources/batches/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to calculate batches");
  const json = await res.json();
  return json.data;
}

export async function getRooms() {
  const res = await fetch(`${API_BASE}/resources/rooms`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch rooms");
  const json = await res.json();
  return json.data || [];
}

export async function createRoom(payload: { name: string; code?: string; capacity: number; institution_id?: number; room_type?: string; building?: string; floor?: number; is_active?: boolean; [key: string]: any }) {
  const res = await fetch(`${API_BASE}/resources/rooms`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...payload, code: payload.code || payload.name.replace(/\s+/g, "_").toUpperCase() }),
  });
  if (!res.ok) throw new Error("Failed to create room");
  const json = await res.json();
  return json.data;
}

export async function updateRoom(roomId: number, payload: any) {
  const res = await fetch(`${API_BASE}/resources/rooms/${roomId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to update room");
  const json = await res.json();
  return json.data;
}

export async function deleteRoom(roomId: number) {
  const res = await fetch(`${API_BASE}/resources/rooms/${roomId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete room");
  const json = await res.json();
  return json.data;
}

export async function getLabs() {
  const res = await fetch(`${API_BASE}/resources/labs`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch labs");
  const json = await res.json();
  return json.data || [];
}

export async function createLab(payload: { name: string; code?: string; capacity: number; institution_id?: number; count?: number; building?: string; floor?: number; lab_type?: string; is_active?: boolean; [key: string]: any }) {
  const res = await fetch(`${API_BASE}/resources/labs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...payload, code: payload.code || payload.name.replace(/\s+/g, "_").toUpperCase() }),
  });
  if (!res.ok) throw new Error("Failed to create lab");
  const json = await res.json();
  return json.data;
}

export async function updateLab(labId: number, payload: any) {
  const res = await fetch(`${API_BASE}/resources/labs/${labId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to update lab");
  const json = await res.json();
  return json.data;
}

export async function deleteLab(labId: number) {
  const res = await fetch(`${API_BASE}/resources/labs/${labId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete lab");
  const json = await res.json();
  return json.data;
}

export async function getLabMappings() {
  const res = await fetch(`${API_BASE}/resources/lab-mappings`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch lab mappings");
  const json = await res.json();
  return json.data || [];
}

export async function createLabMapping(payload: { subject_id: number; lab_id: number; is_mandatory?: boolean; priority?: number }) {
  const res = await fetch(`${API_BASE}/resources/lab-mappings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to create lab mapping");
  const json = await res.json();
  return json.data;
}

export async function deleteLabMapping(mappingId: number) {
  const res = await fetch(`${API_BASE}/resources/lab-mappings/${mappingId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete lab mapping");
  const json = await res.json();
  return json.data;
}

export async function getSlotConfig() {
  const res = await fetch(`${API_BASE}/resources/slot-configs/current`, { cache: "no-store" });
  if (!res.ok) return null;
  const json = await res.json();
  return json.data;
}

export async function saveSlotConfig(payload: any) {
  const res = await fetch(`${API_BASE}/resources/slot-configs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to save slot config");
  const json = await res.json();
  return json.data;
}

export async function generateTimeSlotsAPI(payload: any) {
  const res = await fetch(`${API_BASE}/resources/time-slots/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to generate time slots");
  const json = await res.json();
  return json.data;
}

// ==============================================================================
// TIMETABLE MATRIX & VIEWS (NIVISH)
// ==============================================================================

export async function getTimetableMatrix(
  timetableId: number,
  params: {
    view_type?: string;
    version_id?: number | null;
    section_id?: number | null;
    faculty_id?: number | null;
    room_id?: number | null;
    lab_id?: number | null;
    batch_id?: number | null;
    stream_id?: number | null;
    cycle_group?: string | null;
    [key: string]: any;
  } = {}
) {
  const query = new URLSearchParams();
  if (params.view_type) query.set("view_type", params.view_type);
  if (params.version_id) query.set("version_id", params.version_id.toString());
  if (params.section_id) query.set("section_id", params.section_id.toString());
  if (params.faculty_id) query.set("faculty_id", params.faculty_id.toString());
  if (params.room_id) query.set("room_id", params.room_id.toString());
  if (params.lab_id) query.set("lab_id", params.lab_id.toString());
  if (params.cycle_group) query.set("cycle_group", params.cycle_group);
  if (params.stream_id) query.set("stream_id", params.stream_id.toString());
  if (params.batch_id) query.set("batch_id", params.batch_id.toString());

  const res = await fetch(`${API_BASE}/timetables/${timetableId}/view?${query.toString()}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch timetable matrix");
  const json = await res.json();
  return json.data;
}
