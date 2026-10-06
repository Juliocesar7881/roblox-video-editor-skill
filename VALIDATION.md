# Validação antes da publicação

Em 6 de outubro de 2026, os scripts foram executados localmente com FFmpeg 7.1 e Python 3.12. Os testes usaram vídeos sintéticos, não gameplay real.

- Decodificação completa e verificação SHA-256 dos **185 áudios**: passou. A biblioteca completa está incluída no repositório/pacote; 78 áudios têm origem/licença comercial verificada e 107 arquivos fornecidos permanecem com licença pendente.
- Exportação de um longo 1920×1080 e dois Shorts 1080×1920, com legendas, zoom, PNG sobreposto, música, SFX e ducking: passou.
- Mixagem final dos testes 1080p próxima de −14 LUFS, com true peak abaixo de −1.5 dBTP: passou.
- Exportação de fonte **2560×1440 a 60 FPS** em longo 2560×1440 e dois Shorts 1440×2560, preservando 60 FPS: passou.
- Tentativas de reduzir 1440p para 1080p ou mudar 60 para 30 FPS na exportação final: rejeitadas.
- Cálculo de dimensões nativas 720p, 1080p, 1440p e 4K: passou. Não foi feita renderização integral de gameplay 4K.
- Fonte sem áudio, muting, enquadramento por clipe, crédito da música usada e decodificação completa dos MP4: passou.
- Efeito ou música fornecida sem licença comprovada em exportação comercial: rejeitados. Modo de prévia com marcação: passou.
- Histórico musical e preferência por composições não usadas recentemente: passou.
- Download real de música do autor, extração do trecho, cópia de SFX e nova execução aproveitando o cache: passou.
- Instalação portátil, formato SKILL.md e testes públicos de política: verificados antes da publicação.
- Instalação do pacote completo com os 185 arquivos e preparo da biblioteca com acesso à rede bloqueado: passou; nenhuma música adicional precisou ser baixada.

Quadros exportados foram inspecionados para legibilidade, enquadramento vertical e sobreposições. Não foi feita revisão auditiva integral nem teste de invocação dentro do Claude. Qualidade editorial, seleção dos melhores momentos e revisão final precisam ser verificadas na primeira gameplay real.
