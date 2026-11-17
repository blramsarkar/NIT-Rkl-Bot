/* ==============================================================================
 * File: admin/admin.js
 * Role: Admin view logic. All data is rendered with textContent (no innerHTML),
 *       since logged questions are user input.
 * ============================================================================== */
(function () {
  'use strict';
  const API = '';  // same origin as the backend
  let key = null;
  try { key = sessionStorage.getItem('nitrkl_admin_key'); } catch (e) { /* ignore */ }

  const $ = (id) => document.getElementById(id);
  const td = (text, cls) => { const c = document.createElement('td'); if (cls) c.className = cls; c.textContent = text == null ? '' : String(text); return c; };
  const btn = (label, onClick, cls) => { const b = document.createElement('button'); b.type = 'button'; b.className = 'ghost ' + (cls || ''); b.textContent = label; b.addEventListener('click', onClick); return b; };
  const pill = (text, cls) => { const s = document.createElement('span'); s.className = 'pill ' + (cls || ''); s.textContent = text; return s; };
  const cell = (...nodes) => { const c = document.createElement('td'); nodes.forEach((n) => c.appendChild(n)); return c; };
  const short = (s, n) => (s || '').length > n ? s.slice(0, n - 1) + '…' : (s || '');

  async function api(path, opts) {
    const res = await fetch(API + path, Object.assign({}, opts, {
      headers: Object.assign({ 'Content-Type': 'application/json', 'X-Admin-Key': key || '' }, (opts && opts.headers) || {}),
    }));
    if (res.status === 401 || res.status === 503) {
      const body = await res.json().catch(() => ({}));
      signOut(body.detail || 'Not authorised');
      throw new Error('unauthorised');
    }
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return res.json();
  }

  function signOut(message) {
    key = null;
    try { sessionStorage.removeItem('nitrkl_admin_key'); } catch (e) { /* ignore */ }
    $('app').classList.add('hidden'); $('logoutBtn').classList.add('hidden'); $('loginCard').classList.remove('hidden');
    $('loginError').textContent = message || '';
  }

  async function signIn() {
    key = $('keyInput').value.trim();
    try {
      await api('/admin/stats');
      try { sessionStorage.setItem('nitrkl_admin_key', key); } catch (e) { /* ignore */ }
      $('loginCard').classList.add('hidden'); $('app').classList.remove('hidden'); $('logoutBtn').classList.remove('hidden');
      $('keyInput').value = '';
      showTab('overview');
    } catch (e) { if (e.message !== 'unauthorised') $('loginError').textContent = 'Could not reach the backend.'; }
  }

  function showTab(name) {
    document.querySelectorAll('#tabs button').forEach((b) => b.classList.toggle('active', b.dataset.tab === name));
    document.querySelectorAll('[data-panel]').forEach((p) => p.classList.toggle('hidden', p.dataset.panel !== name));
    ({ overview: loadOverview, logs: loadLogs, unanswered: loadUnanswered, verified: loadVerified, ingestion: loadRuns })[name]();
  }

  async function loadOverview() {
    const s = await api('/admin/stats');
    const items = [
      ['Total questions', s.total_queries], ['Thumbs up', s.thumbs_up], ['Thumbs down', s.thumbs_down],
      ['Unanswered', s.unanswered], ['Verified answers', s.verified_answers],
      ['LLM calls today', `${s.llm_budget.used} / ${s.llm_budget.limit}`],
      ['Last ingestion', s.last_ingestion ? `${s.last_ingestion.started_at.slice(0, 16)} (${s.last_ingestion.failed} failed)` : 'never'],
    ];
    const wrap = $('stats'); wrap.textContent = '';
    items.forEach(([k, v]) => {
      const d = document.createElement('div'); d.className = 'stat';
      const vv = document.createElement('div'); vv.className = 'v'; vv.textContent = v;
      const kk = document.createElement('div'); kk.className = 'k'; kk.textContent = k;
      d.appendChild(vv); d.appendChild(kk); wrap.appendChild(d);
    });
  }

  async function loadLogs() {
    const f = $('logFilter').value;
    const qs = f === 'negative' ? '?negative=true' : f === 'low' ? '?low_confidence=true' : '';
    const { logs } = await api('/admin/logs' + qs);
    const body = $('logRows'); body.textContent = '';
    if (!logs.length) { const tr = document.createElement('tr'); tr.appendChild(td('No entries.', 'muted')); body.appendChild(tr); return; }
    logs.forEach((l) => {
      const tr = document.createElement('tr');
      tr.appendChild(td(l.timestamp.slice(0, 16)));
      tr.appendChild(td(l.query));
      tr.appendChild(td(short(l.response, 400), 'resp'));
      tr.appendChild(cell(pill(l.route || '-', l.confidence < 0.6 ? 'bad' : '')));
      const fb = l.feedback === 1 ? pill('👍', 'good') : l.feedback === -1 ? pill('👎 ' + (l.feedback_comment || ''), 'bad') : pill('—');
      tr.appendChild(cell(fb));
      tr.appendChild(cell(btn('Fix answer', () => prefillVerified(l.query, '', null))));
      body.appendChild(tr);
    });
  }

  async function loadUnanswered() {
    const { queries } = await api('/admin/unanswered');
    const body = $('unansweredRows'); body.textContent = '';
    if (!queries.length) { const tr = document.createElement('tr'); tr.appendChild(td('Nothing unanswered.', 'muted')); body.appendChild(tr); return; }
    queries.forEach((q) => {
      const tr = document.createElement('tr');
      tr.appendChild(td(q.query)); tr.appendChild(td(q.frequency_count)); tr.appendChild(td(q.last_asked_at.slice(0, 16)));
      tr.appendChild(cell(
        btn('Write answer', () => prefillVerified(q.query, '', q.id)),
        btn('Dismiss', async () => { await api(`/admin/unanswered/${q.id}/resolve`, { method: 'POST' }); loadUnanswered(); }),
      ));
      body.appendChild(tr);
    });
  }

  function prefillVerified(question, answer, unansweredId, item) {
    showTab('verified');
    $('vaId').value = item ? item.id : '';
    $('vaUnansweredId').value = unansweredId || '';
    $('vaQuestion').value = question || '';
    $('vaAnswer').value = answer || '';
    $('vaSource').value = item ? (item.source_url || '') : '';
    $('vaActive').checked = item ? item.active : true;
    $('vaFormTitle').textContent = item ? 'Edit verified answer' : 'Add verified answer';
    $('vaMsg').textContent = '';
    $('vaAnswer').focus();
  }

  async function saveVerified() {
    const id = $('vaId').value;
    const source = $('vaSource').value.trim();
    if (source && !/^https:\/\/([a-z0-9-]+\.)*nitrkl\.ac\.in(\/|$)/i.test(source)) { $('vaMsg').textContent = 'Source must be an https://…nitrkl.ac.in URL.'; return; }
    const payload = {
      question: $('vaQuestion').value.trim(), answer: $('vaAnswer').value.trim(),
      source_url: source || null, active: $('vaActive').checked,
      resolve_unanswered_id: $('vaUnansweredId').value ? Number($('vaUnansweredId').value) : null,
    };
    if (payload.question.length < 3 || !payload.answer) { $('vaMsg').textContent = 'Question and answer are required.'; return; }
    await api(id ? `/admin/verified/${id}` : '/admin/verified', { method: id ? 'PUT' : 'POST', body: JSON.stringify(payload) });
    prefillVerified('', '', null);
    $('vaMsg').textContent = 'Saved.';
    loadVerified();
  }

  async function loadVerified() {
    const { answers } = await api('/admin/verified');
    const body = $('vaRows'); body.textContent = '';
    if (!answers.length) { const tr = document.createElement('tr'); tr.appendChild(td('No verified answers yet.', 'muted')); body.appendChild(tr); return; }
    answers.forEach((a) => {
      const tr = document.createElement('tr');
      tr.appendChild(td(a.question)); tr.appendChild(td(short(a.answer, 300), 'resp')); tr.appendChild(td(a.source_url || '—'));
      tr.appendChild(cell(pill(a.active ? 'active' : 'off', a.active ? 'good' : '')));
      tr.appendChild(cell(
        btn('Edit', () => prefillVerified(a.question, a.answer, null, a)),
        btn('Delete', async () => { if (confirm('Delete this verified answer?')) { await api(`/admin/verified/${a.id}`, { method: 'DELETE' }); loadVerified(); } }, 'danger'),
      ));
      body.appendChild(tr);
    });
  }

  async function loadRuns() {
    const { runs } = await api('/admin/ingestion-runs');
    const body = $('runRows'); body.textContent = '';
    if (!runs.length) { const tr = document.createElement('tr'); tr.appendChild(td('No runs yet.', 'muted')); body.appendChild(tr); return; }
    runs.forEach((r) => {
      const tr = document.createElement('tr');
      [r.started_at.slice(0, 16), r.trigger, r.updated, r.unchanged, r.failed].forEach((v) => tr.appendChild(td(v)));
      const pre = document.createElement('pre');
      pre.textContent = (r.details || []).map((d) => `${d.status.padEnd(9)} ${d.url}${d.message ? ' — ' + d.message : ''}`).join('\n');
      tr.appendChild(cell(pre));
      body.appendChild(tr);
    });
  }

  $('loginBtn').addEventListener('click', signIn);
  $('keyInput').addEventListener('keydown', (e) => { if (e.key === 'Enter') signIn(); });
  $('logoutBtn').addEventListener('click', () => signOut(''));
  document.querySelectorAll('#tabs button').forEach((b) => b.addEventListener('click', () => showTab(b.dataset.tab)));
  $('logFilter').addEventListener('change', loadLogs);
  $('refreshLogs').addEventListener('click', loadLogs);
  $('vaSave').addEventListener('click', () => saveVerified().catch((e) => { $('vaMsg').textContent = 'Save failed: ' + e.message; }));
  $('vaReset').addEventListener('click', () => prefillVerified('', '', null));
  $('reingestBtn').addEventListener('click', async () => { await api('/admin/reingest', { method: 'POST' }); $('overviewMsg').textContent = 'Started — check the Ingestion tab in a minute.'; });
  $('clearCacheBtn').addEventListener('click', async () => { await api('/admin/cache/clear', { method: 'POST' }); $('overviewMsg').textContent = 'Cache cleared.'; });

  if (key) {
    api('/admin/stats').then(() => {
      $('loginCard').classList.add('hidden'); $('app').classList.remove('hidden'); $('logoutBtn').classList.remove('hidden');
      showTab('overview');
    }).catch(() => {});
  }
})();
