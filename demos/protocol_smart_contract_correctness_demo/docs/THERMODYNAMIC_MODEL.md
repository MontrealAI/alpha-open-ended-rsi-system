# Thermodynamic / Statistical-Physics Governance Model (Formal Analogy)

This demo uses a **formal governance analogy** to keep resource use, entropy pressure, and proof quality legible.
It is not a claim of literal physical law.
It is a formal analogy with measurable operational content for governance and operator review.

## State vector

$$
X(t)=\big(K,C,D,A,Q,R,\Sigma\big)
$$

- $K$ = deployable capital
- $C$ = compute throughput
- $D$ = data, observations, and telemetry
- $A$ = archived reusable capability
- $Q$ = proof quality and correctness level
- $R$ = rate of validated output
- $\Sigma$ = sovereign control

We reserve $\mathcal S_{\text{org}}$ for organizational entropy.

## Resource flux decomposition

$$
J_{\text{in}}=\alpha_K \dot K_{\text{in}}+\alpha_C \dot C_{\text{in}}+\alpha_D \dot D_{\text{in}}
$$

$$
J_{\text{in}}=\dot W_{\text{useful}}+\dot Q_{\text{diss}}+\dot U
$$

$$
\dot W_{\text{useful}} \approx \beta_A \dot A + \beta_Q \dot Q + \beta_R \dot R_{\text{validated}}
$$

## Free-energy functional

$$
\mathcal G[X]=\mathcal H[X]-T_{\text{eff}}\mathcal S_{\text{org}}[X]
$$

Objective:

$$
\min \mathcal G[X]
$$

Differential form:

$$
d\mathcal G = d\mathcal H - T_{\text{eff}}\,d\mathcal S_{\text{org}} - \mathcal S_{\text{org}}\,dT_{\text{eff}}
$$

## Nonequilibrium maintenance

$$
\frac{dX}{dt}=F_{\text{drive}}(X)-F_{\text{decay}}(X)
$$

$$
\left\langle \frac{dX}{dt}\right\rangle \approx 0
$$

with:

$$
J_{\text{in}}>0,\qquad \dot Q_{\text{diss}}>0,\qquad \dot W_{\text{useful}}>0
$$

## Microstates and economic selection

$$
E_i = E_i^{\text{resource}} + E_i^{\text{error}} + E_i^{\text{latency}} + E_i^{\text{governance}} - E_i^{\text{reuse}}
$$

$$
P_i=\frac{e^{-E_i/(k_B T_{\text{eff}})}}{Z}, \qquad
Z=\sum_i e^{-E_i/(k_B T_{\text{eff}})}
$$

## Entropy balance and viability

$$
\frac{d\mathcal S_{\text{org}}}{dt}=\Pi-\Phi
$$

Viability condition:

$$
\Phi \ge \Pi
$$

## Efficiency

$$
\eta_{\text{sovereign}}=\frac{\dot W_{\text{useful}}}{J_{\text{in}}}
$$

$$
\eta_{\text{archive}}=\frac{\dot A_{\text{reused}}}{J_{\text{in}}}
$$

## Order parameter and phase transition

$$
\Lambda=\frac{\rho_{\text{reuse}}\,\rho_{\text{validation}}\,\rho_{\text{selection}}}{\Pi}
$$

- If $\Lambda < \Lambda_c$: consultancy / bespoke mode.
- If $\Lambda > \Lambda_c$: compounding sovereign mode.
