// Course authoring — instructors build and publish their own video courses; anyone can watch.
import { api } from '../api.js';
import { store } from '../store.js';
import { esc, icon, hydrateIcons, toast, markdown } from '../ui.js';
import { t, langPicker } from '../i18n.js';
import { openProfile } from '../main.js';

function embed(url) {
  if (!url) return '';
  const yt = url.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|shorts\/))([\w-]{11})/);
  if (yt) return `<div class="video-wrap" style="position:relative;padding-top:56.25%;border-radius:12px;overflow:hidden;margin:8px 0"><iframe src="https://www.youtube.com/embed/${yt[1]}" style="position:absolute;inset:0;width:100%;height:100%;border:0" allowfullscreen loading="lazy"></iframe></div>`;
  if (/\.(mp4|webm|ogg)(\?|$)/i.test(url)) return `<video controls preload="none" style="width:100%;border-radius:12px;margin:8px 0" src="${esc(url)}"></video>`;
  return `<a class="btn btn-ghost btn-sm" href="${esc(url)}" target="_blank" rel="noopener">${icon('play')} Watch video</a>`;
}

export async function render(root, { query }) {
  const isInstr = store.user?.role === 'instructor';
  const openId = query?.get('course');

  function shell() {
    root.innerHTML = `
      <div class="row-between" style="margin-bottom:14px">
        <div><span class="hand" style="font-size:1.3rem;color:var(--pink)">teach the world</span>
          <h2 style="margin:0">${icon('cap')} ${esc(t('Create course'))}</h2>
          <p class="muted" style="margin:4px 0 0">${esc(t('Build and publish your own video course'))}</p></div>
        <div class="row" data-lang>${isInstr ? `<button class="btn btn-primary btn-sm" data-new>${icon('plus')} New course</button>` : ''}</div>
      </div>
      <div data-build></div><div data-body></div>`;
    root.querySelector('[data-lang]').insertBefore(langPicker(() => { shell(); openId ? open(openId) : load(); }), root.querySelector('[data-new]') || null);
    hydrateIcons(root);
    root.querySelector('[data-new]')?.addEventListener('click', newCourse);
  }

  async function load() {
    const body = root.querySelector('[data-body]');
    try {
      const courses = await api.authoredCourses();
      body.innerHTML = courses.length ? `<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px">${courses.map((c) => `
        <div class="card"><div class="card-head"><h3 style="margin:0">${esc(c.title)}</h3>${c.price ? `<span class="chip amber">₹${c.price}</span>` : '<span class="chip green">Free</span>'}</div>
          <p class="small">${esc(c.summary || 'No description yet.')}</p>
          <div class="row-between"><span class="faint tiny">${icon('user')} ${esc(c.instructor_name || 'Instructor')} · ${c.lesson_count} lesson${c.lesson_count === 1 ? '' : 's'}</span>
          <button class="btn btn-ghost btn-sm" data-open="${c.id}">${icon('arrowRight')} Open</button></div></div>`).join('')}</div>`
        : `<div class="card empty"><i data-icon="cap"></i><div>No instructor courses yet. ${isInstr ? 'Click “New course” to publish the first one!' : 'Check back soon.'}</div></div>`;
      hydrateIcons(body);
      body.querySelectorAll('[data-open]').forEach((b) => b.addEventListener('click', () => open(b.dataset.open)));
    } catch (e) { body.innerHTML = `<div class="card empty"><i data-icon="alert"></i><div>${esc(e.message)}</div></div>`; hydrateIcons(body); }
  }

  async function open(cid) {
    const body = root.querySelector('[data-body]');
    root.querySelector('[data-build]').innerHTML = '';
    const c = await api.authoredCourse(cid);
    const owner = isInstr && store.user.id === c.instructor_id;
    body.innerHTML = `<button class="btn btn-ghost btn-sm" data-back>${icon('undo')} All courses</button>
      <div class="card" style="margin-top:12px"><div class="card-head"><h2 style="margin:0">${esc(c.title)}</h2>${c.price ? `<span class="chip amber">₹${c.price}</span>` : '<span class="chip green">Free</span>'}</div>
        <p>${esc(c.summary || '')}</p><p class="faint small">${icon('user')} ${esc(c.instructor_name || 'Instructor')}</p></div>
      <div class="stack" style="gap:14px;margin-top:14px">${c.lessons.length ? c.lessons.map((l, i) => `
        <div class="card"><h3 style="margin:0 0 4px">${i + 1}. ${esc(l.title)}</h3>${embed(l.video_url)}${l.body ? `<div class="small">${markdown(l.body)}</div>` : ''}</div>`).join('')
        : '<div class="card empty"><i data-icon="book"></i><div>No lessons yet.</div></div>'}</div>
      ${owner ? `<div class="card" style="margin-top:14px"><div class="card-head"><h3>${icon('plus')} Add a lesson</h3></div>
        <form data-lesson class="stack" style="gap:8px">
          <input class="input" name="title" placeholder="Lesson title" required>
          <input class="input" name="video_url" type="url" placeholder="Video URL (YouTube or .mp4) — optional">
          <textarea class="input" name="body" rows="3" placeholder="Lesson notes (markdown supported) — optional"></textarea>
          <button class="btn btn-primary btn-sm">${icon('plus')} Add lesson</button></form></div>` : ''}`;
    hydrateIcons(body);
    body.querySelector('[data-back]').addEventListener('click', load);
    body.querySelector('[data-lesson]')?.addEventListener('submit', async (e) => {
      e.preventDefault(); const f = e.target;
      try {
        await api.addAuthoredLesson(cid, { title: f.title.value, video_url: f.video_url.value || null, body: f.body.value, instructor_id: store.user.id });
        toast('Lesson added', 'success'); open(cid);
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  function newCourse() {
    if (!isInstr) { openProfile(); return; }
    const box = root.querySelector('[data-build]');
    box.innerHTML = `<div class="card" style="margin-bottom:16px"><div class="card-head"><h3>${icon('plus')} New course</h3><button class="icon-btn btn-sm" data-close>${icon('x')}</button></div>
      <form data-form class="stack" style="gap:10px">
        <input class="input" name="title" placeholder="Course title" required>
        <textarea class="input" name="summary" rows="3" placeholder="What will students learn?"></textarea>
        <div class="row" style="gap:8px;flex-wrap:nowrap"><label class="field" style="margin:0">Price ₹ <input class="input" name="price" type="number" min="0" value="0" style="width:120px"></label>
        <span class="faint tiny" style="align-self:center">0 = free. Paid courses use the instructor payment gateway (separate add-on).</span></div>
        <button class="btn btn-primary btn-sm">${icon('save')} Create course</button></form></div>`;
    hydrateIcons(box); box.scrollIntoView({ behavior: 'smooth' });
    box.querySelector('[data-close]').addEventListener('click', () => { box.innerHTML = ''; });
    box.querySelector('[data-form]').addEventListener('submit', async (e) => {
      e.preventDefault(); const f = e.target;
      try {
        const c = await api.createAuthoredCourse({ title: f.title.value, summary: f.summary.value, instructor_id: store.user.id, price: +f.price.value || 0 });
        toast('Course created — add your first lesson!', 'success'); box.innerHTML = ''; open(c.id);
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  shell();
  if (openId) await open(openId); else await load();
}
