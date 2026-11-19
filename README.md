# Transitório térmico de cabo conectado ao borne de minidisjuntor — dados e código

Dados e código do artigo **"Caracterização experimental da resposta térmica transitória de cabo conectado ao borne de minidisjuntor"** (F. A. de Albuquerque Júnior, R. C. S. Gomes e I. G. Torné, PPGEEL/EST/UEA).

## Conteúdo

| Arquivo | Descrição |
|---|---|
| `dados/leituras_1hz.csv` | Registros de 1 Hz dos 29 ensaios (ids 49 a 77) |
| `dados/ensaios.csv` | Nível de torque de cada ensaio e se ele entra na estatística |
| `codigo/analise.py` | Calcula R_30:90 e Q_beta de cada ensaio e as estatísticas principais do artigo |

### `dados/leituras_1hz.csv`

| Coluna | Unidade | Descrição |
|---|---|---|
| `id` | — | Ensaio (um reaperto do borne e um pulso de carga) |
| `timestamp_local` | — | Data e hora (America/Manaus, UTC−4) |
| `volt_V`, `curr_A`, `power_W`, `pf` | V, A, W, — | Tensão, corrente, potência e fator de potência (PZEM-016) |
| `temp_1_C`, `hum_1_pct` | °C, % | SHT40 Ch1, fixado à isolação do cabo junto ao borne de saída |
| `temp_8_C`, `hum_8_pct` | °C, % | SHT40 Ch8, ar ambiente |
| `load_state` | — | Estado do relé (ON/OFF); vazio nos registros mais antigos |

Cada registro de 1 s é a média de quatro leituras de cada SHT40.

### `dados/ensaios.csv`

`torque_pct` é o percentual do torque de referência de 2,5 N·m (T5 = 0,125 N·m ... T100 = 2,5 N·m). Os ensaios 54 (T120) e 62 (T15), únicos em seus níveis, têm `na_estatistica = False`.

## Bancada

Minidisjuntor monopolar de 10 A, curva C; cabo flexível de cobre/PVC de 1,5 mm² ligado ao borne sem terminal; carga resistiva de 1440 W (≈ 11 A); conjunto sem invólucro. Cada ensaio: reaperto do borne até o torque do nível, ≈ 60 s sem carga, um pulso de ≈ 180 s e registro do resfriamento.

## Como reproduzir

```bash
pip install numpy pandas scipy
python codigo/analise.py
```

O script grava `resultados/parametros_por_ensaio.csv` e imprime, por nível, a média e o desvio-padrão de R_30:90 e Q_beta, a correlação de Spearman com o torque, o ε² de Kruskal-Wallis, o valor-p da permutação dentro da sessão e a probabilidade de superioridade entre níveis vizinhos (Tabelas e Fig. de resultados do artigo).

## Licença e citação

Dados: CC BY 4.0. Código: MIT. Ao usar, cite o artigo.
