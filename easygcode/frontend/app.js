const form = document.querySelector("#design-form");
const templateSelect = document.querySelector("#template");
const printerSelect = document.querySelector("#printer");
const statusEl = document.querySelector("#status");
const summaryEl = document.querySelector("#summary");
const artifactEl = document.querySelector("#artifact");
const warningsEl = document.querySelector("#warnings");
const downloadButton = document.querySelector("#download");
let latestArtifact = null;
const statusEl = document.querySelector("#status");
const summaryEl = document.querySelector("#summary");
const gcodeEl = document.querySelector("#gcode");
const downloadButton = document.querySelector("#download");
let latestGcode = "";

async function loadTemplates() {
  const response = await fetch("/api/templates");
  const templates = await response.json();
  templateSelect.innerHTML = templates
    .map((template) => `<option value="${template.id}">${template.label} — ${template.description}</option>`)
    .join("");
}

async function loadPrinters() {
  const response = await fetch("/api/printers");
  const printers = await response.json();
  printerSelect.innerHTML = printers
    .map((printer) => `<option value="${printer.id}">${printer.label}</option>`)
    .join("");
}

function formPayload() {
  const data = new FormData(form);
  const design = {};
  for (const key of ["template", "width", "depth", "height", "spacing", "feedrate", "travel_feedrate"]) {
    const value = data.get(key);
    design[key] = ["width", "depth", "height", "spacing"].includes(key)
      ? Number.parseFloat(value)
      : ["feedrate", "travel_feedrate"].includes(key)
        ? Number.parseInt(value, 10)
        : value;
  }
  design.printer_name = data.get("printer_id");
  return {
    mode: data.get("mode"),
    printer_id: data.get("printer_id"),
    material: data.get("material"),
    nozzle_diameter: Number.parseFloat(data.get("nozzle_diameter")),
    bed_type: data.get("bed_type"),
    design,
  };
}

function artifactBytes(artifact) {
  if (artifact.encoding === "base64") {
    const binary = atob(artifact.content);
    return Uint8Array.from(binary, (char) => char.charCodeAt(0));
  }
  return artifact.content;
function formPayload() {
  const data = new FormData(form);
  return Object.fromEntries([...data.entries()].map(([key, value]) => {
    if (["width", "depth", "height", "spacing"].includes(key)) return [key, Number.parseFloat(value)];
    if (["feedrate", "travel_feedrate"].includes(key)) return [key, Number.parseInt(value, 10)];
    return [key, value];
  }));
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  statusEl.textContent = "Preparing…";
  downloadButton.disabled = true;
  warningsEl.innerHTML = "";

  const response = await fetch("/api/print-jobs/prepare", {
  statusEl.textContent = "Generating…";
  downloadButton.disabled = true;

  const response = await fetch("/api/gcode", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formPayload()),
  });
  const payload = await response.json();

  if (!response.ok) {
    statusEl.textContent = payload.error || "Unable to prepare print artifact.";
    return;
  }

  latestArtifact = payload;
  artifactEl.textContent = payload.encoding === "base64"
    ? "Binary .gcode.3mf package prepared. Download and inspect before direct printing."
    : payload.content;
  warningsEl.innerHTML = "";
  for (const warning of payload.warnings) {
    const item = document.createElement("li");
    item.textContent = warning;
    warningsEl.appendChild(item);
  }
  summaryEl.textContent = `${payload.filename} · ${payload.status}`;
  if (payload.summary.cli_hint) {
    artifactEl.textContent += `\n\nBambu Studio CLI hint:\n${payload.summary.cli_hint}`;
  }
  statusEl.textContent = "Ready to review and download.";
    statusEl.textContent = payload.error || "Unable to generate G-code.";
    return;
  }

  latestGcode = payload.gcode;
  gcodeEl.textContent = latestGcode;
  const bounds = payload.estimated_bounds;
  summaryEl.textContent = `${payload.point_count} points · X ${bounds.min_x.toFixed(1)}–${bounds.max_x.toFixed(1)} mm · Y ${bounds.min_y.toFixed(1)}–${bounds.max_y.toFixed(1)} mm`;
  statusEl.textContent = "Ready to copy or download.";
  downloadButton.disabled = false;
});

downloadButton.addEventListener("click", () => {
  if (!latestArtifact) return;
  const blob = new Blob([artifactBytes(latestArtifact)], { type: latestArtifact.mime_type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = latestArtifact.filename;
  const blob = new Blob([latestGcode], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "easygcode-output.gcode";
  link.click();
  URL.revokeObjectURL(url);
});

Promise.all([loadTemplates(), loadPrinters()]).catch(() => {
  statusEl.textContent = "Could not load templates or printers. Is the local server running?";
loadTemplates().catch(() => {
  statusEl.textContent = "Could not load templates. Is the local server running?";
});
