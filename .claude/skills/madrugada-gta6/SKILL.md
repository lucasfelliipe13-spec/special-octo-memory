---
name: madrugada-gta6
description: Rotina da madrugada do canal de GTA 6. Pesquisa os temas que mais viralizaram nos concorrentes, faz engenharia reversa da estrutura, cria pautas, ganchos, roteiros, horários e gera os Shorts com o gerador grátis, e entrega tudo por e-mail para aprovação às 7h. Use quando a tarefa agendada da madrugada disparar ou quando pedirem "roda a madrugada do GTA 6".
---

# Madrugada GTA 6

Objetivo: às 07:00 (America/Sao_Paulo) o dono do canal abre o e-mail e encontra o pacote do dia
pronto, dependendo só da aprovação dele. **Nada é publicado sem aprovação.**

Arquivos: `operacao/youtube-gta6/config.json` (nicho, concorrentes, regras, horários),
`operacao/youtube-gta6/historico.md` (temas já usados — não repetir),
`operacao/youtube-gta6/gerador/gerar_video.py` (gerador grátis).

## Passo 0 — Preparar (2 min)
```bash
pip install -q "sherpa-onnx==1.12.40" numpy
```
O gerador baixa sozinho a voz pt-BR (GitHub, ~67 MB) na primeira execução.

## Passo 1 — Pesquisa (o que viralizou nas últimas 72 h)
1. `WebSearch` (mode standard) para cada termo de `busca_noturna` e para cada concorrente
   ("<concorrente> GTA 6 vídeo mais visto esta semana"). Some notícias de GTA 6 das últimas 24 h.
2. Se houver créditos no vidIQ (`vidiq_balance` > 20), use **no máximo 2** chamadas:
   `vidiq_outliers` ou `vidiq_youtube_search` (query "GTA 6", order viewCount, publishedAfter = 3 dias atrás).
   Sem créditos, siga só com WebSearch — não pare.
3. Monte uma lista de 10 temas candidatos com: tema, quem fez, sinal de viral (views, comentários,
   repetição entre canais), fonte (URL).

## Passo 2 — Engenharia reversa (estrutura, nunca o conteúdo)
Para os 5 melhores temas, descreva: tipo de gancho (curiosidade, polêmica, lista, "você não sabia"),
promessa, ritmo (frases por segundo), estrutura (gancho → prova → virada → CTA), duração, texto na tela.
Depois adapte ao canal: ângulo próprio, palavras próprias, exemplo próprio.
Descarte o tema se ele violar qualquer item de `regras_sem_restricao` ou já estiver no `historico.md`.

## Passo 3 — Pacote do dia (3 Shorts)
Para cada Short escolha 1 tema e escreva:
- **Título** (até 60 caracteres, com "GTA 6") e **2 alternativas**
- **Gancho falado** (primeiros 2 s) e **gancho na tela** (até 5 palavras, MAIÚSCULAS)
- **Roteiro** em 4–7 cenas curtas (fala + texto opcional na tela), 20–45 s no total, linguagem falada BR
- **Descrição** (2 linhas) + **5 hashtags** + **comentário fixado** que puxa conversa
- **Horário** de `horarios_sugeridos` (o mais forte para o tema mais forte)
- **Por que deve viralizar** (1 frase, citando o sinal e a fonte)

Salve cada roteiro como `saida/AAAA-MM-DD/shortN.json` no formato do `gerador/exemplo_roteiro.json`.

## Passo 4 — Gerar os vídeos (grátis)
```bash
cd operacao/youtube-gta6/gerador
python3 gerar_video.py ../saida/AAAA-MM-DD/short1.json ../saida/AAAA-MM-DD/short1.mp4
```
Repita para os 3. Confira com `ffprobe` que cada um tem vídeo 1080x1920 e áudio. Se um falhar, siga
com os outros e avise no e-mail.

## Passo 5 — Entregar por e-mail (Gmail `send_message`)
Envie **para o próprio dono** (endereço informado no prompt da tarefa agendada), em `htmlBody`, com os
3 MP4 anexados (total < 25 MB; se passar, suba no Google Drive e coloque o link):
- Resumo do dia em 3 linhas (o que está em alta e por quê)
- Para cada Short: horário, título + alternativas, gancho, roteiro, descrição, hashtags, comentário fixado,
  "por que deve viralizar", fonte
- Fechamento: "Responda APROVO 1, 2, 3 (ou o que quiser mudar)". Publicação continua manual até o
  YouTube ser conectado ao Metricool.

Não envie para mais ninguém. Não publique nada.

## Passo 6 — Memória
Acrescente os 3 temas usados ao `operacao/youtube-gta6/historico.md` (data + tema + título), faça commit
**só do histórico e dos JSON** (nunca dos MP4) e `git push -u origin madrugada`.
