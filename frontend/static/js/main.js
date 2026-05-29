function getEmpId() {
  return parseInt(sessionStorage.getItem("emp_id") || "0", 10);
}
function getFullName() {
  return sessionStorage.getItem("full_name") || "";
}
function getStaffRole() {
  return sessionStorage.getItem("staff_role") || "";
}
function requireAuth(redirect = "login.html") {
  if (!getEmpId()) window.location.href = redirect;
}
function requireStaff(redirect = "login_staff.html") {
  if (!getStaffRole()) window.location.href = redirect;
}