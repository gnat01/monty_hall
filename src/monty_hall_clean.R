N_experiments <- 1000
N_chances <- 1000
num_doors <- 4
door_list <- 1:num_doors

N_tot <- N_experiments * N_chances

stay_correct <- 0
switch_correct <- 0
diff_door <- 0

succ_df <- data.frame(
  n = 1:N_experiments,
  success_switch = integer(N_experiments),
  success_stay = integer(N_experiments)
)

for (e in 1:N_experiments) {
  success_switch <- 0
  success_stay <- 0
  
  for (n in 1:N_chances) {
    car <- sample(door_list, 1)
    guess <- sample(door_list, 1)
    
    # Host opens a goat door that is not the guessed door
    possible_hall <- setdiff(door_list, c(guess, car))
    
    #if (length(possible_hall) == 0) {
    #  # guess == car, so host can open either goat door
    #  possible_hall <- setdiff(door_list, guess)
    #}
    
    #hall <- sample(possible_hall, 1)
    hall <- if (length(possible_hall) == 1) possible_hall else sample(possible_hall, 1)
    
    switched_guess <- setdiff(door_list, c(guess, hall))
    
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
    
    if (guess == car) {
      success_stay <- success_stay + 1
      s_stay <- 1
    } else {
      s_stay <- 0
    }
    
    # some elementary counting here #
    # Quantify our data 
    
    # if s_stay = 0 and s_switch = 0 <- car was in a different slot entirely. missed
    # if s_stay = 0 and s_switch = 1 <- switching was correct
    # if s_stay = 1 and s_switch = 0 <- original guess was correct
    
    if (s_stay == 0 & s_switch == 0) {
      diff_door <- diff_door + 1
    }
    
    if (s_stay == 0 & s_switch == 1) {
      switch_correct <- switch_correct + 1
    }
    
    if (s_stay == 1 & s_switch == 0) {
      stay_correct <- stay_correct + 1
    }
  } # chances in a given experiment loop here #
  
  succ_df$success_switch[e] <- success_switch
  succ_df$success_stay[e] <- success_stay
} # experiment loop here 

# plotting 
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


cat("Entirely missed = ", diff_door, "\n")

cat("Switch correct = ", switch_correct, "\n")

cat("Stay correct = ", stay_correct, "\n")

diff_door + switch_correct + stay_correct
cat("confirming N_tot = ", N_tot, " = ", N_experiments*N_chances,"\n")


