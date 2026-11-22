# Operação — plano de mentoria

Uma frente por arquivo, cada uma com a ordem exata de execução. Regra de ouro: **uma frente rodando
sozinha antes de abrir a próxima.** Ordem de prioridade (maior retorno por hora investida primeiro):

| # | Frente | Por quê agora | Arquivo |
|---|---|---|---|
| 1 | YouTube GTA 6 | GTA 6 acabou de lançar (19/11/2026): é a janela de maior busca da história da franquia. Automação já montada. | `youtube-gta6/` |
| 2 | Despachante | Gera caixa direto; automação de atendimento e prazos libera seu tempo. | `despachante.md` |
| 3 | Achadinhos (TikTok Shop) | Skill de roteiro e TikTok no Metricool já existem; reaproveita a mesma máquina de vídeo. | `achadinhos-tiktok.md` |
| 4 | Mercado Livre | Sem conector ainda; começa como afiliado/link na bio dos vídeos, depois API. | `mercado-livre.md` |

## Ferramentas: o que fica e o que sai

**Fica (estratégico):** Gmail, Google Calendar, Google Drive, Metricool, vidIQ, TikTok for Business,
n8n (Despachante), Canva, rea-video, watch, skill `roteiro-achadinhos`, skill `madrugada-gta6`.

**Sob demanda:** Kling (pago por vídeo — só para vídeos já aprovados que precisem de cena de IA),
Gamma, Claude Docs, Montage, Windsor.ai **ou** Supermetrics (escolha um só).

**Pode desconectar:** OpusClip (exige plano Pro), LunarCrush (cripto), Higgsfield (não gera por aqui),
HyperFrames (não gera pelo Claude Code). ECC: **desativado** no projeto (custa ~50 mil tokens por
sessão); reative com `claude plugin enable ecc@ecc` quando for programar.

## Rotina diária
- **03:00** — tarefa agendada roda a skill `madrugada-gta6` (pesquisa → roteiros → vídeos).
- **07:00** — e-mail "Pacote GTA 6 do dia" com 3 Shorts anexados. Você aprova.
- **12:00 / 18:30 / 21:00** — publicar os aprovados (manual até conectar o YouTube ao Metricool).
- **Domingo** — 15 min olhando o que performou; ajustar horários e temas no `config.json`.
