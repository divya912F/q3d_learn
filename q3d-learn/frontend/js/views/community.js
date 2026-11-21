// Community — classroom discussion & chat. Friends in the same classroom discuss and
// solve problems together. Polls for new messages; works with any classroom code.
import { api } from '../api.js';
import { store } from '../store.js';
import { esc, icon, hydrateIcons, toast, initials } from '../ui.js';
import { t, langPicker } from '../i18n.js';

export async function render(root, { query }) {
  let code = (query?.get('code') || store.user?.classroom_code || sessionStorage.getItem('q3d-class') || '').toUpperCase();
  let lastId = 0;
  let timer = null;

  function shell() {
    root.innerHTML = `
      <div class="row-between" style="margin-bottom:14px">
        <div><span class="hand" style="font-size:1.3rem;color:var(--pink)">study together</span>
          <h2 style="margin:0">${icon('chat')} ${esc(t('Community'))}</h2>
          <p class="muted" style="margin:4px 0 0">${esc(t('Discuss and solve problems with your class'))}</p></div>
        <div class="row" data-lang></div>
      </div>
      <div class="row" style="gap:8px;margin-bottom:14px;flex-wrap:nowrap">
        <input class="input mono" data-code value="${esc(code)}" placeholder="Classroom code (e.g. DEMO42)" maxlength="12" style="max-width:220px">
        <button class="btn btn-primary btn-sm" data-join>${icon('arrowRight')} Open</button>
        <span class="faint small">Join a classroom from your profile, or try <b class="mono">DEMO42</b>.</span>
      </div>
      <div data-body></div>`;
    root.querySelector('[data-lang]').appendChild(langPicker(() => { stop(); shell(); open(); }));
    hydrateIcons(root);
    root.querySelector('[data-join]').addEventListener('click', () => {
      code = root.querySelector('[data-code]').value.trim().toUpperCase();
      sessionStorage.setItem('q3d-class', code);
      lastId = 0; open();
    });
  }

  async function open() {
    const body = root.querySelector('[data-body]');
    if (!code) { body.innerHTML = `<div class="card empty"><i data-icon="chat"></i><div>Enter a classroom code above to start chatting.</div></div>`; hydrateIcons(body); return; }
    body.innerHTML = `<div class="card" style="display:flex;flex-direction:column;height:min(62vh,560px);padding:0">
        <div class="row-between" style="padding:12px 16px;border-bottom:1px solid var(--line)"><b>${icon('users')} ${esc(code)}</b><span class="faint tiny">live discussion</span></div>
        <div data-msgs style="flex:1;overflow-y:auto;padding:14px 16px;display:flex;flex-direction:column;gap:10px"></div>
        <form data-send class="row" style="gap:8px;padding:12px 16px;border-top:1px solid var(--line);flex-wrap:nowrap">
          <input class="input grow" name="body" placeholder="${esc(t('Type a message…'))}" maxlength="2000" ${store.user ? '' : 'disabled'}>
          <button class="btn btn-primary" ${store.user ? '' : 'disabled'}>${icon('send')} ${esc(t('Send'))}</button>
        </form>
        ${store.user ? '' : `<div class="faint small" style="padding:0 16px 12px">${esc(t('Sign in to join the discussion'))}.</div>`}</div>`;
    hydrateIcons(body);
    root.querySelector('[data-send]').addEventListener('submit', async (e) => {
      e.preventDefault();
      const inp = e.target.body; const text = inp.value.trim();
      if (!text || !store.user) return;
      inp.value = '';
      try { await api.sendChat(code, { user_id: store.user.id, name: store.user.name, body: text }); await poll(); }
      catch (err) { toast(err.message, 'error'); }
    });
    stop();
    try { await poll(true); timer = setInterval(poll, 4000); }
    catch (e) { root.querySelector('[data-msgs]').innerHTML = `<div class="faint small">${esc(e.message)}</div>`; }
  }

  async function poll(first = false) {
    const box = root.querySelector('[data-msgs]'); if (!box) return;
    const data = await api.chat(code, lastId);
    if (first && !data.messages.length) box.innerHTML = `<div class="faint small" style="margin:auto">${esc(t('No messages yet — say hello!'))}</div>`;
    if (data.messages.length && box.querySelector('.faint')) box.innerHTML = '';
    for (const m of data.messages) {
      lastId = Math.max(lastId, m.id);
      const mine = store.user && m.user_id === store.user.id;
      const row = document.createElement('div');
      row.style.cssText = `display:flex;gap:9px;${mine ? 'flex-direction:row-reverse' : ''}`;
      row.innerHTML = `<span class="avatar" style="flex:none;width:30px;height:30px;font-size:.72rem">${esc(initials(m.name))}</span>
        <div style="max-width:76%"><div class="small" style="margin-bottom:2px;${mine ? 'text-align:right' : ''}"><b>${esc(m.name)}</b> <span class="faint tiny">${m.at ? new Date(m.at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}</span></div>
        <div class="card" style="padding:8px 12px;margin:0;${mine ? 'background:color-mix(in srgb,var(--primary) 12%,transparent)' : ''};white-space:pre-wrap">${esc(m.body)}</div></div>`;
      box.appendChild(row);
    }
    if (data.messages.length) box.scrollTop = box.scrollHeight;
  }

  function stop() { if (timer) { clearInterval(timer); timer = null; } }
  shell();
  await open();
  return stop;   // cleanup when navigating away
}
