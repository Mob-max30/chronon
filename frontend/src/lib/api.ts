const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

// =============================================================================
// HEALTH CHECK
// =============================================================================
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

// =============================================================================
// ACADEMIC YEARS & CURRICULUM (UJWAL & PRANAV)
// =============================================================================
export async function getAcademicYears() {
  try {
    const res = await fetch(`${API_BASE}/academic-years`);
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

export async function getCurrentAcademicYear() {
  try {
    const res = await fetch(`${API_BASE}/academic-years/current`);
    const json = await res.json();
    return json.data || null;
  } catch {
    return null;
  }
}

export async function setCurrentAcademicYear(yearId: number) {
  const res = await fetch(`${API_BASE}/academic-years/${yearId}/set-current`, {
    method: "POST",
  });
  return res.json();
}

export async function getHistoricalAcademicYears() {
  try {
    const res = await fetch(`${API_BASE}/academic-years/historical`);
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

export async function createAcademicYear(nameOrPayload: any, isCurrent: boolean = false) {
  const payload = typeof nameOrPayload === "string" 
    ? { name: nameOrPayload, is_current: isCurrent } 
    : nameOrPayload;
  const res = await fetch(`${API_BASE}/academic-years`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function validateSemester(payload: any) {
  const res = await fetch(`${API_BASE}/academic-years/validate-semester`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function fetchBranches() {
  try {
    const res = await fetch(`${API_BASE}/branches`);
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

export async function fetchStreams() {
  try {
    const res = await fetch(`${API_BASE}/branches/streams`);
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

export async function fetchSubjects(semesterId?: number) {
  try {
    const url = semesterId ? `${API_BASE}/subjects?semester_id=${semesterId}` : `${API_BASE}/subjects`;
    const res = await fetch(url);
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

export async function fetchFaculty() {
  try {
    const res = await fetch(`${API_BASE}/faculty`);
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

// =============================================================================
// GENERATION ORCHESTRATION & LIFECYCLE (PRANAV)
// =============================================================================
export async function triggerGenerationRun(payload: any) {
  const res = await fetch(`${API_BASE}/generation/trigger`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function getGenerationRunStatus(runId: number) {
  try {
    const res = await fetch(`${API_BASE}/generation/runs/${runId}`);
    const json = await res.json();
    return json.data || null;
  } catch {
    return null;
  }
}

export async function cancelGenerationRun(runId: number) {
  const res = await fetch(`${API_BASE}/generation/runs/${runId}/cancel`, {
    method: "POST",
  });
  return res.json();
}

// =============================================================================
// VERSIONING & COMPARISON (PRANAV)
// =============================================================================
export async function getTimetableVersions(timetableId: number) {
  try {
    const res = await fetch(`${API_BASE}/versions/${timetableId}`);
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

export async function getVersionDetail(timetableId: number, versionId: number) {
  try {
    const res = await fetch(`${API_BASE}/versions/${timetableId}/${versionId}`);
    const json = await res.json();
    return json.data || null;
  } catch {
    return null;
  }
}

export async function setActiveVersion(timetableId: number, versionId: number) {
  const res = await fetch(`${API_BASE}/versions/${timetableId}/activate/${versionId}`, {
    method: "POST",
  });
  return res.json();
}

export async function compareVersions(timetableId: number, v1Id: number, v2Id: number) {
  try {
    const res = await fetch(`${API_BASE}/versions/${timetableId}/compare?v1_id=${v1Id}&v2_id=${v2Id}`);
    const json = await res.json();
    return json.data || null;
  } catch {
    return null;
  }
}

// =============================================================================
// PHYSICAL RESOURCES & DETERMINISTIC MATH (NIVISH)
// =============================================================================
export async function getRooms() {
  try {
    const res = await fetch(`${API_BASE}/resources/rooms`);
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

export async function createRoom(payload: any) {
  const res = await fetch(`${API_BASE}/resources/rooms`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function updateRoom(roomId: number, payload: any) {
  const res = await fetch(`${API_BASE}/resources/rooms/${roomId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function deleteRoom(roomId: number) {
  const res = await fetch(`${API_BASE}/resources/rooms/${roomId}`, {
    method: "DELETE",
  });
  return res.json();
}

export async function getLabs() {
  try {
    const res = await fetch(`${API_BASE}/resources/labs`);
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

export async function createLab(payload: any) {
  const res = await fetch(`${API_BASE}/resources/labs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function updateLab(labId: number, payload: any) {
  const res = await fetch(`${API_BASE}/resources/labs/${labId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function deleteLab(labId: number) {
  const res = await fetch(`${API_BASE}/resources/labs/${labId}`, {
    method: "DELETE",
  });
  return res.json();
}

export async function getLabMappings() {
  try {
    const res = await fetch(`${API_BASE}/resources/labs/mappings`);
    const json = await res.json();
    return json.data || [];
  } catch {
    return [];
  }
}

export async function createLabMapping(payload: any) {
  const res = await fetch(`${API_BASE}/resources/labs/mappings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function deleteLabMapping(mappingId: number) {
  const res = await fetch(`${API_BASE}/resources/labs/mappings/${mappingId}`, {
    method: "DELETE",
  });
  return res.json();
}

export async function calculateSectionsAPI(payload: any) {
  const res = await fetch(`${API_BASE}/resources/sections/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function createSection(payload: any) {
  const res = await fetch(`${API_BASE}/resources/sections`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function createBatch(payload: any) {
  const res = await fetch(`${API_BASE}/resources/batches`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function calculateBatchesAPI(payload: any) {
  const res = await fetch(`${API_BASE}/resources/batches/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function getSlotConfig() {
  try {
    const res = await fetch(`${API_BASE}/resources/slot-config`);
    const json = await res.json();
    return json.data || null;
  } catch {
    return null;
  }
}

export async function saveSlotConfig(payload: any) {
  const res = await fetch(`${API_BASE}/resources/slot-config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function generateTimeSlotsAPI(payload: any) {
  const res = await fetch(`${API_BASE}/resources/time-slots/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

// =============================================================================
// TIMETABLE MATRIX & EXPORT (NIVISH)
// =============================================================================
export async function getTimetableMatrix(
  timetableId: number = 1,
  viewTypeOrFilters: string | Record<string, any> = "SECTION",
  filters: Record<string, any> = {}
) {
  let viewType = "SECTION";
  let activeFilters: Record<string, any> = {};

  if (typeof viewTypeOrFilters === "string") {
    viewType = viewTypeOrFilters;
    activeFilters = filters;
  } else if (typeof viewTypeOrFilters === "object" && viewTypeOrFilters !== null) {
    viewType = viewTypeOrFilters.view_type || "SECTION";
    activeFilters = viewTypeOrFilters;
  }

  const params = new URLSearchParams({ view_type: viewType });
  Object.entries(activeFilters).forEach(([k, v]) => {
    if (k !== "view_type" && v !== undefined && v !== null && v !== "") {
      params.append(k, String(v));
    }
  });

  const res = await fetch(`${API_BASE}/timetables/${timetableId}/view?${params.toString()}`);
  const json = await res.json();
  return json.data || null;
}

export async function exportTimetableCSV(
  timetableId: number = 1,
  viewType: string = "SECTION",
  filters: Record<string, any> = {}
) {
  const params = new URLSearchParams({ export_format: "csv", view_type: viewType });
  Object.entries(filters).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") {
      params.append(k, String(v));
    }
  });

  const res = await fetch(`${API_BASE}/timetables/${timetableId}/export?${params.toString()}`);
  return await res.text();
}
