# Monty Hall - switching + a simple Metropolis to determine IF we switch
# K doors
# Contestant chooses i, MH shows j
# Switch is correct only with a probability 1 / (K-2)

# So we sample a random number r uniformly from [0,1] and ONLY switch IF
# r <= 1 / (K-2)

# then we see what happens when we conditionally switch!



N_experiments <- 1000
N_chances <- 100
door_list <- 1:5
N_tot <- N_experiments * N_chances

K <- length(door_list)
K2 <- K - 2
switch_prob_threshold <- 1.0 / K2

succ_df <- data.frame(
  n = 1:N_experiments,
  success_switch = integer(N_experiments),
  success_stay = integer(N_experiments)
)

perf_df <- data.frame(
  car = rep(NA, N_tot),
  guess = rep(NA, N_tot),
  switched_guess = rep(NA, N_tot),
  s_stay = rep(0, N_tot),
  s_switch = rep(0, N_tot),
  good_switch = rep(0, N_tot),
  switch_approved = rep(NA, N_tot)
  
)
ctr <- 1

for (e in 1:N_experiments) {
  success_switch <- 0
  success_stay <- 0
  
  for (n in 1:N_chances) {
    car <- sample(door_list, 1)
    guess <- sample(door_list, 1)
    s_switch <- 0
    s_stay <- 0
    sa <- 0
    
    # Host opens a goat door that is not the guessed door
    possible_hall <- setdiff(door_list, c(guess, car))
    
    #if (length(possible_hall) == 0) {
    #  # guess == car, so host can open either goat door
    #  possible_hall <- setdiff(door_list, guess)
    #}
    
    #hall <- sample(possible_hall, 1)
    hall <- if (length(possible_hall) == 1) possible_hall else sample(possible_hall, 1)
    
    
    # we only switch with a conditional probability 1 / (K-2)
    
    if (runif(1) <= switch_prob_threshold) {
      # we switched since we got a runif <= switch probability threshold
      
    switched_guess <- setdiff(door_list, c(guess, hall))
    sa <- 1
    
    if (length(switched_guess) == 1) {
      if (switched_guess == car)  {
        success_switch <- success_switch + 1
        s_switch <- 1
      } else {
        s_switch <- 0
      }
    } else {
      switched_guess <- sample(switched_guess, 1)
      if (switched_guess == car) {
        success_switch <- success_switch + 1
        s_switch <- 1
      } else {
        s_switch <- 0
      }
    }
    
    } else {
      switched_guess <- guess # No change but also no updation of s_switch at all
      sa <- 0
    }
    
    if (guess == car) {
      success_stay <- success_stay + 1
      s_stay <- 1
    } else {
      s_stay <- 0
    }
    
    perf_df[ctr,1] <- car
    perf_df[ctr,2] <- guess
    perf_df[ctr,3] <- switched_guess
    perf_df[ctr,4] <- s_stay
    perf_df[ctr,5] <- s_switch
    
    if (s_switch == 1) {
      perf_df[ctr,6] <- 1
    }
    ctr <- ctr + 1
  }
  
  perf_df[ctr,7] <- sa # did we even switch? 1 = yes, 0 = no
  
  succ_df$success_switch[e] <- success_switch
  succ_df$success_stay[e] <- success_stay
}

library(ggplot2)

ggplot(succ_df) +
  geom_histogram(aes(x = success_switch), bins = 30,
                 colour = "red", fill = "red", alpha = 0.25) +
  geom_histogram(aes(x = success_stay), bins = 30,
                 colour = "blue", fill = "blue", alpha = 0.25) +
  ggtitle("Monty Hall: switch vs stay") +
  xlab("Successes out of 100 per experiment")

cat("Mean and SD successes with switch = ",
    mean(succ_df$success_switch),
    sd(succ_df$success_switch), "\n")

cat("Mean and SD successes without switch = ",
    mean(succ_df$success_stay),
    sd(succ_df$success_stay), "\n")

# Quantify our data 

# if s_stay = 0 and s_switch = 0 <- car was in a different slot entirely. missed
# if s_stay = 0 and s_switch = 1 <- switching was correct
# if s_stay = 1 and s_switch = 0 <- original guess was correct

diff_door <- nrow(subset(perf_df, s_stay == 0 & s_switch == 0))
diff_door

switch_correct <- nrow(subset(perf_df, s_stay == 0 & s_switch == 1))
switch_correct

stay_correct <- nrow(subset(perf_df, s_stay == 1 & s_switch == 0))
stay_correct

diff_door + switch_correct + stay_correct
N_tot