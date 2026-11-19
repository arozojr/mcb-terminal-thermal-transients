"""Reproduz os parâmetros e as estatísticas principais do artigo:
"Caracterização experimental da resposta térmica transitória de cabo conectado ao borne de minidisjuntor".

Uso:  python codigo/analise.py            (a partir da pasta raiz do repositório)
Saída: resultados/parametros_por_ensaio.csv e o resumo impresso no terminal.

Definições (Seção III-D do artigo):
  t = 0     primeira amostra com corrente acima de 1 A
  t_off     primeira amostra sem corrente (<= 1 A) depois do patamar
  dT        temp_1 - temp_8 (cabo junto ao borne menos ar ambiente)
  beta      inclinação (°C/min) da regressão linear de dT na janela
  I2        média dos quadrados da corrente entre 10 s e t_off - 5 s
  R_30_90   1000 * beta(30-90 s) / I2      [m°C/(min.A²)]
  Q_beta    beta(90 s - t_off) / beta(30-90 s)
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parents[1]
NIVEIS = [5, 10, 25, 50, 100]


def parametros(g):
    g = g.sort_values("timestamp_local")
    ts = pd.to_datetime(g["timestamp_local"])
    c = g["curr_A"].to_numpy()
    k0 = int(np.argmax(c > 1))
    t = (ts - ts.iloc[k0]).dt.total_seconds().to_numpy()
    t_off = t[np.where((t > 0) & (c <= 1))[0][0]]
    dT = (g["temp_1_C"] - g["temp_8_C"]).to_numpy()

    def inclinacao(a, b, incluir_b=True):
        m = (t >= a) & ((t <= b) if incluir_b else (t < b))
        return np.polyfit(t[m] / 60.0, dT[m], 1)[0]

    b1 = inclinacao(30, 90)
    b2 = inclinacao(90, t_off)
    mi = (t >= 10) & (t <= t_off - 5)
    I2 = float(np.mean(c[mi] ** 2))
    return pd.Series({
        "inicio_pulso": ts.iloc[k0],
        "t_off_s": t_off,
        "I2_A2": I2,
        "beta_30_90_C_min": b1,
        "beta_90_off_C_min": b2,
        "R_30_90": 1000 * b1 / I2,
        "Q_beta": b2 / b1,
        "T_amb_pre_C": g.loc[(t < 0) & (t >= -10), "temp_8_C"].mean(),
    })


def epsilon2(d, v):
    H = stats.kruskal(*[d.loc[d.torque_pct == k, v] for k in NIVEIS]).statistic
    n = len(d)
    return H / ((n ** 2 - 1) / (n + 1))


def perm_dentro_sessao(d, v, n_perm=100_000, semente=20261118):
    rng = np.random.default_rng(semente)
    tq = d["torque_pct"].to_numpy()
    ry = stats.rankdata(d[v].to_numpy())
    obs = abs(stats.spearmanr(tq, ry).statistic)
    grupos = [np.where(d["sessao"].to_numpy() == s)[0] for s in d["sessao"].unique()]
    cont = 0
    for _ in range(n_perm):
        t2 = tq.copy()
        for g in grupos:
            t2[g] = rng.permutation(tq[g])
        if abs(np.corrcoef(stats.rankdata(t2), ry)[0, 1]) >= obs - 1e-12:
            cont += 1
    return (cont + 1) / (n_perm + 1)


def main():
    L = pd.read_csv(RAIZ / "dados" / "leituras_1hz.csv")
    E = pd.read_csv(RAIZ / "dados" / "ensaios.csv")
    P = L.groupby("id").apply(parametros).reset_index().merge(E, on="id")
    # sessões: intervalos de mais de 4 h entre inícios de pulso (inclui os 29 ensaios)
    P = P.sort_values("inicio_pulso")
    P["sessao"] = (P["inicio_pulso"].diff() > pd.Timedelta(hours=4)).cumsum() + 1
    P = P.sort_values("id")
    (RAIZ / "resultados").mkdir(exist_ok=True)
    P.to_csv(RAIZ / "resultados" / "parametros_por_ensaio.csv", index=False)

    D = P[P["na_estatistica"]].copy()
    print(f"Ensaios na estatística: {len(D)} (sessões: {D['sessao'].nunique()})\n")
    print("Por nível (média ± desvio-padrão):")
    for k in NIVEIS:
        x = D[D.torque_pct == k]
        print(f"  T{k:<3d} n={len(x)}  R_30_90 = {x.R_30_90.mean():6.2f} ± {x.R_30_90.std():.2f}"
              f"   Q_beta = {x.Q_beta.mean():.3f} ± {x.Q_beta.std():.3f}")
    print()
    for v in ["R_30_90", "Q_beta"]:
        rho = stats.spearmanr(D.torque_pct, D[v]).statistic
        print(f"{v}: Spearman = {rho:+.2f}; epsilon² (Kruskal-Wallis) = {epsilon2(D, v):.2f}; "
              f"p (permutação dentro da sessão) = {perm_dentro_sessao(D, v):.4f}")
    print("\nProbabilidade de superioridade entre níveis vizinhos (R_30_90):")
    for a, b in zip(NIVEIS[:-1], NIVEIS[1:]):
        xa = D.loc[D.torque_pct == a, "R_30_90"].to_numpy()
        xb = D.loc[D.torque_pct == b, "R_30_90"].to_numpy()
        ps = (xa[:, None] > xb[None]).mean() + 0.5 * (xa[:, None] == xb[None]).mean()
        print(f"  T{a}-T{b}: {ps:.2f}")


if __name__ == "__main__":
    main()
