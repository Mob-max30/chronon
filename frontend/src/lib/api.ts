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

// --- Academic Years (Pranav) ---

export async function fetchCurrentAcademicYear() {
  const res = await fetch(`${API_BASE}/academic-years/current`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch current academic year");
  const json = await res.json();
  return json.data;
}

export async function fetchHistoricalAcademicYears() {
  const res = await fetch(`${API_BASE}/academic-years/historical`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch historical academic years");
  const json = await res.json();
  return json.data || [];
}

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

// --- Curriculum & Ingestion (Ujwal) ---

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

// --- Generation & Orchestration (Pranav) ---

export async function triggerGeneration(data: {
  timetable_id: number;
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

// --- Versions & Historical Diffs (Pranav) ---

export async function fetchTimetableVersions(timetableId: number) {
  const res = await fetch(`${API_BASE}/versions/${timetableId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch timetable versions");
  const json = await res.json();
  return json.data || [];
}

export async function setActiveVersion(timetableId: number, versionId: number) {
  const res = await fetch(`${API_BASE}/versions/${timetableId}/version/${versionId}/set-active`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to set active version");
  const json = await res.json();
  return json.data;
}

export async function fetchVersionDiff(timetableId: number, fromVersionId: number, toVersionId: number) {
  const res = await fetch(
    `${API_BASE}/versions/${timetableId}/diff?from_version_id=${fromVersionId}&to_version_id=${toVersionId}`,
    { cache: "no-store" }
  );
  if (!res.ok) throw new Error("Failed to fetch version diff");
  const json = await res.json();
  return json.data;
}

// --- Resources (Nivish) ---

export async function fetchRooms() {
  try {
    const res = await fetch(`${API_BASE}/resources/rooms`, { cache: "no-store" });
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

export async function fetchLabs() {
  try {
    const res = await fetch(`${API_BASE}/resources/labs`, { cache: "no-store" });
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

export async function fetchSections(semesterId?: number) {
  try {
    const url = semesterId ? `${API_BASE}/resources/sections?semester_id=${semesterId}` : `${API_BASE}/resources/sections`;
    const res = await fetch(url, { cache: "no-store" });
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

export async function fetchTimeSlots() {
  try {
    const res = await fetch(`${API_BASE}/resources/time-slots`, { cache: "no-store" });
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}
