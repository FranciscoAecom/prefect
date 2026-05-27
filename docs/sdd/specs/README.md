# Specs Existentes

Esta pasta guarda as especificacoes SDD das bases e familias de bases do
pipeline.

## Padrao

Todas as specs devem seguir a ordem de secoes definida em
`docs/sdd/spec-template.md`. Quando uma secao nao se aplicar a uma base, manter
a secao e registrar `nao aplicavel`, `nao configurado` ou `nenhum`.

## Baselines

- `app_car.md`
- `reserva_legal_car.md`
- `sa_car.md`
- `ur_car.md`
- `estado.md`
- `localidades.md`
- `autorizacao_para_supressao_vegetal-auth_supn.md`
- `autos_infracao.md`
- `default.md`

As specs de baseline descrevem o comportamento atual do repositorio. Quando uma
regra de negocio ficar mais detalhada, atualize a spec antes de alterar o
codigo.
