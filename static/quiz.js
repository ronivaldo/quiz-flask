let questions = [];
let total = 0;
let remaining = [];
let score = 0;
let currentIdx = null;

// DOM elements
const qText     = document.getElementById('question-text');
const answers   = document.getElementById('answers');
const nextBtn   = document.getElementById('next-btn');
const feedback  = document.getElementById('feedback');
const scoreEl   = document.getElementById('score');
const pctEl     = document.getElementById('percent');
const bar       = document.getElementById('progress-bar');

// Atualiza placar e barra
function updateStatus() {
  scoreEl.textContent = score;
  const pct = Math.round((score / total) * 100);
  pctEl.textContent = pct;
  bar.style.width = pct + '%';
}

// Toca bip
function playSound(type) {
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.value = type === 'correct' ? 440 : 220;
  osc.connect(ctx.destination);
  osc.start();
  setTimeout(() => { osc.stop(); ctx.close(); },
             type === 'correct' ? 150 : 400);
}

// Escolhe e renderiza próxima pergunta
function pickQuestion() {
  feedback.textContent = '';
  nextBtn.classList.add('hidden');
  answers.innerHTML = '';

  if (remaining.length === 0) {
    qText.textContent = '🎉 Parabéns! Você concluiu todas as perguntas.';
    return;
  }

  currentIdx = Math.floor(Math.random() * remaining.length);
  const q = remaining[currentIdx];
  qText.textContent = q.pergunta;

  q.respostas.forEach(resp => {
    const btn = document.createElement('button');
    btn.className = 'w-full text-left px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded';
    btn.textContent = resp;
    btn.onclick = () => handleAnswer(resp);
    answers.appendChild(btn);
  });
}

// Lógica ao clicar resposta
function handleAnswer(selected) {
  Array.from(answers.children).forEach(b => b.disabled = true);

  const q = remaining[currentIdx];
  const correta = q.correta;

  if (selected === correta) {
    score++;
    updateStatus();
    playSound('correct');
    feedback.className = 'mt-3 text-green-600 font-semibold';
    feedback.textContent = '✅ Correto!';
    remaining.splice(currentIdx, 1);
    setTimeout(pickQuestion, 2000);
  } else {
    playSound('error');
    feedback.className = 'mt-3 text-red-600 font-semibold';
    feedback.textContent = `❌ Errado! A resposta certa é: "${correta}".`;
    nextBtn.textContent = 'Próxima';
    nextBtn.classList.remove('hidden');
    nextBtn.onclick = () => pickQuestion();
  }
}

// Inicialização após fetch
fetch(`/api/quizzes/${quizId}/perguntas`)
  .then(res => res.json())
  .then(data => {
    questions = data;
    total = questions.length;
    remaining = [...questions];
    updateStatus();
    pickQuestion();
  })
  .catch(err => {
    qText.textContent = 'Erro ao carregar o quiz.';
    console.error(err);
  });
