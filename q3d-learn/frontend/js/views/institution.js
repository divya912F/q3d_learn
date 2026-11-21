// Institution mode (SSO) — organisations sign their members in with one code; an admin
// view lists members. A lightweight, provider-agnostic SSO-style flow.
import { api } from '../api.js';
import { store } from '../store.js';
import { esc, icon, hydrateIcons, toast } from '../ui.js';
import { t, langPicker } from '../i18n.js';

export async function render(root) {
  function shell() {
    root.innerHTML = `
      <div class="row-between" style="margin-bottom:14px">
        <div><span class="hand" style="font-size:1.3rem;color:var(--pink)">for schools & colleges</span>
          <h2 style="margin:0">${icon('school')} ${esc(t('Institution'))}</h2>
          <p class="muted" style="margin:4px 0 0">${esc(t('Sign your whole institution in with one code'))}</p></div>
        <div class="row" data-lang></div>
      </div>
      <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px">
        <div class="card"><div class="card-head"><h3 style="margin:0">${icon('key')} ${esc(t('Institution sign-in (SSO)'))}</h3></div>
          <form data-sso class="stack" style="gap:8px">
            <input class="input mono" name="code" placeholder="Institution code" maxlength="16" required>
            <input class="input" name="name" placeholder="Your full name" required>
            <input class="input" name="email" type="email" placeholder="Your institution email" required>
            <div class="role-pick"><label><input type="radio" name="role" value="student" checked> <span><b>Student</b></span></label>
            <label><input type="radio" name="role" value="instructor"> <span><b>Instructor</b></span></label></div>
            <button class="btn btn-primary btn-sm">${icon('arrowRight')} Sign in with institution</button></form></div>

        <div class="card"><div class="card-head"><h3 style="margin:0">${icon('plus')} Register an institution</h3></div>
          <form data-reg class="stack" style="gap:8px">
            <input class="input" name="name" placeholder="Institution name (e.g. MIET)" required>
            <input class="input" name="admin_name" placeholder="Admin name (optional)">
            <input class="input" name="domain" placeholder="Allowed email domain, e.g. miet.ac.in (optional)">
            <button class="btn btn-ghost btn-sm">${icon('school')} Create & get code</button></form>
          <div data-reg-out class="faint small" style="margin-top:8px"></div></div>

        <div class="card"><div class="card-head"><h3 style="margin:0">${icon('users')} Admin — ${esc(t('Members'))}</h3></div>
          <form data-admin class="row" style="gap:8px;flex-wrap:nowrap">
            <input class="input mono grow" name="code" placeholder="Institution code" maxlength="16">
            <button class="btn btn-ghost btn-sm">${icon('search')} View</button></form>
          <div data-admin-out style="margin-top:10px"></div></div>
      </div>`;
    root.querySelector('[data-lang]').appendChild(langPicker(() => shell()));
    hydrateIcons(root);

    root.querySelector('[data-sso]').addEventListener('submit', async (e) => {
      e.preventDefault(); const f = e.target;
      try {
        const r = await api.ssoLogin({ code: f.code.value.trim().toUpperCase(), name: f.name.value.trim(), email: f.email.value.trim(), role: f.role.value });
        store.set('user', r.user);
        toast(`Signed in to ${esc(r.institution.name)} as ${esc(r.user.name)}`, 'success');
        setTimeout(() => location.reload(), 700);
      } catch (err) { toast(err.message, 'error'); }
    });

    root.querySelector('[data-reg]').addEventListener('submit', async (e) => {
      e.preventDefault(); const f = e.target;
      try {
        const r = await api.createInstitution({ name: f.name.value.trim(), admin_name: f.admin_name.value.trim(), domain: f.domain.value.trim() || null });
        root.querySelector('[data-reg-out]').innerHTML = `✓ Created <b>${esc(r.name)}</b>. Share this code with your members: <b class="mono chip">${esc(r.code)}</b>${r.domain ? ` · emails must end in <b>@${esc(r.domain)}</b>` : ''}`;
        f.reset();
      } catch (err) { toast(err.message, 'error'); }
    });

    root.querySelector('[data-admin]').addEventListener('submit', async (e) => {
      e.preventDefault();
      const out = root.querySelector('[data-admin-out]');
      try {
        const d = await api.institution(e.target.code.value.trim().toUpperCase());
        out.innerHTML = `<div class="row-between" style="margin-bottom:8px"><b>${esc(d.name)}</b><span class="chip">${d.count} ${esc(t('Members'))}</span></div>
          ${d.members.length ? `<table class="table"><thead><tr><th>Name</th><th>Email</th><th>Role</th></tr></thead><tbody>
          ${d.members.map((m) => `<tr><td>${esc(m.name)}</td><td class="small">${esc(m.email)}</td><td><span class="chip ${m.role === 'instructor' ? 'violet' : 'gray'}">${esc(m.role)}</span></td></tr>`).join('')}</tbody></table>`
          : '<div class="faint small">No members have signed in yet.</div>'}`;
      } catch (err) { out.innerHTML = `<div class="faint small">${esc(err.message)}</div>`; }
    });
  }
  shell();
}
