export const exportToCsv = (profiles, baseFileName = "export") => {
  if (!profiles || profiles.length === 0) {
    if (typeof alert !== 'undefined') alert("No data available to export.");
    console.warn("exportToCsv called with no data.");
    return;
  }

  const headers = [
    "Full Name",
    "Email",
    "Phone Number",
    "Company Name",
    "Customer Name",
    "Role",
    "Duration",
    "Skills/Technologies",
    "Industry/Domain",
    "Location"
  ];

  const escapeCsv = (field) =>
    `"${String(field ?? "N/A").replace(/"/g, '""')}"`;

  const rows = [];

  profiles.forEach(resume => {
    if (resume.work_experience && resume.work_experience.length > 0) {
      resume.work_experience.forEach(entry => {
        const skillsString = Array.isArray(entry.skills_technologies)
          ? entry.skills_technologies.join('; ')
          : (entry.skills_technologies || "N/A");

        rows.push([
          resume.full_name || "N/A",
          resume.email || "N/A",
          resume.phone_number || "N/A",
          entry.company_name || "N/A",
          entry.customer_name || "N/A",
          entry.role || "N/A",
          entry.duration || "N/A",
          skillsString,
          entry.industry_domain || "N/A",
          entry.location || "N/A"
        ].map(escapeCsv));
      });
    } else {
      rows.push([
        resume.full_name || "N/A",
        resume.email || "N/A",
        resume.phone_number || "N/A",
        "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
      ].map(escapeCsv));
    }
  });

  let csvContent = headers.map(escapeCsv).join(",") + "\n";
  csvContent += rows.map(row => row.join(",")).join("\n");

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", `${baseFileName}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};