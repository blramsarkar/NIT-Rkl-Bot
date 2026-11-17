/* ==============================================================================
 * File: widget/nitrkl-bot-widget.js
 * Role: Embeddable Vanilla JavaScript Floating Chat Widget
 * Purpose: Floating chat for nitrkl.ac.in. Talks ONLY to the bot backend (no API
 *          keys here). Features: streaming answers, clickable official source
 *          links, quick-suggestion chips, English / Hindi / Odia, thumbs up/down
 *          feedback, privacy notice, per-user quota display.
 * Security: bot text is rendered by building DOM nodes (textContent), never via
 *          innerHTML; links are only made clickable for allowlisted domains.
 * Config:  window.NITRKL_BOT_API_URL or <script data-api-url="https://bot.../chat">
 * ============================================================================== */

(function () {
  'use strict';

  const currentScript = document.currentScript || (function () {
    const scripts = document.getElementsByTagName('script');
    return scripts[scripts.length - 1];
  })();
  const scriptApiUrl = currentScript ? currentScript.getAttribute('data-api-url') : null;
  const apiEndpoint = (window.NITRKL_BOT_API_URL || scriptApiUrl || '/chat').replace(/\/+$/, '');
  const apiBase = apiEndpoint.replace(/\/chat$/, '');

  const CONFIG = {
    chatUrl: apiEndpoint,
    streamUrl: apiEndpoint + '/stream',
    feedbackUrl: apiBase + '/feedback',
    maxChars: 500,
    maxQuestions: 15,
    // Links in answers are clickable only for these domains (and their subdomains).
    linkDomains: ['nitrkl.ac.in', 'josaa.nic.in', 'csab.nic.in', 'ccmt.admissions.nic.in'],
  };

  const I18N = {
    en: {
      name: 'English',
      subtitle: 'Official Campus Assistant',
      greeting: 'Hello! I am NIT RKL Bot, the official assistant for NIT Rourkela. How can I help you today?',
      placeholder: 'Ask about admissions, exams, fees, hostels…',
      privacy: 'Please don\'t share personal details (roll number, phone, Aadhaar). Answers can be wrong — check the source link.',
      left: (n) => `${n} questions left`,
      sources: 'Sources:',
      helpful: 'Helpful', notHelpful: 'Not helpful',
      thanks: 'Thanks for the feedback!',
      whatWrong: 'What was wrong? (optional)', send: 'Send',
      limit: 'Question limit reached. Please wait a few minutes.',
      error: 'Sorry, the assistant is unavailable right now. Please try again later or visit https://www.nitrkl.ac.in',
      tooLong: (n) => `Please keep your question under ${n} characters.`,
    },
    hi: {
      name: 'हिंदी',
      subtitle: 'आधिकारिक परिसर सहायक',
      greeting: 'नमस्ते! मैं NIT RKL Bot हूँ, NIT राउरकेला का आधिकारिक सहायक। मैं आपकी क्या मदद कर सकता हूँ?',
      placeholder: 'प्रवेश, परीक्षा, शुल्क, छात्रावास के बारे में पूछें…',
      privacy: 'कृपया व्यक्तिगत जानकारी (रोल नंबर, फ़ोन, आधार) साझा न करें। उत्तर गलत हो सकते हैं — स्रोत लिंक अवश्य देखें।',
      left: (n) => `${n} प्रश्न शेष`,
      sources: 'स्रोत:',
      helpful: 'उपयोगी', notHelpful: 'उपयोगी नहीं',
      thanks: 'प्रतिक्रिया के लिए धन्यवाद!',
      whatWrong: 'क्या गलत था? (वैकल्पिक)', send: 'भेजें',
      limit: 'प्रश्नों की सीमा पूरी हो गई। कृपया कुछ मिनट प्रतीक्षा करें।',
      error: 'क्षमा करें, सहायक अभी उपलब्ध नहीं है। कृपया बाद में प्रयास करें या https://www.nitrkl.ac.in देखें',
      tooLong: (n) => `कृपया प्रश्न ${n} अक्षरों से छोटा रखें।`,
    },
    or: {
      name: 'ଓଡ଼ିଆ',
      subtitle: 'ଆଧିକାରିକ କ୍ୟାମ୍ପସ ସହାୟକ',
      greeting: 'ନମସ୍କାର! ମୁଁ NIT RKL Bot, NIT ରାଉରକେଲାର ଆଧିକାରିକ ସହାୟକ। ମୁଁ ଆପଣଙ୍କୁ କିପରି ସାହାଯ୍ୟ କରିପାରିବି?',
      placeholder: 'ନାମଲେଖା, ପରୀକ୍ଷା, ଫି, ହଷ୍ଟେଲ ବିଷୟରେ ପଚାରନ୍ତୁ…',
      privacy: 'ଦୟାକରି ବ୍ୟକ୍ତିଗତ ତଥ୍ୟ (ରୋଲ ନମ୍ବର, ଫୋନ, ଆଧାର) ଦିଅନ୍ତୁ ନାହିଁ। ଉତ୍ତର ଭୁଲ ହୋଇପାରେ — ଉତ୍ସ ଲିଙ୍କ ଯାଞ୍ଚ କରନ୍ତୁ।',
      left: (n) => `${n}ଟି ପ୍ରଶ୍ନ ବାକି`,
      sources: 'ଉତ୍ସ:',
      helpful: 'ଉପଯୋଗୀ', notHelpful: 'ଉପଯୋଗୀ ନୁହେଁ',
      thanks: 'ମତାମତ ପାଇଁ ଧନ୍ୟବାଦ!',
      whatWrong: 'କଣ ଭୁଲ ଥିଲା? (ଇଚ୍ଛାଧୀନ)', send: 'ପଠାନ୍ତୁ',
      limit: 'ପ୍ରଶ୍ନ ସୀମା ପୂରଣ ହୋଇଗଲା। ଦୟାକରି କିଛି ମିନିଟ ଅପେକ୍ଷା କରନ୍ତୁ।',
      error: 'କ୍ଷମା କରନ୍ତୁ, ସହାୟକ ବର୍ତ୍ତମାନ ଉପଲବ୍ଧ ନାହିଁ। ପରେ ଚେଷ୍ଟା କରନ୍ତୁ କିମ୍ବା https://www.nitrkl.ac.in ଦେଖନ୍ତୁ',
      tooLong: (n) => `ଦୟାକରି ପ୍ରଶ୍ନ ${n} ଅକ୍ଷରରୁ କମ ରଖନ୍ତୁ।`,
    },
  };

  // Chip label is localised; the query sent stays English (matches the knowledge base),
  // and the answer comes back in the selected language.
  const CHIPS = [
    { q: 'How do I apply for B.Tech admission?', en: 'Admissions', hi: 'प्रवेश', or: 'ନାମଲେଖା' },
    { q: 'When are the mid-semester exams?', en: 'Exam dates', hi: 'परीक्षा तिथियाँ', or: 'ପରୀକ୍ଷା ତାରିଖ' },
    { q: 'What are the tuition fee waiver rules?', en: 'Fees & waivers', hi: 'शुल्क व छूट', or: 'ଫି ଓ ଛାଡ' },
    { q: 'What are the hostel curfew timings?', en: 'Hostels', hi: 'छात्रावास', or: 'ହଷ୍ଟେଲ' },
    { q: 'Who is the HOD of Computer Science?', en: 'HOD of CSE', hi: 'CSE विभागाध्यक्ष', or: 'CSE ବିଭାଗମୁଖ୍ୟ' },
    { q: 'Show the latest notices', en: 'Latest notices', hi: 'नवीनतम सूचनाएँ', or: 'ସଦ୍ୟତମ ବିଜ୍ଞପ୍ତି' },
    { q: 'What is the minimum attendance required?', en: 'Attendance rule', hi: 'उपस्थिति नियम', or: 'ଉପସ୍ଥାନ ନିୟମ' },
    { q: 'Placement guidelines for students', en: 'Placements', hi: 'प्लेसमेंट', or: 'ପ୍ଲେସମେଣ୍ଟ' },
  ];

  function storageGet(key) { try { return window.localStorage.getItem(key); } catch (e) { return null; } }
  function storageSet(key, v) { try { window.localStorage.setItem(key, v); } catch (e) { /* ignore */ } }

  let lang = I18N[storageGet('nitrkl_bot_lang')] ? storageGet('nitrkl_bot_lang') : 'en';
  let isOpen = false;
  let isDark = false;
  let busy = false;
  let remaining = CONFIG.maxQuestions;
  const history = [];

  const t = (key, ...args) => {
    const v = (I18N[lang] && I18N[lang][key]) || I18N.en[key];
    return typeof v === 'function' ? v(...args) : v;
  };

  // ---------------------------------------------------------------- DOM helpers
  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([k, v]) => {
      if (k === 'class') node.className = v;
      else if (k === 'text') node.textContent = v;
      else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
      else node.setAttribute(k, v);
    });
    (children || []).forEach((c) => node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c));
    return node;
  }

  function safeUrl(raw) {
    try {
      const u = new URL(raw);
      if (u.protocol !== 'https:' && u.protocol !== 'http:') return null;
      const host = u.hostname.toLowerCase();
      const ok = CONFIG.linkDomains.some((d) => host === d || host.endsWith('.' + d));
      return ok ? u.href : null;
    } catch (e) {
      return null;
    }
  }

  function makeLink(text, url) {
    const href = safeUrl(url);
    if (!href) return document.createTextNode(text === url ? url : `${text} (${url})`);
    return el('a', { href, target: '_blank', rel: 'noopener noreferrer nofollow', text });
  }

  // Safe inline markdown -> DOM: **bold**, *italic*, `code`, [text](url), bare URLs.
  const TOKEN = /(\*\*[^*\n]+\*\*|\[[^\]\n]+\]\(https?:\/\/[^\s)]+\)|https?:\/\/[^\s<>()\]]+|\*[^*\s][^*\n]*\*|`[^`\n]+`)/g;

  function appendInline(parent, line) {
    let last = 0;
    String(line || '').replace(TOKEN, (match, _g, offset) => {
      if (offset > last) parent.appendChild(document.createTextNode(line.slice(last, offset)));
      if (match.startsWith('**')) {
        parent.appendChild(el('strong', { text: match.slice(2, -2) }));
      } else if (match.startsWith('[')) {
        const m = match.match(/^\[([^\]]+)\]\((.+)\)$/);
        if (m) parent.appendChild(makeLink(m[1], m[2]));
        else parent.appendChild(document.createTextNode(match));
      } else if (match.startsWith('http')) {
        const trimmed = match.replace(/[.,;:]+$/, '');
        parent.appendChild(makeLink(trimmed, trimmed));
        if (trimmed.length < match.length) parent.appendChild(document.createTextNode(match.slice(trimmed.length)));
      } else if (match.startsWith('`')) {
        parent.appendChild(el('code', { class: 'nitrkl-code', text: match.slice(1, -1) }));
      } else {
        parent.appendChild(el('em', { text: match.slice(1, -1) }));
      }
      last = offset + match.length;
      return match;
    });
    if (last < line.length) parent.appendChild(document.createTextNode(line.slice(last)));
  }

  function parseMarkdownBlocks(text) {
    const rawLines = String(text || '').replace(/\r\n/g, '\n').split('\n');
    const blocks = [];
    let i = 0;

    while (i < rawLines.length) {
      const line = rawLines[i];
      const trimmed = line.trim();

      if (!trimmed) {
        i++;
        continue;
      }

      // 1. Table Detection: starts & ends with '|' and contains inner '|'
      if (trimmed.startsWith('|') && trimmed.endsWith('|') && trimmed.includes('|', 1)) {
        const tableRows = [];
        while (i < rawLines.length && rawLines[i].trim().startsWith('|') && rawLines[i].trim().endsWith('|')) {
          const rowStr = rawLines[i].trim();
          // Skip divider row |---|---|
          if (!/^\|(\s*:?-+:?\s*\|)+$/.test(rowStr)) {
            const cells = rowStr.slice(1, -1).split('|').map((c) => c.trim());
            tableRows.push(cells);
          }
          i++;
        }
        if (tableRows.length > 0) {
          blocks.push({ type: 'table', headers: tableRows[0], rows: tableRows.slice(1) });
          continue;
        }
      }

      // 2. Heading Detection: # H1, ## H2, ### H3
      const headMatch = trimmed.match(/^(#{1,4})\s+(.+)$/);
      if (headMatch) {
        blocks.push({ type: 'heading', level: headMatch[1].length, text: headMatch[2] });
        i++;
        continue;
      }

      // 3. Bullet & Numbered List Detection: - item, * item, • item, 1. item
      if (/^(\s*[-*•]|\s*\d+\.)\s+/.test(line)) {
        const isNum = /^\s*\d+\./.test(line);
        const listItems = [];
        while (i < rawLines.length && /^(\s*[-*•]|\s*\d+\.)\s+/.test(rawLines[i])) {
          const itemText = rawLines[i].replace(/^(\s*[-*•]|\s*\d+\.)\s+/, '').trim();
          listItems.push(itemText);
          i++;
        }
        blocks.push({ type: 'list', ordered: isNum, items: listItems });
        continue;
      }

      // 4. Regular Paragraph Line
      blocks.push({ type: 'paragraph', text: line });
      i++;
    }

    return blocks;
  }

  function renderRich(container, text) {
    container.textContent = '';
    const blocks = parseMarkdownBlocks(text);

    blocks.forEach((block) => {
      if (block.type === 'heading') {
        const tag = block.level <= 2 ? 'h4' : 'h5';
        const h = el(tag, { class: 'nitrkl-heading' });
        appendInline(h, block.text);
        container.appendChild(h);
      } else if (block.type === 'list') {
        const listTag = block.ordered ? 'ol' : 'ul';
        const listEl = el(listTag, { class: 'nitrkl-list' });
        block.items.forEach((item) => {
          const li = el('li');
          appendInline(li, item);
          listEl.appendChild(li);
        });
        container.appendChild(listEl);
      } else if (block.type === 'table') {
        const table = el('table', { class: 'nitrkl-table' });
        if (block.headers && block.headers.length > 0) {
          const thead = el('thead');
          const tr = el('tr');
          block.headers.forEach((hText) => {
            const th = el('th');
            appendInline(th, hText);
            tr.appendChild(th);
          });
          thead.appendChild(tr);
          table.appendChild(thead);
        }
        if (block.rows && block.rows.length > 0) {
          const tbody = el('tbody');
          block.rows.forEach((row) => {
            const tr = el('tr');
            row.forEach((cellText) => {
              const td = el('td');
              appendInline(td, cellText);
              tr.appendChild(td);
            });
            tbody.appendChild(tr);
          });
          table.appendChild(tbody);
        }
        const tableWrapper = el('div', { class: 'nitrkl-table-wrap' }, [table]);
        container.appendChild(tableWrapper);
      } else if (block.type === 'paragraph') {
        const p = el('p', { class: 'nitrkl-p' });
        appendInline(p, block.text);
        container.appendChild(p);
      }
    });
  }

  // ---------------------------------------------------------------- UI
  let container, chatWindow, bodyEl, inputEl, sendBtn, quotaEl, privacyEl, subtitleEl, chipsEl, greetingEl;

  function initWidget() {
    container = el('div', { id: 'nitrkl-widget-container' });

    const langSelect = el('select', { class: 'nitrkl-lang', 'aria-label': 'Language', title: 'Language' });
    Object.keys(I18N).forEach((code) => {
      const opt = el('option', { value: code, text: I18N[code].name });
      if (code === lang) opt.selected = true;
      langSelect.appendChild(opt);
    });
    langSelect.addEventListener('change', () => { lang = langSelect.value; storageSet('nitrkl_bot_lang', lang); applyLanguage(); });

    const themeBtn = el('button', { class: 'nitrkl-icon-btn', title: 'Dark / light', type: 'button', text: '🌙' });
    themeBtn.addEventListener('click', () => {
      isDark = !isDark;
      chatWindow.classList.toggle('dark-theme', isDark);
      themeBtn.textContent = isDark ? '☀️' : '🌙';
    });
    const closeBtn = el('button', { class: 'nitrkl-icon-btn', title: 'Close', type: 'button', text: '✕', onclick: toggle });

    subtitleEl = el('span');
    quotaEl = el('span', { class: 'nitrkl-quota' });
    const header = el('div', { class: 'nitrkl-header' }, [
      el('div', { class: 'nitrkl-header-brand' }, [
        el('div', { class: 'nitrkl-avatar', text: 'NIT' }),
        el('div', {}, [
          el('h3', { class: 'nitrkl-header-title', text: 'NIT RKL Bot' }),
          el('p', { class: 'nitrkl-header-subtitle' }, [subtitleEl, ' • ', quotaEl]),
        ]),
      ]),
      el('div', { class: 'nitrkl-header-actions' }, [langSelect, themeBtn, closeBtn]),
    ]);

    greetingEl = el('div');
    chipsEl = el('div', { class: 'nitrkl-chips-container' });
    bodyEl = el('div', { class: 'nitrkl-body', id: 'nitrklChatBody', 'aria-live': 'polite' }, [
      el('div', { class: 'nitrkl-msg bot' }, [greetingEl, chipsEl]),
    ]);

    inputEl = el('input', { type: 'text', class: 'nitrkl-input', maxlength: String(CONFIG.maxChars), 'aria-label': 'Message' });
    inputEl.addEventListener('keydown', (e) => { if (e.key === 'Enter') handleSend(); });
    sendBtn = el('button', { class: 'nitrkl-send-btn', type: 'button', title: 'Send', 'aria-label': 'Send', onclick: () => handleSend() });
    sendBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>';
    privacyEl = el('div', { class: 'nitrkl-privacy' });

    chatWindow = el('div', { class: 'nitrkl-chat-window', id: 'nitrklChatWindow', role: 'dialog', 'aria-label': 'NIT RKL Bot' }, [
      header, bodyEl,
      el('div', { class: 'nitrkl-footer-wrap' }, [el('div', { class: 'nitrkl-footer' }, [inputEl, sendBtn]), privacyEl]),
    ]);

    const trigger = el('button', { class: 'nitrkl-trigger-btn', id: 'nitrklTriggerBtn', type: 'button', title: 'Chat with NIT RKL Bot', onclick: toggle });
    trigger.innerHTML = '<div class="nitrkl-badge-pulse"></div><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 9h12v2H6V9zm8 5H6v-2h8v2zm4-6H6V6h12v2z"/></svg>';

    container.appendChild(chatWindow);
    container.appendChild(trigger);
    document.body.appendChild(container);
    applyLanguage();
  }

  function applyLanguage() {
    subtitleEl.textContent = t('subtitle');
    greetingEl.textContent = t('greeting');
    inputEl.placeholder = t('placeholder');
    privacyEl.textContent = t('privacy');
    updateQuota();
    chipsEl.textContent = '';
    CHIPS.forEach((c) => {
      chipsEl.appendChild(el('button', {
        class: 'nitrkl-chip', type: 'button', text: c[lang] || c.en,
        onclick: () => handleSend(c.q),
      }));
    });
  }

  function updateQuota() {
    quotaEl.textContent = t('left', remaining);
    quotaEl.classList.toggle('low', remaining <= 3 && remaining > 0);
    quotaEl.classList.toggle('none', remaining <= 0);
  }

  function toggle() {
    isOpen = !isOpen;
    chatWindow.classList.toggle('nitrkl-open', isOpen);
    if (isOpen) inputEl.focus();
  }

  function scrollDown() { bodyEl.scrollTop = bodyEl.scrollHeight; }

  function addUserMessage(text) {
    bodyEl.appendChild(el('div', { class: 'nitrkl-msg user', text }));
    scrollDown();
  }

  function addBotMessage() {
    const textEl = el('div', { class: 'nitrkl-text' });
    const msg = el('div', { class: 'nitrkl-msg bot' }, [textEl]);
    bodyEl.appendChild(msg);
    scrollDown();
    return { msg, textEl };
  }

  function addTyping() {
    const node = el('div', { class: 'nitrkl-msg bot nitrkl-typing' });
    node.innerHTML = '<div class="nitrkl-typing-dots"><span></span><span></span><span></span></div>';
    bodyEl.appendChild(node);
    scrollDown();
    return node;
  }

  function renderSources(msg, sources) {
    if (!sources || !sources.length) return;
    const wrap = el('div', { class: 'nitrkl-sources' }, [el('strong', { text: t('sources') + ' ' })]);
    sources.forEach((s) => {
      const label = (s && s.ref) || '';
      const short = label.length > 40 ? label.slice(0, 37) + '…' : label;
      const href = s && s.url ? safeUrl(s.url) : null;
      wrap.appendChild(href
        ? el('a', { class: 'nitrkl-source-badge', href, target: '_blank', rel: 'noopener noreferrer', title: href, text: short })
        : el('span', { class: 'nitrkl-source-badge', text: short }));
    });
    msg.appendChild(wrap);
  }

  function renderFeedback(msg, logId) {
    if (!logId) return;
    const bar = el('div', { class: 'nitrkl-feedback' });
    const up = el('button', { type: 'button', class: 'nitrkl-fb-btn', title: t('helpful'), 'aria-label': t('helpful'), text: '👍' });
    const down = el('button', { type: 'button', class: 'nitrkl-fb-btn', title: t('notHelpful'), 'aria-label': t('notHelpful'), text: '👎' });
    const done = (note) => { bar.textContent = ''; bar.appendChild(el('span', { class: 'nitrkl-fb-thanks', text: note })); };

    up.addEventListener('click', () => { sendFeedback(logId, 1); done(t('thanks')); });
    down.addEventListener('click', () => {
      sendFeedback(logId, -1);
      bar.textContent = '';
      const box = el('input', { type: 'text', class: 'nitrkl-fb-input', maxlength: '300', placeholder: t('whatWrong') });
      const send = el('button', { type: 'button', class: 'nitrkl-fb-send', text: t('send') });
      const submit = () => { if (box.value.trim()) sendFeedback(logId, -1, box.value.trim()); done(t('thanks')); };
      send.addEventListener('click', submit);
      box.addEventListener('keydown', (e) => { if (e.key === 'Enter') submit(); });
      bar.appendChild(box); bar.appendChild(send);
      box.focus();
    });
    bar.appendChild(up); bar.appendChild(down);
    msg.appendChild(bar);
  }

  function sendFeedback(logId, rating, comment) {
    fetch(CONFIG.feedbackUrl, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ log_id: logId, rating, comment: comment || null }),
    }).catch(() => { /* feedback is best-effort */ });
  }

  function lockInput(reason) {
    inputEl.disabled = true;
    sendBtn.disabled = true;
    inputEl.placeholder = reason;
  }

  // ---------------------------------------------------------------- networking
  async function readStream(response, onDelta) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let final = null;
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let idx;
      while ((idx = buffer.indexOf('\n\n')) >= 0) {
        const chunk = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 2);
        const line = chunk.split('\n').find((l) => l.startsWith('data: '));
        if (!line) continue;
        let ev;
        try { ev = JSON.parse(line.slice(6)); } catch (e) { continue; }
        if (ev.type === 'delta') onDelta(ev.text || '', false);
        else if (ev.type === 'reset') onDelta('', true);
        else if (ev.type === 'final') final = ev;
        else if (ev.type === 'error') throw new Error(ev.detail || 'stream error');
      }
    }
    return final;
  }

  async function handleSend(preset) {
    const query = (preset || inputEl.value).trim();
    if (!query || busy) return;
    if (query.length > CONFIG.maxChars) { addBotMessage().textEl.textContent = t('tooLong', CONFIG.maxChars); return; }
    if (remaining <= 0) { addBotMessage().textEl.textContent = t('limit'); return; }

    busy = true;
    addUserMessage(query);
    inputEl.value = '';
    const typing = addTyping();
    const payload = JSON.stringify({ query, history: history.slice(-4), language: lang });
    const headers = { 'Content-Type': 'application/json' };

    let bot = null;
    let text = '';
    const onDelta = (piece, reset) => {
      if (!bot) { typing.remove(); bot = addBotMessage(); }
      text = reset ? '' : text + piece;
      bot.textEl.textContent = text; // plain text while streaming
      scrollDown();
    };

    try {
      let data = null;
      let response = await fetch(CONFIG.streamUrl, { method: 'POST', headers, body: payload });
      if (response.status === 404 || response.status === 405) {
        response = await fetch(CONFIG.chatUrl, { method: 'POST', headers, body: payload });
        if (response.ok) data = await response.json();
      } else if (response.ok && response.body) {
        data = await readStream(response, onDelta);
      }

      if (response.status === 429) {
        typing.remove();
        const err = await response.json().catch(() => null);
        addBotMessage().textEl.textContent = (err && err.detail) || t('limit');
        remaining = 0; updateQuota(); lockInput(t('limit'));
        return;
      }
      if (!response.ok || !data) throw new Error('HTTP ' + response.status);

      if (!bot) { typing.remove(); bot = addBotMessage(); }
      renderRich(bot.textEl, data.answer || text);
      renderSources(bot.msg, data.sources);
      renderFeedback(bot.msg, data.log_id);
      scrollDown();

      history.push({ role: 'user', content: query });
      history.push({ role: 'assistant', content: (data.answer || text).slice(0, 2000) });
      if (typeof data.questions_remaining === 'number') {
        remaining = data.questions_remaining; updateQuota();
        if (remaining <= 0) lockInput(t('limit'));
      }
    } catch (e) {
      console.error('NIT RKL Bot error:', e);
      typing.remove();
      if (bot) bot.msg.remove();
      renderRich(addBotMessage().textEl, t('error'));
    } finally {
      busy = false;
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initWidget);
  else initWidget();
})();
