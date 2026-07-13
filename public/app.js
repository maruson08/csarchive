async function loadEntries() {
  const res = await fetch('/api/entries');
  const data = await res.json();
  renderEntries(data.entries || []);
}

function renderEntries(entries) {
  const container = document.getElementById('entries');
  if (!entries.length) {
    container.innerHTML = '<p>아직 저장된 항목이 없습니다.</p>';
    return;
  }

  container.innerHTML = entries
    .slice()
    .reverse()
    .map((entry) => `
      <article class="entry-card">
        <h3>Week ${entry.week}</h3>
        <p><strong>Colab:</strong> <a href="${entry.colab_link}" target="_blank" rel="noreferrer">${entry.colab_link}</a></p>
        <p><strong>느낀점:</strong> ${entry.reflection}</p>
        <p><strong>개선할 점:</strong> ${entry.improvement}</p>
        <p><small>${entry.id}</small></p>
      </article>
    `)
    .join('');
}

document.getElementById('entry-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = Object.fromEntries(new FormData(form).entries());

  const res = await fetch('/api/entries', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (res.ok) {
    form.reset();
    loadEntries();
  }
});

loadEntries();
