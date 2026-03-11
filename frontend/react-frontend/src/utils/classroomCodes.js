/**
 * Skeleton storage for classroom join codes (frontend-only).
 * Uses localStorage so teacher-generated codes can be validated by student in the same browser.
 * Replace with API calls when backend is ready.
 */

const STORAGE_KEY = "mamh_classroom_join_codes";

const CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // no 0/O, 1/I to avoid confusion

function randomCode(length = 6) {
  let code = "";
  for (let i = 0; i < length; i++) {
    code += CHARS[Math.floor(Math.random() * CHARS.length)];
  }
  return code;
}

/** Get all active codes from storage. Shape: { [code]: { classroomId, classroomName } } */
export function getJoinCodes() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

/** Save codes to storage. */
function setJoinCodes(codes) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(codes));
}

/** Teacher: generate a new code for a classroom and store it. Returns the code. */
export function generateJoinCode(classroomId, classroomName) {
  const codes = getJoinCodes();
  let code = randomCode(6);
  while (codes[code]) code = randomCode(6);
  codes[code] = { classroomId, classroomName };
  setJoinCodes(codes);
  return code;
}

/** Student: validate code and return classroom info if valid, else null. */
export function validateJoinCode(enteredCode) {
  const trimmed = (enteredCode || "").trim().toUpperCase();
  if (!trimmed) return null;
  const codes = getJoinCodes();
  return codes[trimmed] || null;
}
