import { useEffect, useState } from "react";
import { useAuth } from "../../auth/UseAuth";
import { apiFetch } from "../../api/client";

export default function AdminOverview() {
  const { token, user } = useAuth();
  const isSuperAdmin = user?.role === "super_admin";

  const [schools, setSchools] = useState([]);
  const [schoolsLoading, setSchoolsLoading] = useState(false);
  const [schoolError, setSchoolError] = useState("");
  const [newSchoolName, setNewSchoolName] = useState("");
  const [creatingSchool, setCreatingSchool] = useState(false);
  const [selectedSchoolId, setSelectedSchoolId] = useState(user?.school_id ? String(user.school_id) : "");

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [role, setRole] = useState("teacher");
  const [password, setPassword] = useState("");
  const [lastPassword, setLastPassword] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [search, setSearch] = useState("");
  const [filterRole, setFilterRole] = useState("");
  const [users, setUsers] = useState([]);
  const [listError, setListError] = useState("");
  const [listLoading, setListLoading] = useState(false);
  const [deleteLoadingId, setDeleteLoadingId] = useState(null);

  useEffect(() => {
    if (!user?.school_id && !isSuperAdmin) {
      setSelectedSchoolId("");
      return;
    }
    if (!selectedSchoolId && user?.school_id && !isSuperAdmin) {
      setSelectedSchoolId(String(user.school_id));
    }
  }, [isSuperAdmin, selectedSchoolId, user?.school_id]);

  async function loadSchools() {
    setSchoolError("");
    setSchoolsLoading(true);
    try {
      const data = await apiFetch("/admin/schools", {
        method: "GET",
        token,
      });
      const nextSchools = Array.isArray(data) ? data : [];
      setSchools(nextSchools);
      if (isSuperAdmin && !selectedSchoolId && nextSchools.length > 0) {
        setSelectedSchoolId(String(nextSchools[0].id));
      }
    } catch (err) {
      setSchoolError(err.message || "Failed to load schools.");
    } finally {
      setSchoolsLoading(false);
    }
  }

  async function loadUsers() {
    if (isSuperAdmin && !selectedSchoolId) {
      setUsers([]);
      setListError("Select a school first.");
      return;
    }

    setListError("");
    setListLoading(true);
    try {
      const params = new URLSearchParams();
      if (search.trim()) params.set("q", search.trim());
      if (filterRole) params.set("role", filterRole);
      if (selectedSchoolId) params.set("school_id", selectedSchoolId);
      const query = params.toString();
      const data = await apiFetch(`/admin/users${query ? `?${query}` : ""}`, {
        method: "GET",
        token,
      });
      setUsers(Array.isArray(data) ? data : []);
    } catch (err) {
      setListError(err.message || "Failed to load users.");
    } finally {
      setListLoading(false);
    }
  }

  async function handleCreateSchool(e) {
    e.preventDefault();
    setSchoolError("");
    setCreatingSchool(true);
    try {
      const created = await apiFetch("/admin/schools", {
        method: "POST",
        token,
        body: JSON.stringify({ name: newSchoolName }),
      });
      setNewSchoolName("");
      await loadSchools();
      setSelectedSchoolId(String(created.id));
    } catch (err) {
      setSchoolError(err.message || "Failed to create school.");
    } finally {
      setCreatingSchool(false);
    }
  }

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    setResult(null);

    if (isSuperAdmin && !selectedSchoolId) {
      setError("Select a school before creating users.");
      return;
    }

    setLoading(true);
    try {
      const data = await apiFetch("/admin/users", {
        method: "POST",
        token,
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          role,
          password,
          school_id: selectedSchoolId ? Number(selectedSchoolId) : null,
        }),
      });
      setResult(data);
      setLastPassword(password);
      await loadUsers();
      setFirstName("");
      setLastName("");
      setPassword("");
      if (!isSuperAdmin) {
        setRole("teacher");
      }
    } catch (err) {
      setError(err.message || "Failed to create user.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDeleteUser(userId) {
    setListError("");
    setDeleteLoadingId(userId);
    try {
      await apiFetch(`/admin/users/${userId}`, {
        method: "DELETE",
        token,
      });
      await loadUsers();
    } catch (err) {
      setListError(err.message || "Failed to delete user.");
    } finally {
      setDeleteLoadingId(null);
    }
  }

  async function handleCopyCredentials() {
    if (!result?.email || !lastPassword) return;
    const text = `Email: ${result.email}\nPassword: ${lastPassword}`;
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // Ignore clipboard failures.
    }
  }

  useEffect(() => {
    loadSchools();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (selectedSchoolId || !isSuperAdmin) {
      loadUsers();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSchoolId]);

  const currentSchoolName =
    schools.find((school) => String(school.id) === selectedSchoolId)?.name || "No school selected";

  const roleOptions = isSuperAdmin
    ? [
        { value: "teacher", label: "Teacher" },
        { value: "student", label: "Student" },
        { value: "admin", label: "School Admin" },
      ]
    : [
        { value: "teacher", label: "Teacher" },
        { value: "student", label: "Student" },
      ];

  return (
    <div className="max-w-6xl flex flex-col gap-8">
      <div>
        <h2 className="text-2xl font-bold">{isSuperAdmin ? "School Management" : "School Dashboard"}</h2>
        <p className="text-sm text-gray-600">
          {isSuperAdmin
            ? "Create schools, assign school admins, and manage users inside each school."
            : "Create and manage teachers and students inside your assigned school."}
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border p-5 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold">School Scope</h3>
            <button
              type="button"
              onClick={loadSchools}
              className="rounded-lg px-3 py-2 text-sm font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
            >
              {schoolsLoading ? "Loading..." : "Refresh"}
            </button>
          </div>

          {schoolError ? (
            <div className="w-full p-3 rounded-xl border border-red-300 bg-red-50 text-red-700 text-sm">
              {schoolError}
            </div>
          ) : null}

          {isSuperAdmin ? (
            <>
              <form onSubmit={handleCreateSchool} className="flex flex-col gap-3">
                <input
                  type="text"
                  placeholder="New school name"
                  value={newSchoolName}
                  onChange={(e) => setNewSchoolName(e.target.value)}
                  required
                  className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="submit"
                  disabled={creatingSchool}
                  className="w-full rounded-xl px-4 py-3 text-sm font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition disabled:opacity-60"
                >
                  {creatingSchool ? "Creating..." : "Create School"}
                </button>
              </form>

              <select
                value={selectedSchoolId}
                onChange={(e) => setSelectedSchoolId(e.target.value)}
                className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              >
                <option value="">Select a school</option>
                {schools.map((school) => (
                  <option key={school.id} value={school.id}>
                    {school.name}
                  </option>
                ))}
              </select>
            </>
          ) : (
            <div className="rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
              Current school: <span className="font-semibold">{currentSchoolName}</span>
            </div>
          )}
        </div>

        <div className="rounded-2xl border p-5 flex flex-col gap-4">
          <div>
            <h3 className="text-xl font-bold">Create User</h3>
            <p className="text-sm text-gray-600">
              {isSuperAdmin
                ? "Select a school, then create teachers, students, or that school's admin."
                : "Create teachers and students for your school."}
            </p>
          </div>

          {error ? (
            <div className="w-full p-3 rounded-xl border border-red-300 bg-red-50 text-red-700 text-sm">
              {error}
            </div>
          ) : null}

          {result ? (
            <div className="w-full p-3 rounded-xl border border-green-300 bg-green-50 text-green-800 text-sm">
              <div>
                Created: <span className="font-semibold">{result.email}</span> ({result.role})
              </div>
              <div className="mt-1">
                School: <span className="font-semibold">{result.school_name || "None"}</span>
              </div>
              <div className="mt-2 text-xs">
                Password set to: <span className="font-semibold">{lastPassword}</span>
              </div>
              <button
                type="button"
                onClick={handleCopyCredentials}
                className="mt-2 inline-flex rounded-lg px-3 py-2 text-sm font-semibold border border-green-300 hover:bg-green-200 transition"
              >
                Copy credentials
              </button>
            </div>
          ) : null}

          <form onSubmit={handleCreate} className="flex flex-col gap-4">
            <div className="grid gap-3 sm:grid-cols-2">
              <input
                type="text"
                placeholder="First name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                required
                className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="text"
                placeholder="Last name"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                required
                className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            >
              {roleOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl px-8 py-4 text-lg font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition disabled:opacity-60"
            >
              {loading ? "Creating..." : "Create Account"}
            </button>
          </form>
        </div>
      </div>

      <div className="rounded-2xl border p-5 flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-bold">Users</h3>
          <button
            type="button"
            onClick={loadUsers}
            className="rounded-lg px-3 py-2 text-sm font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
          >
            {listLoading ? "Loading..." : "Refresh"}
          </button>
        </div>

        <div className="grid gap-3 md:grid-cols-3">
          <input
            type="text"
            placeholder="Search by email"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
            className="w-full p-3 border border-blue-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            <option value="">All roles</option>
            <option value="teacher">Teacher</option>
            <option value="student">Student</option>
            <option value="admin">Admin</option>
          </select>
          <button
            type="button"
            onClick={loadUsers}
            className="w-full rounded-xl px-4 py-3 text-sm font-semibold border border-blue-300 hover:bg-blue-500 hover:text-white transition"
          >
            Search
          </button>
        </div>

        {listError ? (
          <div className="w-full p-3 rounded-xl border border-red-300 bg-red-50 text-red-700 text-sm">
            {listError}
          </div>
        ) : null}

        <div className="rounded-2xl border overflow-hidden">
          <div className="grid grid-cols-6 bg-blue-50 text-blue-900 text-sm font-semibold px-4 py-3 gap-3">
            <div>Email</div>
            <div>Role</div>
            <div>School</div>
            <div>Admin</div>
            <div>Password Reset</div>
            <div>Action</div>
          </div>
          <div className="divide-y">
            {users.length === 0 ? (
              <div className="px-4 py-4 text-sm text-gray-600">No users found.</div>
            ) : (
              users.map((listedUser) => (
                <div key={listedUser.id} className="grid grid-cols-6 px-4 py-3 text-sm gap-3 items-center">
                  <div className="truncate">{listedUser.email}</div>
                  <div className="capitalize">{listedUser.role}</div>
                  <div className="truncate">{listedUser.school_name || "None"}</div>
                  <div>{listedUser.is_admin ? "Yes" : "No"}</div>
                  <div>{listedUser.must_change_password ? "Yes" : "No"}</div>
                  <div>
                    <button
                      type="button"
                      onClick={() => handleDeleteUser(listedUser.id)}
                      disabled={deleteLoadingId === listedUser.id}
                      className="rounded-lg px-3 py-2 text-xs font-semibold border border-red-300 text-red-700 hover:bg-red-600 hover:text-white transition disabled:opacity-60"
                    >
                      {deleteLoadingId === listedUser.id ? "Deleting..." : "Delete"}
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
