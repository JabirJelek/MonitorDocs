document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("monitor-form");
  const list = document.getElementById("monitor-list");
  const tabFilter = document.getElementById("tab-filter");

  async function loadList() {
    list.innerHTML = "<li>Loading...</li>";
    try {
      let url = '/progress';
      const params = [];
      if (tabFilter && tabFilter.value) params.push('tab=' + encodeURIComponent(tabFilter.value));
      if (params.length) url += '?' + params.join('&');
      const res = await fetch(url);
      const data = await res.json();
      if (Array.isArray(data) && data.length) {
        list.innerHTML = '';
        data.forEach(item => {
          const li = document.createElement('li');
          li.textContent = `${item.id} — ${item.date} — ${item.agent_id} — [${item.tab}] — ${item.summary || ''}`;
          list.appendChild(li);
        });
      } else {
        list.innerHTML = '<li>No entries</li>';
      }
    } catch (e) {
      list.innerHTML = '<li>Error loading entries</li>';
    }
  }

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const fd = new FormData(form);
    const payload = {
      date: fd.get('date'),
      agent_id: fd.get('agent_id'),
      summary: fd.get('summary'),
      artifacts: [],
      tags: (fd.get('tags') || '').split(',').map(s=>s.trim()).filter(Boolean),
      tab: (fd.get('tab') || '').toString() || undefined
    };
    try {
      const res = await fetch('/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data && data.id) {
        form.reset();
        loadList();
      } else {
        alert('Failed to save');
      }
    } catch (e) {
      alert('Failed to save');
    }
  });

  loadList();
  async function loadTabs() {
    if (!tabFilter) return;
    try {
      const res = await fetch('/tabs');
      const data = await res.json();
      tabFilter.innerHTML = '<option value="">All</option>';
      if (Array.isArray(data)) {
        data.forEach(t => {
          const opt = document.createElement('option');
          opt.value = t;
          opt.textContent = t;
          tabFilter.appendChild(opt);
        });
      }
    } catch (e) {
      // ignore
    }
  }

  if (tabFilter) {
    tabFilter.addEventListener('change', () => loadList());
  }
  loadTabs();
});
