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
