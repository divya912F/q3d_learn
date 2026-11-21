// Lightweight i18n for Q-3D Learn. English default; additive — existing screens are
// untouched unless they opt in by calling t(). Language persists in localStorage.
const KEY = 'q3d-lang';
const LANGS = { en: 'English', hi: 'हिन्दी' };

const DICT = {
  en: {},  // English is the source of truth (keys are the English text)
  hi: {
    'Leaderboard': 'लीडरबोर्ड',
    'Community': 'समुदाय',
    'Practice': 'अभ्यास',
    'Tests': 'टेस्ट',
    'Mini-projects': 'मिनी-प्रोजेक्ट',
    'Projects': 'प्रोजेक्ट',
    'Create course': 'कोर्स बनाएं',
    'Institution': 'संस्थान',
    'Compete & connect': 'प्रतिस्पर्धा और जुड़ाव',
    'All courses': 'सभी कोर्स',
    'Rank': 'रैंक',
    'Student': 'छात्र',
    'Lessons': 'पाठ',
    'Challenges': 'चुनौतियाँ',
    'Solved': 'हल किया',
    'Submit': 'जमा करें',
    'Send': 'भेजें',
    'Sign in to join the discussion': 'चर्चा में शामिल होने के लिए साइन इन करें',
    'No messages yet — say hello!': 'अभी कोई संदेश नहीं — नमस्ते कहें!',
    'Type a message…': 'एक संदेश लिखें…',
    'Difficulty': 'कठिनाई',
    'Open on LeetCode': 'लीटकोड पर खोलें',
    'Mark solved': 'हल के रूप में चिह्नित करें',
    'Take test': 'टेस्ट दें',
    'Your score': 'आपका स्कोर',
    'Submit a project': 'प्रोजेक्ट जमा करें',
    'Your submission': 'आपकी प्रस्तुति',
    'Institution sign-in (SSO)': 'संस्थान साइन-इन (SSO)',
    'Members': 'सदस्य',
    'Language': 'भाषा',
    'Points': 'अंक',
    'Leaderboard — climb your course': 'लीडरबोर्ड — अपने कोर्स में आगे बढ़ें',
    'Discuss and solve problems with your class': 'अपनी कक्षा के साथ समस्याओं पर चर्चा करें और हल करें',
    'Linked practice problems to sharpen your skills': 'आपके कौशल को निखारने के लिए अभ्यास प्रश्न',
    'Finish each course with a hands-on mini-project': 'हर कोर्स को एक व्यावहारिक मिनी-प्रोजेक्ट के साथ पूरा करें',
    'Instructor-created tests and quizzes': 'प्रशिक्षक द्वारा बनाए गए टेस्ट और क्विज़',
    'Build and publish your own video course': 'अपना खुद का वीडियो कोर्स बनाएं और प्रकाशित करें',
    'Sign your whole institution in with one code': 'एक कोड से अपने पूरे संस्थान को साइन इन करें',
  },
};

export function getLang() {
  try { return localStorage.getItem(KEY) || 'en'; } catch { return 'en'; }
}
export function setLang(l) {
  try { localStorage.setItem(KEY, l in LANGS ? l : 'en'); } catch { /* ignore */ }
}
export function t(s) {
  const l = getLang();
  if (l === 'en') return s;
  return (DICT[l] && DICT[l][s]) || s;
}
export const languages = LANGS;

/** A compact language <select>; call onChange to re-render the view. */
export function langPicker(onChange) {
  const cur = getLang();
  const sel = document.createElement('select');
  sel.className = 'input';
  sel.style.width = 'auto';
  sel.title = t('Language');
  sel.innerHTML = Object.entries(LANGS).map(([k, v]) => `<option value="${k}" ${k === cur ? 'selected' : ''}>${v}</option>`).join('');
  sel.addEventListener('change', () => { setLang(sel.value); onChange?.(); });
  return sel;
}
