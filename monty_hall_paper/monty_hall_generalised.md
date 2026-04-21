# Monty Hall — Generalised Theory

## Overview

We generalise the classical Monty Hall problem to:

- K ≥ 3 doors
- m ≥ 1 prize doors
- Monty opens r ≥ 1 doors, each guaranteed to have no prize
- The player:
  1. Picks one door uniformly at random
  2. Observes Monty opening r losing doors
  3. Either:
     - stays, or
     - switches uniformly to one of the remaining unopened doors

---

## Feasibility Constraints

1 ≤ m < K

0 ≤ r ≤ K - m - 1

---

## Strategy 1: Stay

P(stay wins) = m / K

---

## Strategy 2: Switch

After Monty opens r losing doors, remaining unopened doors (excluding original choice):

K - 1 - r

### Case 1: Initial pick is a prize

P = m / K

Win probability after switching:

(m - 1) / (K - 1 - r)

### Case 2: Initial pick is not a prize

P = (K - m) / K

Win probability after switching:

m / (K - 1 - r)

---

### Combined

P(switch wins) =
(m/K)*(m-1)/(K-1-r) + (K-m)/K * m/(K-1-r)

= m(K-1) / [K(K-1-r)]

---

## Final Results

P(stay) = m / K

P(switch) = m(K-1) / [K(K-1-r)]

---

## Advantage

P(switch) - P(stay) = mr / [K(K-1-r)]

---

## Ratio

P(switch) / P(stay) = (K-1)/(K-1-r)

---

## Special Cases

### Classical (K=3, m=1, r=1)

Stay = 1/3  
Switch = 2/3

---

### Single prize (m=1)

Stay = 1/K  
Switch = (K-1) / [K(K-1-r)]

---

### If r = 1

Switch = (K-1) / [K(K-2)]

---

### If r = K-2

Switch = (K-1)/K

---

### Multiple prizes

Stay = m/K  
Switch = m(K-1) / [K(K-1-r)]

---

### Example

K=10, m=3, r=4

Stay = 0.3  
Switch = 0.54

---

## Intuition

- Original door keeps probability m/K
- Monty removes losing doors from alternatives
- Probability mass concentrates on fewer doors

---

## Summary

Stay = m/K  
Switch = m(K-1) / [K(K-1-r)]  
Advantage = mr / [K(K-1-r)]
