# Agendar no YouTube Studio (Chrome do usuário, canal BRUNOBLOX)

Pedir para rodar o lote da semana é a autorização para agendar **aquele** lote no BRUNOBLOX (@eibrunoruan). Use o
Chrome do usuário (ferramentas `mcp__claude-in-chrome__*`), já logado na conta Google dele. Nunca digite senha: se
pedir login ou verificação, pare e peça para ele entrar. Nada vai para o canal BRUNOBLOX ESP (abandonado).

`python scripts/lote.py agenda LOTE` gera `agenda.json`: um vídeo por dia às **09:00** (Brasília) a partir de
amanhã (lote de 7 → os próximos 7 dias; se houver mais vídeos, segue nos dias seguintes), cada item com `video`,
`titulo`, `descricao`, `tags`, `data_studio` (dd/mm/aaaa) e `hora_studio`. Mostre a tabela ao usuário.

O Studio do usuário está em inglês (Create, Upload videos, Show more, Next, Schedule, Got it, Close, Time zone). O
idioma do vídeo (Portuguese (Brazil)) e a categoria (Gaming) já são o padrão do canal: não precisa mexer. Thumbnail
também não: o dono coloca depois.

## Antes de começar
1. Abra `https://studio.youtube.com`. Confira o canal ativo (nome no menu lateral). Se não for o **BRUNOBLOX
   (@eibrunoruan)**, troque em avatar → **Switch account** → BRUNOBLOX (a mesma conta Google também tem o BRUNOBLOX
   ESP: não use).
2. Os vídeos têm 20–45 MB e a ferramenta `file_upload` só aceita até 10 MB. Suba o servidor local do lote em segundo
   plano: `python scripts/servidor_envio.py LOTE` (só 127.0.0.1:8768, só responde ao Studio). Ele entrega
   `/video/NN` (o MP4), `/meta/NN` (título, descrição, tags, data e hora da agenda) e `/ping`.
3. No primeiro `fetch` o Chrome pergunta se o studio.youtube.com pode acessar a rede local. **Quem aceita é o
   usuário** (não clique por ele): avise e espere ele dizer que aceitou. Se ele recusar, pare e explique; não tente
   contornar.

## Para cada vídeo (status `pendente` na agenda)
Um vídeo por vez, nesta ordem. Os passos com JavaScript rodam na aba do Studio (`javascript_tool`).

1. **Envio, título, descrição, público e "Show more"** (troque `NN`):
   ```js
   const espera = ms => new Promise(r => setTimeout(r, ms)); const N = 'NN';
   const clicar = el => (el.querySelector('button') || el).click();
   for (const b of [...document.querySelectorAll('ytcp-button, button')].filter(b => /^close$/i.test((b.innerText || '').trim()) && b.offsetParent)) { clicar(b); await espera(500); }
   clicar([...document.querySelectorAll('ytcp-button')].find(b => /^create$/i.test((b.innerText || '').trim()) && b.offsetParent)); await espera(1200);
   [...document.querySelectorAll('tp-yt-paper-item')].find(i => /upload videos/i.test(i.innerText) && i.offsetParent).click(); await espera(2500);
   const m = await (await fetch('http://127.0.0.1:8768/meta/' + N)).json();
   const blob = await (await fetch('http://127.0.0.1:8768/video/' + N)).blob();
   const input = document.querySelector('ytcp-uploads-file-picker input[type=file][name=Filedata]');
   const dt = new DataTransfer(); dt.items.add(new File([blob], m.arquivo, {type: 'video/mp4'}));
   input.files = dt.files; input.dispatchEvent(new Event('change', {bubbles: true}));
   let t0 = Date.now(); while (!document.querySelector('ytcp-uploads-dialog #title-textarea #textbox') && Date.now() - t0 < 30000) await espera(500);
   await espera(6000);  // o Studio preenche o título com o nome do arquivo nesse intervalo; escreva depois
   const d = document.querySelector('ytcp-uploads-dialog');
   const preencher = (sel, texto) => { const c = d.querySelector(sel); c.focus(); document.execCommand('selectAll', false, null); document.execCommand('insertText', false, texto); c.dispatchEvent(new Event('input', {bubbles: true})); return c.innerText; };
   const tit = preencher('#title-textarea #textbox', m.titulo); await espera(500);
   const des = preencher('#description-textarea #textbox', m.descricao); await espera(500);
   const mais = [...d.querySelectorAll('ytcp-button, button')].find(b => /^show more$/i.test((b.innerText || '').trim()) && b.offsetParent);
   if (mais) { clicar(mais); await espera(1500); }
   const radios = {};
   for (const nome of ['VIDEO_MADE_FOR_KIDS_NOT_MFK', 'VIDEO_PAID_PRODUCT_PLACEMENT_NO', 'VIDEO_HAS_ALTERED_CONTENT_NO']) {
     const r = d.querySelector('[name=' + nome + ']'); if (r) { r.click(); await espera(400); } radios[nome] = r ? r.getAttribute('aria-checked') : 'nao achei'; }
   JSON.stringify({canal: (document.querySelector('ytcp-navigation-drawer #entity-name') || {}).innerText, tit, desLen: des.length, radios, tags: m.tags.join(', ')})
   ```
   Confira: canal BRUNOBLOX, título igual ao da agenda, os três rádios `true` (não é para crianças, sem promoção
   paga, sem conteúdo alterado/sintético: é animação de Roblox, sem pessoa real nem cena realista).
2. **Tags**: `find` "Tags input" → `left_click` pela `ref` → confirme por JavaScript que `document.activeElement` tem
   `aria-label="Tags"` → `computer type` com as tags separadas por vírgula **e uma vírgula no fim** (vira o último
   chip). Confira por JavaScript: 17 chips (`ytcp-chip, ytcp-free-text-chip` dentro do diálogo), campo de tag vazio
   e o título ainda certo. Se o foco pular para o título enquanto o envio processa, as tags caem no título: restaure
   com `preencher('#title-textarea #textbox', m.titulo)`, clique de novo no campo de tags e digite outra vez.
3. **Next ×3 e abrir a data**:
   ```js
   const espera = ms => new Promise(r => setTimeout(r, ms)); const d = document.querySelector('ytcp-uploads-dialog');
   for (let i = 0; i < 3; i++) { d.querySelector('#next-button').click(); await espera(1800); }
   d.querySelector('#second-container-expand-button').click(); await espera(1500);   // Schedule
   d.querySelector('#datepicker-trigger').click(); await espera(1500);
   const di = [...document.querySelectorAll('input')].find(i => i.offsetParent && /^\d{1,2} \w{3} \d{4}$/.test(i.value));
   di.focus(); di.select(); di.value
   ```
4. **Data**: `computer type` "21 Oct 2026" (dia, mês em inglês abreviado, ano) e `key` Return.
5. **Fuso, hora e Schedule** (troque a data esperada):
   ```js
   const espera = ms => new Promise(r => setTimeout(r, ms)); const d = document.querySelector('ytcp-uploads-dialog');
   const tz = [...d.querySelectorAll('ytcp-button')].find(b => /^time zone$/i.test((b.innerText || '').trim()) && b.offsetParent);
   if (tz) { (tz.querySelector('button') || tz).click(); await espera(1000);
     const op = [...document.querySelectorAll('tp-yt-paper-item, [role=option]')].find(i => /\(GMT-0300\) Local Time/.test(i.innerText) && i.offsetParent);
     if (op) op.click(); await espera(900); }
   const hi = [...d.querySelectorAll('input')].find(i => /^\d\d:\d\d$/.test(i.value));
   hi.click(); hi.focus(); await espera(1200);
   const op9 = [...document.querySelectorAll('tp-yt-paper-item, [role=option]')].find(i => i.offsetParent && i.innerText.trim() === '09:00');
   if (op9) { op9.scrollIntoView({block: 'center'}); op9.click(); await espera(1000); }
   const estado = {data: d.querySelector('#datepicker-trigger').innerText.trim(), hora: hi.value,
     fuso: [...d.querySelectorAll('ytcp-dropdown-trigger, ytcp-text-dropdown-trigger')].map(x => x.innerText.trim()).find(t => /GMT/.test(t))};
   const res = {estado};
   if (estado.data === '21 Oct 2026' && estado.hora === '09:00' && /GMT-0300/.test(estado.fuso || '') && op9) {
     d.querySelector('#done-button').click(); await espera(4500);   // botão "Schedule"
     const ok = [...document.querySelectorAll('ytcp-button, button')].find(b => /^got it$/i.test((b.innerText || '').trim()) && b.offsetParent);
     if (ok) { (ok.querySelector('button') || ok).click(); await espera(3000); }   // "We're still checking your content"
     const sd = [...document.querySelectorAll('ytcp-video-share-dialog')].find(x => x.offsetParent);
     res.link = sd && [...sd.querySelectorAll('a')].map(a => a.href).find(h => /shorts\//.test(h));
     res.confirmacao = sd && sd.innerText.replace(/\s+/g, ' ').slice(0, 160); }
   JSON.stringify(res)
   ```
   **A hora tem que ser escolhida clicando na opção "09:00" da lista** (96 opções, de 15 em 15 minutos). Digitar
   "09:00" mostra 09:00 no campo, mas o Studio salva 00:00; Enter no campo também escolhe 00:00.
6. **Confirme pela janela final**: "Your video will be set to public on 21 October 2026 at 09:00". Se a hora vier
   diferente, abra `https://studio.youtube.com/video/<ID>/edit` → Visibility → clique no campo de hora → opção
   09:00 → Time zone (GMT-0300) Local Time → Done → Save, e reabra a Visibility para conferir.
7. `python scripts/lote.py marcar LOTE <NN> agendado --link https://youtube.com/shorts/<ID>` (link sem
   `?feature=share`). Erro → `marcar ... erro` e siga para o próximo; no fim, relate os que falharam.

## No fim
- Lista de conteúdo (Content → Shorts): todos os vídeos do lote com **Scheduled** e a data certa. Abra um ou dois
  pela Visibility para conferir 09:00.
- `python scripts/lote.py status LOTE`, a lista de links e datas para o usuário, e pare o servidor de envio.

## Cuidados
- Um envio por vez; o próximo só começa depois da janela "Video scheduled".
- O Studio às vezes pede verificação de telefone para recursos avançados ou mostra "limite diário de envios": pare e
  avise o usuário (não tente contornar).
- Não aceite termos, não mude configurações do canal e não ative monetização sem o usuário pedir.

## Alternativa sem navegador (API do YouTube)
`scripts/youtube_api.py` envia e agenda pela YouTube Data API (`privacyStatus: private` + `publishAt`). Exige projeto
no Google Cloud com OAuth criado pelo próprio usuário, e projetos não verificados têm os envios travados como
privados até passarem na auditoria do Google. Use só se o usuário pedir.
