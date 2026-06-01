# Specs Existentes

Esta pasta guarda as especificacoes SDD das bases e familias de bases do
pipeline.

## Padrao

Todas as specs devem seguir a ordem de secoes definida em
`docs/sdd/spec-template.md`. Quando uma secao nao se aplicar a uma base, manter
a secao e registrar `nao aplicavel`, `nao configurado` ou `nenhum`.

Quando houver SLD, ele deve existir somente no `silver_data` e o nome deve
comecar com `sld_`, no formato `sld_<nome_sem_prefixo_geometrico>.sld`.
Prefixos como `pnt_`, `pol_`, `lin_` e `rst_` nao entram no nome do SLD.

## Baselines

- `car_area_preservacao_permanente.md`
- `car_reserva_legal.md`
- `car_servidao_administrativa.md`
- `car_uso_restrito.md`
- `estado.md`
- `localidades.md`
- `setor_censitario.md`
- `autorizacao_para_supressao_vegetal-auth_supn.md`
- `autos_infracao.md`
- `degradacao_amazonia.md`
- `default.md`

As specs de baseline descrevem o comportamento atual do repositorio. Quando uma
regra de negocio ficar mais detalhada, atualize a spec antes de alterar o
codigo.
