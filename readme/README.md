# Documentacao Complementar

Esta pasta concentra referencias tecnicas genericas que nao pertencem a uma
base especifica.

Use como fonte principal:

- `README.md`: visao geral do projeto, fluxo de execucao, versionamento,
  bronze/silver, metadados XML, SLD no silver e comandos principais.
- `docs/sdd/README.md`: fluxo Spec-Driven Development.
- `docs/sdd/spec-template.md`: template para especificar novas bases.
- `docs/sdd/specs/`: especificacoes por projeto/base.
- `readme/rules.md`: contrato generico dos perfis modulares em `rules/`.

Evite documentar regras especificas de uma base nesta pasta. Regras de uma base
devem ficar em `docs/sdd/specs/<projeto>.md`, para nao misturar contrato geral
com comportamento especifico.
