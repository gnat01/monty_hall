# Monty Hall generalised 
# K >=3 doors, m >=1 prize, and Monty can choose to open r >= 1 doors 

simulate_monty_general <- function(
    K = 3,
    m = 1,
    r = 1,
    N_experiments = 10000,
    N_chances = 100
) {
  if (m < 1 || m >= K) stop("Need 1 <= m < K")
  if (r < 0 || r > (K - m - 1)) stop("Need 0 <= r <= K - m - 1")
  
  door_list <- 1:K
  
  results <- data.frame(
    experiment = 1:N_experiments,
    success_stay = integer(N_experiments),
    success_switch = integer(N_experiments)
  )
  
  for (e in 1:N_experiments) {
    success_stay <- 0
    success_switch <- 0
    
    for (n in 1:N_chances) {
      # Randomly place m prizes
      prize_doors <- sample(door_list, m)
      
      # Initial guess
      guess <- sample(door_list, 1)
      
      # Doors Monty is allowed to open:
      # not your guess, and not a prize
      monty_options <- setdiff(door_list, c(guess, prize_doors))
      
      # Monty opens r losing doors uniformly from allowed options
      opened <- if (r == 0) integer(0) else sample(monty_options, r)
      
      # Stay
      if (guess %in% prize_doors) {
        success_stay <- success_stay + 1
      }
      
      # Switch uniformly to one other unopened door
      switch_options <- setdiff(door_list, c(guess, opened))
      switched_guess <- switch_options[sample.int(length(switch_options), 1)]
      
      if (switched_guess %in% prize_doors) {
        success_switch <- success_switch + 1
      }
    }
    
    results$success_stay[e] <- success_stay
    results$success_switch[e] <- success_switch
  }
  
  theory_stay <- m / K
  theory_switch <- m * (K - 1) / (K * (K - 1 - r))
  
  list(
    params = list(K = K, m = m, r = r,
                  N_experiments = N_experiments,
                  N_chances = N_chances),
    theory = c(
      stay = theory_stay,
      switch = theory_switch
    ),
    empirical = c(
      stay = mean(results$success_stay) / N_chances,
      switch = mean(results$success_switch) / N_chances
    ),
    raw = results
  )
}

# plotting

library(ggplot2)

plot_results <- function(out) {
  df <- data.frame(
    strategy = c("stay", "switch"),
    theory = as.numeric(out$theory),
    empirical = as.numeric(out$empirical)
  )
  
  ggplot(df, aes(x = strategy)) +
    geom_point(aes(y = theory), size = 3, colour = "red", fill = 0.2) +
    geom_point(aes(y = empirical), size = 4, colour = "blue", fill = 0.3) +
    ylim(0, 1) +
    ggtitle(
      paste0(
        "Monty Hall Generalization: K=", out$params$K,
        ", m=", out$params$m,
        ", r=", out$params$r
      )
    ) +
    ylab("Probability of winning")
}


# Run the full thing

# Classical Monty Hall

out1 <- simulate_monty_general(K = 3, m = 1, r = 1)
out1$theory
out1$empirical

# 10 doors, 1 prize, 1 door opened

out2 <- simulate_monty_general(K = 10, m = 1, r = 1)
out2$theory
out2$empirical

# 10 doors, 1 prize, Monty Hall opens 8 doors without a prize behind them

out3 <- simulate_monty_general(K = 10, m = 1, r = 8)
out3$theory
out3$empirical

# 10 doors, 3 prize, MH opens 4 doors

out4 <- simulate_monty_general(K = 10, m = 3, r = 4)
out4$theory
out4$empirical

plot_results(out1)
