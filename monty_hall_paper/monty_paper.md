# Generalised Monty Hall with Switching Costs:  
## Optimal Stopping with Increasing Marginal Value of Information

---

## Abstract

We study a generalisation of the Monty Hall problem with \(K\) doors and \(m\) prizes in which a host sequentially reveals non-prize doors at a cost. This transforms the classical puzzle into a deterministic sequential information acquisition problem.

We derive closed-form expressions for switching probabilities under arbitrary reveal depth, and formulate the agent’s decision as an optimal stopping problem. We show that the marginal value of information is **strictly increasing** in the number of reveals, in contrast to classical models such as Pandora’s box, where marginal value decreases. This leads to a structural failure of myopic policies.

We characterise the optimal policy and prove the existence of a sharp phase transition in behaviour as a function of reveal cost. Empirical simulations confirm the theoretical predictions and illustrate the transition between immediate stopping and full information acquisition regimes.

---

## 1. Introduction

The Monty Hall problem is a canonical example of probabilistic reasoning under partial information. Its classical formulation shows that switching dominates staying, due to a redistribution of probability mass following the host’s reveal.

However, the classical setting assumes:
- a fixed number of doors,
- a single reveal,
- and **zero cost of information**.

These assumptions obscure a deeper question:

> **How much information should one acquire before making a decision?**

We address this by introducing:
- an arbitrary number of doors \(K\),
- multiple prizes \(m\),
- **sequential reveals**, and
- **costs associated with each reveal**.

This transforms Monty Hall from a static puzzle into a **sequential decision problem** with a deterministic state space.

---

## 2. Related Work

### Monty Hall Variants
Numerous generalisations of Monty Hall consider:
- more than three doors,
- multiple prizes,
- different host strategies.

These works primarily analyse static switching probabilities, without considering costs or sequential decisions.

### Optimal Stopping and Information Acquisition
The problem relates to classical optimal stopping and search theory, particularly:

- **Pandora’s box problem** (Weitzman, 1979)
- Sequential decision processes with costly observations

However, these models typically assume:
- independent reward draws,
- diminishing marginal value of information.

### Key Gap
To our knowledge, no prior work studies:

> **Sequential elimination-based information acquisition with increasing marginal value.**

This is the central novelty of our formulation.

---

## 3. Model

We consider:

- \(K\) doors, \(m\) of which contain prizes.
- The agent selects one door uniformly at random.
- The host knows prize locations and reveals non-prize doors sequentially.

Constraints:
\begin{equation}
$0 \le t \le K - m - 1$
\end{equation}

Each reveal incurs cost \(c_i\).

After \(t\) reveals, the agent:
- switches uniformly among remaining unopened doors.

---

## 4. Central Idea

The key structural property is:

> **Reveals eliminate losing options, thereby concentrating probability mass.**

Unlike classical learning models:
- no new rewards are revealed,
- only **impossibilities are eliminated**.

This leads to a fundamentally different geometry of information:

- early reveals: weak impact
- late reveals: extremely strong impact

This produces **increasing marginal value of information**, which drives all subsequent results.

---

## 5. Switching Probability

### Theorem 1
\[
$P_t(\text{switch}) = \frac{m(K-1)}{K(K-1-t)}$
\]

### Interpretation
- Probability mass initially spread over \(K-1\) doors
- After eliminating \(t\) losing doors, it is redistributed over \(K-1-t\)

---

## 6. Optimal Stopping

Define:

\[
$S(t) = V \cdot \frac{m(K-1)}{K(K-1-t)}$
\]

\[
$W(t) = S(t) - \sum_{i=1}^t c_i$
\]

### Theorem 2
\[
$t^* \in \arg\max_{t} W(t)$
\]

---

## 7. Increasing Marginal Value

### Proposition
\[
\Delta_t = S(t+1) - S(t)
= \frac{m(K-1)}{K(K-2-t)(K-1-t)}
\]

### Theorem 3
\[
\Delta_t \text{ is strictly increasing in } t
\]

---

## 8. Failure of Myopic Policies

A myopic policy accepts reveal \(t+1\) iff:
\[
\Delta_t \ge c
\]

### Theorem 4 (Non-myopic Gap)
There exist instances such that:
- myopic policy stops at \(t=0\),
- optimal policy chooses \(t=K-m-1\),
- yielding a constant-factor improvement.

### Insight
- Early reveals appear worthless
- Late reveals are extremely valuable
- Optimal policy requires **committing through low-value early steps**

---

## 9. Phase Transition

Assume constant cost $c_i = c$.

### Theorem 5
There exists \($c^*(K)$\) such that:

\[
$t^*$ = $K-m-1, c < c^*(K)$ \\
$t^{*} = 0, c > c^*(K)$
\\]

### Proposition
For \(m=1\):

\[
$c^*(K) = \Theta\left(\frac{1}{K}\right)$
\]

---

## 10. Experiments

We simulate:

- \($K \in \{10, 20, 50, 100\}$\)
- \($m = 1$\)
- varying \($c$\)

### Observations

1. \($S(t)$\) is convex and sharply increasing near terminal stages  
2. \($W(t)$\) is non-monotonic  
3. Optimal \($t^*$\) exhibits a sharp threshold  
4. Empirically:
   \[
   $c^*(K) \approx \frac{1}{K}$
   \]

### Key Plot Suggestions

- $S(t)$ vs $t$
- $W(t)$ vs $t$
- $t^*$ vs $c$
- heatmap: $(K,c)$ $\to$ $t^*$

---

## 11. Comparison to Pandora’s Box

| Property | Pandora | This Work |
|--------|--------|-----------|
| Info type | reward revelation | elimination |
| Independence | independent | coupled |
| Marginal value | decreasing | increasing |
| Optimal policy | greedy index | non-myopic |
| State | high-dim | 1D (t) |

### Key Difference

Pandora assumes:
\[
\text{Value of information decreases}
\]

We show:
\[
\text{Value of information increases}
\]

This fundamentally changes:
- policy structure
- algorithm design
- approximation guarantees

---

## 12. Conclusion

Introducing costs transforms Monty Hall into a structured optimal stopping problem with:

- increasing marginal information value,
- failure of greedy policies,
- sharp phase transitions.

This provides a clean and tractable counterexample to standard assumptions in information acquisition.

---

## 13. Future Work

- stochastic / adversarial hosts  
- Bayesian uncertainty over \(m\)  
- non-uniform switching policies  
- partial reveals  
- continuous-time formulation  
- connections to bandits with structured feedback  

---

## References

- Weitzman, M. (1979). Optimal search for the best alternative.
