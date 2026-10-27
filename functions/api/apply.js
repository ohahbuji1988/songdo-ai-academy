// Cloudflare Pages Function: /api/apply
// Sends instant Telegram Push Notification upon application submission

export async function onRequestPost(context) {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  try {
    const data = await context.request.json();
    const name = (data.name || '').trim();
    const phone = (data.phone || '').trim();
    const track = (data.track || 'regular').trim();
    const note = (data.note || '').trim();

    if (!name || !phone) {
      return new Response(JSON.stringify({ success: false, error: '성함과 휴대폰 번호는 필수 입력 항목입니다.' }), {
        status: 400,
        headers: corsHeaders
      });
    }

    const botToken = (context.env && context.env.TELEGRAM_BOT_TOKEN) || '9208715626:AAFw_jfMSF4utz0hPXxx7awX438fp24D8Ww';
    const chatId = (context.env && context.env.TELEGRAM_CHAT_ID) || '639973681';

    if (botToken && chatId) {
      const kstTime = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });
      const messageText = 
`🔔 <b>[송도 AI 아카데미] 새 무료 수강 신청!</b>

👤 <b>신청자 성함:</b> ${name}
📞 <b>연락처:</b> ${phone}
🎯 <b>신청 트랙:</b> ${track}
📝 <b>희망 내용/질문:</b> ${note || '(없음)'}
⏰ <b>접수 일시:</b> ${kstTime}

👉 확인 후 수강생에게 안내 연락을 진행해 주세요!`;

      await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text: messageText,
          parse_mode: 'HTML'
        })
      });
    }

    return new Response(JSON.stringify({ 
      success: true, 
      message: `${name}님의 무료 수강 신청이 정상 접수되었습니다!` 
    }), {
      status: 200,
      headers: corsHeaders
    });

  } catch (err) {
    return new Response(JSON.stringify({ 
      success: false, 
      error: '신청 처리 중 오류가 발생했습니다: ' + err.message 
    }), {
      status: 500,
      headers: corsHeaders
    });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  });
}
