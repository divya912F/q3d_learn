// Tests — instructor-authored tests/quizzes. Students take them; instructors build them
// with a question editor and see results.
import { api } from '../api.js';
import { store } from '../store.js';
import { esc, icon, hydrateIcons, toast, confetti } from '../ui.js';
import { t, langPicker } from '../i18n.js';

export async function render(root) {
  const isInstr = store.user?.role === 'instructor';

  function shell() {
    root.innerHTML = `
      <div class="row-between" style="margin-bottom:14px">
        <div><span class="hand" style="font-size:1.3rem;color:var(--pink)">test yourself</span>
          <h2 style="margin:0">${icon('checkCircle')} ${esc(t('Tests'))}</h2>
          <p class="muted" style="margin:4px 0 0">${esc(t('Instructor-created tests and quizzes'))}</p></div>
        <div class="row" data-lang>${isInstr ? `<button class="btn btn-primary btn-sm" data-new>${icon('plus')} New test</button>` : ''}</div>
      </div>
      <div data-build></div>
      <div data-body><div class="card empty"><i data-icon="checkCircle"></i><div>Loading…</div></div></div>`;
    root.querySelector('[data-lang]').insertBefore(langPicker(() => { shell(); load(); }), root.querySelector('[data-new]') || null);
    hydrateIcons(root);
    root.querySelector('[data-new]')?.addEventListener('click', () => builder());
  }

  async function load() {
    const body = root.querySelector('[data-body]');
    try {
      const tests = await api.tests(isInstr ? `?instructor_id=${store.user.id}` : '');
      if (!tests.length) { body.innerHTML = `<div class="card empty"><i data-icon="checkCircle"></i><div>${isInstr ? 'No tests yet — click “New test” to build one.' : 'No tests have been published yet. Check back soon!'}</div></div>`; hydrateIcons(body); return; }
      body.innerHTML = `<div class="stack" style="gap:10px">${tests.map((t2) => `
        <div class="card" style="padding:12px 14px"><div class="row-between" style="flex-wrap:nowrap;gap:10px">
          <div><b>${esc(t2.title)}</b> <span class="chip gray">${t2.questions} question${t2.questions === 1 ? '' : 's'}</span>${t2.course ? `<span class="chip">${esc(store.courseMeta(t2.course)?.short || t2.course)}</span>` : ''}</div>
          <div class="row" style="gap:8px;flex-wrap:nowrap">
            <button class="btn btn-primary btn-sm" data-take="${t2.id}">${icon('play')} ${esc(t('Take test'))}</button>
            ${isInstr ? `<button class="btn btn-ghost btn-sm" data-results="${t2.id}">${icon('chart')} Results</button>` : ''}</div></div></div>`).join('')}</div>`;
      hydrateIcons(body);
      body.querySelectorAll('[data-take]').forEach((b) => b.addEventListener('click', () => take(b.dataset.take)));
      body.querySelectorAll('[data-results]').forEach((b) => b.addEventListener('click', () => results(b.dataset.results)));
    } catch (e) { body.innerHTML = `<div class="card empty"><i data-icon="alert"></i><div>${esc(e.message)}</div></div>`; hydrateIcons(body); }
  }

  async function take(tid) {
    const body = root.querySelector('[data-body]');
    const test = await api.test(tid);
    body.innerHTML = `<button class="btn btn-ghost btn-sm" data-back>${icon('undo')} Back</button>
      <div class="card" style="margin-top:12px"><h3>${esc(test.title)}</h3>
      <form data-quiz class="stack" style="gap:16px">${test.questions.map((q, i) => `
        <div><div style="font-weight:600;margin-bottom:6px">${i + 1}. ${esc(q.prompt)}</div>
        ${q.options.map((o, j) => `<label class="opt"><input type="radio" name="q${i}" value="${j}"> <span>${esc(o)}</span></label>`).join('')}</div>`).join('')}
        <button class="btn btn-primary">${icon('check')} Submit answers</button></form></div>`;
    hydrateIcons(body);
    body.querySelector('[data-back]').addEventListener('click', load);
    body.querySelector('[data-quiz]').addEventListener('submit', async (e) => {
      e.preventDefault();
      const answers = test.questions.map((_, i) => { const sel = e.target.querySelector(`[name="q${i}"]:checked`); return sel ? +sel.value : -1; });
      try {
        const r = await api.submitTest(tid, { user_id: store.user?.id || null, name: store.user?.name || 'Guest', answers });
        if (r.percent >= 80) confetti();
        body.querySelector('.card').insertAdjacentHTML('afterbegin',
          `<div class="callout ${r.percent >= 60 ? 'insight' : 'warning'}"><i data-icon="${r.percent >= 60 ? 'checkCircle' : 'alert'}"></i><div><b>${esc(t('Your score'))}: ${r.score}/${r.total} (${r.percent}%)</b></div></div>`);
        test.questions.forEach((q, i) => {
          const sel = body.querySelector(`[name="q${i}"]:checked`);
          const given = sel ? +sel.value : -1;
          body.querySelectorAll(`[name="q${i}"]`).forEach((inp) => {
            const lab = inp.closest('.opt'); const j = +inp.value;
            if (j === r.results[i].answer) lab.style.cssText = 'background:color-mix(in srgb,var(--green) 18%,transparent);border-radius:8px';
            else if (j === given) lab.style.cssText = 'background:color-mix(in srgb,var(--red) 16%,transparent);border-radius:8px';
            inp.disabled = true;
          });
          if (r.results[i].explain) inp_explain(body, i, r.results[i].explain);
        });
        hydrateIcons(body);
        body.querySelector('[data-quiz] button[type],[data-quiz] .btn')?.remove();
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  function inp_explain(body, i, text) {
    const blocks = body.querySelectorAll('[data-quiz] > div');
    if (blocks[i]) blocks[i].insertAdjacentHTML('beforeend', `<div class="faint small" style="margin-top:4px">${icon('bulb')} ${esc(text)}</div>`);
  }

  async function results(tid) {
    const body = root.querySelector('[data-body]');
    const rows = await api.testResults(tid);
    body.innerHTML = `<button class="btn btn-ghost btn-sm" data-back>${icon('undo')} Back</button>
      <div class="card" style="margin-top:12px"><h3>${icon('chart')} Results</h3>
      ${rows.length ? `<table class="table"><thead><tr><th>Student</th><th>Score</th><th>When</th></tr></thead><tbody>
        ${rows.map((r) => `<tr><td>${esc(r.name)}</td><td><span class="chip ${r.percent >= 60 ? 'green' : 'red'}">${r.score}/${r.total} · ${r.percent}%</span></td><td class="faint small">${r.at ? new Date(r.at).toLocaleString() : ''}</td></tr>`).join('')}</tbody></table>`
        : '<div class="faint small">No attempts yet.</div>'}</div>`;
    hydrateIcons(body);
    body.querySelector('[data-back]').addEventListener('click', load);
  }

  function builder() {
    const box = root.querySelector('[data-build]');
    let n = 1;
    const qBlock = (i) => `<div class="card" data-q style="padding:12px 14px;background:color-mix(in srgb,var(--course,var(--primary)) 5%,transparent)">
        <input class="input" name="prompt" placeholder="Question ${i + 1}" required style="margin-bottom:8px">
        ${[0, 1, 2, 3].map((j) => `<label class="row" style="gap:8px;flex-wrap:nowrap;margin:4px 0"><input type="radio" name="correct" value="${j}" ${j === 0 ? 'checked' : ''} title="correct answer"><input class="input grow" name="opt${j}" placeholder="Option ${j + 1}" ${j < 2 ? 'required' : ''}></label>`).join('')}
        <input class="input" name="explain" placeholder="Explanation (optional)" style="margin-top:6px">
      </div>`;
    box.innerHTML = `<div class="card" style="margin-bottom:16px"><div class="card-head"><h3>${icon('plus')} New test</h3><button class="icon-btn btn-sm" data-close>${icon('x')}</button></div>
      <form data-form class="stack" style="gap:10px">
        <input class="input" name="title" placeholder="Test title (e.g. Week 2 — Sorting quiz)" required>
        <div class="row" style="gap:8px;flex-wrap:nowrap"><select class="input" name="course"><option value="">No specific course</option>${store.courses.map((c) => `<option value="${c.id}">${esc(c.title)}</option>`).join('')}</select>
        <input class="input mono" name="classroom_code" placeholder="Classroom code (optional)" maxlength="12" style="max-width:200px"></div>
        <div data-qs class="stack" style="gap:10px">${qBlock(0)}</div>
        <div class="row" style="gap:8px"><button type="button" class="btn btn-ghost btn-sm" data-addq>${icon('plus')} Add question</button>
        <button class="btn btn-primary btn-sm">${icon('save')} Publish test</button></div></form></div>`;
    hydrateIcons(box);
    box.scrollIntoView({ behavior: 'smooth' });
    box.querySelector('[data-close]').addEventListener('click', () => { box.innerHTML = ''; });
    box.querySelector('[data-addq]').addEventListener('click', () => { box.querySelector('[data-qs]').insertAdjacentHTML('beforeend', qBlock(n++)); hydrateIcons(box); });
    box.querySelector('[data-form]').addEventListener('submit', async (e) => {
      e.preventDefault();
      const f = e.target;
      const questions = [...box.querySelectorAll('[data-q]')].map((q) => {
        const opts = [0, 1, 2, 3].map((j) => q.querySelector(`[name="opt${j}"]`).value.trim()).filter(Boolean);
        return { prompt: q.querySelector('[name="prompt"]').value.trim(), options: opts, answer: Math.min(+q.querySelector('[name="correct"]:checked').value, opts.length - 1), explain: q.querySelector('[name="explain"]').value.trim() };
      }).filter((q) => q.prompt && q.options.length >= 2);
      if (!questions.length) { toast('Add at least one question with two options', 'error'); return; }
      try {
        await api.createTest({ title: f.title.value, course: f.course.value || null, classroom_code: f.classroom_code.value.trim().toUpperCase() || null, instructor_id: store.user.id, questions });
        toast('Test published!', 'success'); box.innerHTML = ''; load();
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  shell();
  await load();
}
