# Thermodynamic / Nonequilibrium Governance Model (Formal Analogy)

This model is a formal governance analogy with measurable operational content.
It is **not** a claim of literal physical law.

## State vector

$$
X(t)=\big(K,C,D,A,Q,R,\Sigma\big)
$$

## Resource influx

$$
J_{\text{in}}=\alpha_K \dot K_{\text{in}}+\alpha_C \dot C_{\text{in}}+\alpha_D \dot D_{\text{in}}
$$

## Useful work partition

$$
J_{\text{in}}=\dot W_{\text{useful}}+\dot Q_{\text{diss}}+\dot U
$$

## Useful work approximation

$$
\dot W_{\text{useful}} \approx \beta_A \dot A + \beta_Q \dot Q + \beta_R \dot R_{\text{validated}}
$$

## Free-energy functional

$$
\mathcal G[X]=\mathcal H[X]-T_{\text{eff}}\mathcal S_{\text{org}}[X]
$$

## Objective

$$
\min \mathcal G[X]
$$

## Corrected differential

$$
d\mathcal G = d\mathcal H - T_{\text{eff}}\,d\mathcal S_{\text{org}} - \mathcal S_{\text{org}}\,dT_{\text{eff}}
$$

## Nonequilibrium maintenance

$$
\frac{dX}{dt}=F_{\text{drive}}(X)-F_{\text{decay}}(X)
$$

## Steady operation

$$
\left\langle \frac{dX}{dt}\right\rangle \approx 0
$$

## Nonzero throughputs

$$
J_{\text{in}}>0,\qquad \dot Q_{\text{diss}}>0,\qquad \dot W_{\text{useful}}>0
$$

## Microstate cost

$$
E_i = E_i^{\text{resource}} + E_i^{\text{error}} + E_i^{\text{latency}} + E_i^{\text{governance}} - E_i^{\text{reuse}}
$$

## Boltzmann-style ensemble

$$
P_i=\frac{e^{-E_i/(k_B T_{\text{eff}})}}{Z}, \qquad
Z=\sum_i e^{-E_i/(k_B T_{\text{eff}})}
$$

## Entropy balance

$$
\frac{d\mathcal S_{\text{org}}}{dt}=\Pi-\Phi
$$

## Viability

$$
\Phi \ge \Pi
$$

## Sovereign efficiency

$$
\eta_{\text{sovereign}}=\frac{\dot W_{\text{useful}}}{J_{\text{in}}}
$$

## Archive efficiency

$$
\eta_{\text{archive}}=\frac{\dot A_{\text{reused}}}{J_{\text{in}}}
$$

## Order parameter

$$
\Lambda=\frac{\rho_{\text{reuse}}\,\rho_{\text{validation}}\,\rho_{\text{selection}}}{\Pi}
$$
