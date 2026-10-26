/**
 * DEVIL'S ADVOCATE - Groq AI + Offline Engine
 */

const PUNCH_ROASTS = [
  {
    triggers: ['칼퇴', '퇴근', '집에 가', '야근'],
    headline: "응 내일 또 출근이야~ ㅋㅋㅋ",
    subtext: "2시간 일찍 누워있다고 인생 피는 거 아니다? 내일의 너한테 대출 땡겨 쓴 거야."
  },
  {
    triggers: ['다이어트', '내일부터', '운동', '살', '치킨'],
    headline: "그 '내일' 3년째 안 오는 중",
    subtext: "달력에 13월 32일 생기면 그때 빼든가~ 일단 입에 든 탄수화물부터 삼키고 말해."
  },
  {
    triggers: ['방향을 잃었어', '방향', '길을 잃', '막막', '불안'],
    headline: "방향이 아니라 의지를 잃은 거겠지",
    subtext: "그냥 침대에서 뒹굴고 싶은 걸 무슨 비운의 철학자 주인공처럼 포장하고 있냐 ㅋㅋㅋ"
  },
  {
    triggers: ['주식', '코인', '존버', '떡상', '물렸'],
    headline: "한강 물 아직 안 차갑냐?",
    subtext: "세력들이 너 같은 호구 덕분에 오늘 밤 소고기 회식한대. 존버가 아니라 감금이야 그거."
  },
  {
    triggers: ['ai', '인공지능', 'chatgpt', '망함', '개발자'],
    headline: "AI보다 네 게으름이 널 먼저 망침",
    subtext: "남들은 AI 굴려서 장난감 만들 때 혼자 방구석에서 뉴스 보며 덜덜 떠는 중 ㅋㅋㅋ"
  },
  {
    triggers: ['공부', '강의', '책 샀', '독서'],
    headline: "완강률 0%에 내 전 재산 건다",
    subtext: "결제 버튼 누르는 순간 뇌가 '공부 끝났다'고 착각하는 병 완치 불가임."
  },
  {
    triggers: ['연애', '솔로', '소개팅', '외로'],
    headline: "안 생기는 데는 과학적인 이유가 있어",
    subtext: "상대방 눈에도 너는 '피해야 할 지뢰'로 보일 텐데 왜 자꾸 인연 탓을 하냐?"
  },
  {
    triggers: ['침대', '쉬고', '귀찮', '피곤'],
    headline: "하루 종일 폰만 봐놓고 뭐가 피곤해?",
    subtext: "손가락 스크롤만 3만 번 굴려서 엄지손가락만 피곤한 거겠지 ㅋㅋㅋ"
  }
];

function generateDynamicPunch(input) {
  const text = input.trim();
  
  if (text.endsWith('?') || text.endsWith('까')) {
    return {
      headline: "답 정해놓고 왜 물어보냐?",
      subtext: "어차피 내가 뭐라 하든 네 듣고 싶은 말만 골라 들을 거 다 안다 ㅋㅋㅋ"
    };
  }
  
  if (text.length < 8) {
    return {
      headline: `"${text}"... 이걸 글이라고 썼냐?`,
      subtext: "생각도 문장 길이만큼이나 성의 없고 짧아서 참 보기 좋다~"
    };
  }

  return {
    headline: "말은 참 그럴듯하게 잘해~",
    subtext: "스스로는 되게 똑똑한 줄 알겠지만 남들이 보면 전형적인 정신승리 핑계 1등이야."
  };
}

async function callBackendGroqRoast(userInput) {
  const endpoint = window.location.protocol.startsWith('http') 
    ? '/api/roast' 
    : 'http://127.0.0.1:3000/api/roast';

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: userInput })
  });

  const data = await response.json();
  if (!response.ok || data.error) {
    throw new Error(data.error || "Groq 호출 실패");
  }

  return data;
}

window.DevilApp = {
  activeMode: 'live', // Default to live AI since user has Groq!
  isProcessing: false,
  lastResult: null,

  init() {
    this.bindEvents();
    // Highlight default mode
    this.setMode('live');
  },

  setMode(mode) {
    this.activeMode = mode;
    const presetBtn = document.getElementById('modePreset');
    const liveBtn = document.getElementById('modeLive');
    if (mode === 'live') {
      liveBtn.classList.add('bg-white', 'text-black');
      liveBtn.classList.remove('text-textDim');
      presetBtn.classList.remove('bg-white', 'text-black');
      presetBtn.classList.add('text-textDim');
    } else {
      presetBtn.classList.add('bg-white', 'text-black');
      presetBtn.classList.remove('text-textDim');
      liveBtn.classList.remove('bg-white', 'text-black');
      liveBtn.classList.add('text-textDim');
    }
  },

  bindEvents() {
    const form = document.getElementById('roastForm');
    const input = document.getElementById('userInput');
    const pills = document.querySelectorAll('.prompt-pill');

    form?.addEventListener('submit', (e) => {
      e.preventDefault();
      this.process(input.value);
    });

    pills.forEach(pill => {
      pill.addEventListener('click', () => {
        const text = pill.getAttribute('data-text') || pill.textContent.trim();
        input.value = text;
        this.process(text);
      });
    });

    // Mode Toggle
    document.getElementById('modePreset')?.addEventListener('click', () => this.setMode('preset'));
    document.getElementById('modeLive')?.addEventListener('click', () => this.setMode('live'));

    document.getElementById('copyCardBtn')?.addEventListener('click', () => {
      this.copyShare();
    });
  },

  async process(text) {
    if (!text || !text.trim() || this.isProcessing) return;
    const clean = text.trim();
    this.isProcessing = true;
    this.setLoading(true);

    let result = null;

    try {
      if (this.activeMode === 'live') {
        result = await callBackendGroqRoast(clean);
      } else {
        const matched = PUNCH_ROASTS.find(r => 
          r.triggers.some(t => clean.toLowerCase().includes(t.toLowerCase()))
        );
        await new Promise(r => setTimeout(r, 200));
        result = matched || generateDynamicPunch(clean);
      }

      this.lastResult = { ...result, query: clean };
      this.render(result);
    } catch (err) {
      console.warn("Live API Error:", err.message);
      // Fallback with friendly toast notice
      result = generateDynamicPunch(clean);
      this.lastResult = { ...result, query: clean };
      this.render(result);
      this.showToast(err.message || ".env의 GROQ_API_KEY를 확인해주세요!");
    } finally {
      this.isProcessing = false;
      this.setLoading(false);
    }
  },

  setLoading(isLoading) {
    const btn = document.getElementById('submitBtn');
    const label = document.getElementById('submitLabel');
    if (isLoading) {
      btn.disabled = true;
      label.textContent = "긁는 중...";
    } else {
      btn.disabled = false;
      label.textContent = "시비 걸기";
    }
  },

  render(data) {
    const stage = document.getElementById('verdictStage');
    const empty = document.getElementById('emptyState');
    
    empty?.classList.add('hidden');
    stage?.classList.remove('hidden');

    document.getElementById('headlineText').textContent = data.headline;
    document.getElementById('subtextText').textContent = data.subtext;

    stage?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  },

  copyShare() {
    if (!this.lastResult) return;
    const { query, headline, subtext } = this.lastResult;
    const share = `[악마의 변호인에게 뼈맞음]\n\n나: "${query}"\n\n😈 "${headline}"\n→ ${subtext}\n\n👉 https://devils-advocate.app`;

    navigator.clipboard.writeText(share).then(() => {
      this.showToast("복사 완료! 친구한테 보내봐 ㅋㅋㅋ");
    });
  },

  showToast(msg) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.remove('hidden');
    toast.classList.add('toast-slide');
    setTimeout(() => {
      toast.classList.add('hidden');
      toast.classList.remove('toast-slide');
    }, 2800);
  }
};

document.addEventListener('DOMContentLoaded', () => {
  window.DevilApp.init();
});
