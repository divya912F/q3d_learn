// Mini-projects — one or two capstone projects that finish each course.
import { api } from '../api.js';
import { store } from '../store.js';
import { esc, icon, hydrateIcons, toast, markdown } from '../ui.js';
import { t, langPicker } from '../i18n.js';
import { openProfile } from '../main.js';

export async function render(root, { params, query }) {
  let course = params?.[0] || query?.get('course') || store.course || 'quantum';

  function shell() {
    root.innerHTML = `
      <div class="row-between" style="margin-bottom:14px">
        <div><span class="hand" style="font-size:1.3rem;color:var(--pink)">prove it</span>
          <h2 style="margin:0">${icon('rocket')} ${esc(t('Mini-projects'))}</h2>
          <p class="muted" style="margin:4px 0 0">${esc(t('Finish each course with a hands-on mini-project'))}</p></div>
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
      const data = await api.projects(course, store.user?.id);
      if (!data.projects.length) { body.innerHTML = `<div class="card empty"><i data-icon="rocket"></i><div>No mini-project for this course yet.</div></div>`; hydrateIcons(body); return; }
      body.innerHTML = `<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px">${data.projects.map((p) => `
        <div class="card"><div class="card-head"><h3 style="margin:0">${esc(p.title)}</h3>${p.submitted ? `<span class="chip green">${icon('check')} ${esc(t('Solved'))}</span>` : ''}</div>
          <p class="small">${markdown(p.brief)}</p>
          <div class="row" style="gap:6px;flex-wrap:wrap;margin:6px 0">${p.skills.map((s) => `<span class="chip gray">${esc(s)}</span>`).join('')}<span class="chip">${icon('clock')} ${esc(p.est)}</span></div>
          <hr>
          ${store.user ? `<form data-submit="${esc(p.id)}" class="stack" style="gap:8px">
            <input class="input" name="link" type="url" placeholder="Link to your project (GitHub, Drive, demo)…">
            <textarea class="input" name="note" rows="2" placeholder="A note about what you built (optional)"></textarea>
            <button class="btn btn-primary btn-sm">${icon('upload')} ${esc(t('Submit a project'))}</button></form>`
          : `<button class="btn btn-ghost btn-sm" data-signin>${icon('user')} Sign in to submit</button>`}
          <div class="faint tiny" data-subs="${esc(p.id)}" style="margin-top:8px"></div></div>`).join('')}</div>`;
      hydrateIcons(body);
      body.querySelector('[data-signin]')?.addEventListener('click', () => openProfile());
      body.querySelectorAll('[data-submit]').forEach((f) => f.addEventListener('submit', async (e) => {
        e.preventDefault();
        const pid = f.dataset.submit;
        try {
          await api.submitProject(pid, { user_id: store.user.id, name: store.user.name, link: f.link.value || null, note: f.note.value });
          toast('Project submitted! 🎉', 'success'); load();
        } catch (err) { toast(err.message, 'error'); }
      }));
      for (const p of data.projects) {
        api.projectSubmissions(p.id).then((subs) => {
          const el = body.querySelector(`[data-subs="${CSS.escape(p.id)}"]`);
          if (el && subs.length) el.textContent = `${subs.length} submission${subs.length > 1 ? 's' : ''} so far`;
        }).catch(() => {});
      }
    } catch (e) { body.innerHTML = `<div class="card empty"><i data-icon="alert"></i><div>${esc(e.message)}</div></div>`; hydrateIcons(body); }
  }
  shell();
  await load();
}
