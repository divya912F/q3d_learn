// Per-course leaderboard — ranks learners by XP from lessons, quizzes and challenges.
import { api } from '../api.js';
import { store } from '../store.js';
import { esc, icon, hydrateIcons } from '../ui.js';
import { t, langPicker } from '../i18n.js';

export async function render(root, { query }) {
  let course = query?.get('course') || 'all';
  const medal = ['#f1b000', '#9aa6c4', '#cd7f32'];

  function shell() {
    root.innerHTML = `
      <div class="row-between" style="margin-bottom:14px">
        <div><span class="hand" style="font-size:1.3rem;color:var(--pink)">who's on top?</span>
          <h2 style="margin:0">${icon('trophy')} ${esc(t('Leaderboard'))}</h2>
          <p class="muted" style="margin:4px 0 0">${esc(t('Leaderboard — climb your course'))}</p></div>
        <div class="row" data-lang></div>
      </div>
      <div class="seg" data-course style="margin:6px 0 16px;max-width:640px;flex-wrap:wrap">
        <button data-c="all" class="${course === 'all' ? 'active' : ''}">${esc(t('All courses'))}</button>
        ${store.courses.map((c) => `<button data-c="${c.id}" class="${course === c.id ? 'active' : ''}">${esc(c.short)}</button>`).join('')}
      </div>
      <div data-body><div class="card empty"><i data-icon="trophy"></i><div>Loading…</div></div></div>`;
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
      const data = await api.leaderboard(course);
      const me = store.user?.id;
      if (!data.entries.length) {
        body.innerHTML = `<div class="card empty"><i data-icon="trophy"></i><div>No scores yet for this course. Complete a lesson or solve a challenge to get on the board!</div></div>`;
        hydrateIcons(body); return;
      }
      body.innerHTML = `<div class="card" style="padding:0;overflow:hidden">
        <table class="table"><thead><tr><th style="width:70px">${esc(t('Rank'))}</th><th>${esc(t('Student'))}</th><th>${esc(t('Points'))}</th><th>${esc(t('Lessons'))}</th><th>${esc(t('Challenges'))}</th></tr></thead>
        <tbody>${data.entries.map((r) => `<tr style="${r.user_id === me ? 'background:color-mix(in srgb,var(--primary) 10%,transparent)' : ''}">
          <td><span style="font-weight:800;color:${medal[r.rank - 1] || 'var(--text-2)'}">${r.rank <= 3 ? '●' : ''} ${r.rank}</span></td>
          <td><b>${esc(r.name)}</b>${r.user_id === me ? ' <span class="chip">you</span>' : ''}</td>
          <td><b class="mono">${r.xp}</b> <span class="faint tiny">XP</span></td>
          <td>${r.lessons}</td><td>${r.challenges}</td></tr>`).join('')}</tbody></table></div>`;
      hydrateIcons(body);
    } catch (e) {
      body.innerHTML = `<div class="card empty"><i data-icon="alert"></i><div>${esc(e.message)}</div></div>`;
      hydrateIcons(body);
    }
  }
  shell();
  await load();
}
