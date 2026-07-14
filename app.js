const scenarios = {
  model: {
    title: 'A new model improves reasoning but changes tool-call behavior.',
    decision: 'CANARY',
    tone: 'canary',
    rows: [
      ['Customer promise', 'Same outcome', 'Preserve'],
      ['Tool authority', 'Call pattern changed', 'Re-evaluate'],
      ['Human authority', 'Escalation unchanged', 'Verify'],
      ['Evaluation suite', 'Regression set required', 'Expand'],
      ['Economics', 'Token cost uncertain', 'Budget'],
      ['Release owner', 'One governed change', 'Canary']
    ],
    summary: ['Controlled exposure', 'Behavior-level regression', 'Rollback before broad release']
  },
  voice: {
    title: 'Voice introduces interruption, identity, and handoff behavior.',
    decision: 'HOLD',
    tone: 'hold',
    rows: [
      ['Customer promise', 'Faster assistance', 'Define'],
      ['Tool authority', 'Actions by voice', 'Constrain'],
      ['Human authority', 'Warm transfer needed', 'Design'],
      ['Evaluation suite', 'Turn-taking + consent', 'Add'],
      ['Economics', 'Latency budget tighter', 'Model'],
      ['Release owner', 'Cross-channel decision', 'Hold']
    ],
    summary: ['Do not copy chat behavior', 'Prove safe handoff', 'Launch one bounded journey']
  },
  policy: {
    title: 'A policy change affects responses in multiple customer journeys.',
    decision: 'SHIP',
    tone: 'ready',
    rows: [
      ['Customer promise', 'Accurate guidance', 'Preserve'],
      ['Tool authority', 'No capability change', 'Confirm'],
      ['Human authority', 'Exception path updated', 'Align'],
      ['Evaluation suite', 'Policy cases versioned', 'Run'],
      ['Economics', 'No material change', 'Monitor'],
      ['Release owner', 'Single change set', 'Ship']
    ],
    summary: ['One source of truth', 'Traceable coverage', 'Consistent deployment']
  },
  failure: {
    title: 'A downstream tool is unavailable during a high-intent interaction.',
    decision: 'HUMAN-FIRST',
    tone: 'human',
    rows: [
      ['Customer promise', 'No false completion', 'Protect'],
      ['Tool authority', 'Tool unavailable', 'Disable'],
      ['Human authority', 'Escalate with context', 'Activate'],
      ['Evaluation suite', 'Failure recovery cases', 'Run'],
      ['Economics', 'Avoid retry loops', 'Cap'],
      ['Release owner', 'Incident mode', 'Human-first']
    ],
    summary: ['State limits plainly', 'Preserve customer context', 'Learn from the exception']
  }
};

const decisionColors = {
  canary: ['#fff1d9', '#794400'],
  hold: ['#feeceb', '#8f1913'],
  ready: ['#e7f7ef', '#115c40'],
  human: ['#efedff', '#37307d']
};

function renderScenario(key) {
  const data = scenarios[key];
  if (!data) return;
  document.querySelectorAll('.scenario-button').forEach(button => {
    const selected = button.dataset.scenario === key;
    button.setAttribute('aria-selected', String(selected));
    button.tabIndex = selected ? 0 : -1;
  });
  const title = document.querySelector('[data-lab-title]');
  const badge = document.querySelector('[data-decision]');
  const table = document.querySelector('[data-diff-table]');
  const summary = document.querySelector('[data-output-summary]');
  title.textContent = data.title;
  badge.textContent = data.decision;
  badge.style.background = decisionColors[data.tone][0];
  badge.style.color = decisionColors[data.tone][1];
  table.innerHTML = '<div class="head">Manifest field</div><div class="head">Observed change</div><div class="head">Product response</div>' +
    data.rows.map(row => row.map((cell, index) => `<div class="${index === 2 ? 'risk' : ''}">${cell}</div>`).join('')).join('');
  summary.innerHTML = data.summary.map((item, index) => `<div><strong>${['Release posture','Required evidence','Customer protection'][index]}</strong><span>${item}</span></div>`).join('');
  const output = document.querySelector('.lab-output');
  output.animate([{opacity:.55, transform:'translateY(5px)'},{opacity:1, transform:'translateY(0)'}], {duration:260, easing:'ease-out'});
}

document.addEventListener('DOMContentLoaded', () => {
  const tabs = [...document.querySelectorAll('.scenario-button')];
  tabs.forEach((button, index) => {
    button.addEventListener('click', () => renderScenario(button.dataset.scenario));
    button.addEventListener('keydown', event => {
      const keys = ['ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp', 'Home', 'End'];
      if (!keys.includes(event.key)) return;
      event.preventDefault();
      let next = index;
      if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index - 1 + tabs.length) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      tabs[next].focus();
      renderScenario(tabs[next].dataset.scenario);
    });
  });
  const reset = document.querySelector('[data-reset]');
  if (reset) reset.addEventListener('click', () => renderScenario('model'));
  renderScenario('model');
});
