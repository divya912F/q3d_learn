// Practice — LeetCode Connect. Curated LeetCode problems linked to each course;
// learners open them on leetcode.com and mark them solved to track progress.
import { api } from '../api.js';
import { store } from '../store.js';
import { esc, icon, hydrateIcons, toast } from '../ui.js';
import { t, langPicker } from '../i18n.js';

const DIFF = { Easy: 'green', Medium: 'amber', Hard: 'red' };

export async function render(root, { query }) {
  let course = query?.get('course') || 'dsa';

  function shell() {
    root.innerHTML = `
      <div class="row-between" style="margin-bottom:14px">
        <div><span class="hand" style="font-size:1.3rem;color:var(--pink)">sharpen up</span>
          <h2 style="margin:0">${icon('code')} ${esc(t('Practice'))} · LeetCode</h2>
          <p class="muted" style="margin:4px 0 0">${esc(t('Linked practice problems to sharpen your skills'))}</p></div>
        <div class="row" data-lang></div>
      </div>
      <div class="seg" data-course style="margin:6px 0 16px;max-width:640px;flex-wrap:wrap">
        ${store.courses.map((c) => `<button data-c="${c.id}" class="${course === c.id ? 'active' : ''}">${esc(c.short)}</button>`).join('')}
      </div>
      <div data-body></div>`;
    root.querySelector('[data-lang]').appendChild(langPicker(() => { shell(); load(); }));
    hydrateIcons(root);
    root.querySelector('[data-course]').addEventListener('click', (e) => {
      const b = e.target.closest('[data-c]'); if (!b) return;
      course = b.dataset.c;
      root.querySelectorAll('[data-c]').forEach((x) => x.classList.toggle('active', x === b));
      load();
    });
  }

  async function load() {
    const body = root.querySelector('[data-body]');
    try {
      const data = await api.leetcode(course, store.user?.id);
      if (!data.problems.length) { body.innerHTML = `<div class="card empty"><i data-icon="code"></i><div>No linked problems for this course yet — try DSA or Cybersecurity.</div></div>`; hydrateIcons(body); return; }
      const done = data.problems.filter((p) => p.solved).length;
      body.innerHTML = `
        <div class="callout insight" style="margin-bottom:14px"><i data-icon="trophy"></i><div><b>${done}/${data.problems.length}</b> solved. ${store.user ? 'Keep going — each one counts toward your mastery.' : 'Sign in to track which problems you’ve solved.'}</div></div>
        <div class="stack" style="gap:10px">${data.problems.map((p) => `
          <div class="card" style="padding:12px 14px"><div class="row-between" style="flex-wrap:nowrap;gap:10px">
            <div><b>${esc(p.title)}</b> <span class="chip ${DIFF[p.difficulty] || 'gray'}">${esc(t('Difficulty'))}: ${esc(p.difficulty)}</span> <span class="chip gray">${esc(p.topic)}</span></div>
            <div class="row" style="gap:8px;flex-wrap:nowrap">
              <a class="btn btn-ghost btn-sm" href="${esc(p.url)}" target="_blank" rel="noopener">${icon('link')} ${esc(t('Open on LeetCode'))}</a>
              <button class="btn btn-sm ${p.solved ? 'btn-primary' : 'btn-ghost'}" data-slug="${esc(p.slug)}" ${store.user ? '' : 'disabled title="Sign in to track"'}>${icon('check')} ${p.solved ? esc(t('Solved')) : esc(t('Mark solved'))}</button>
            </div></div></div>`).join('')}</div>`;
      hydrateIcons(body);
      body.querySelectorAll('[data-slug]').forEach((btn) => btn.addEventListener('click', async () => {
        const slug = btn.dataset.slug;
        const nowSolved = !btn.classList.contains('btn-primary');
        try {
          await api.solvePractice({ user_id: store.user.id, course, slug, solved: nowSolved });
          load();
        } catch (e) { toast(e.message, 'error'); }
      }));
    } catch (e) { body.innerHTML = `<div class="card empty"><i data-icon="alert"></i><div>${esc(e.message)}</div></div>`; hydrateIcons(body); }
  }
  shell();
  await load();
}
