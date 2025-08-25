const form = document.getElementById('cp-form');
const result = document.getElementById('result');
const link = document.getElementById('downloadLink');
const reportEl = document.getElementById('report');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const recap = document.getElementById('recap').files[0];
  const base_cp = document.getElementById('base_cp').files[0];
  const negotiated = document.getElementById('negotiated').files[0];
  const filename = document.getElementById('filename').value || 'Final_CP.docx';

  const fd = new FormData();
  fd.append('recap', recap);
  fd.append('base_cp', base_cp);
  fd.append('negotiated', negotiated);
  fd.append('filename', filename);

  try {
    const res = await fetch('http://localhost:8000/api/generate', {
      method: 'POST',
      body: fd
    });
    if (!res.ok) {
      const t = await res.text();
      throw new Error(t || 'Failed to generate');
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    link.href = url;
    result.classList.remove('hidden');

    // Also attempt to preview the JSON report by reading the zip (best-effort)
    reportEl.textContent = 'Bundle ready. Click "Download CP Bundle".';
  } catch (err) {
    alert(err.message);
  }
});
