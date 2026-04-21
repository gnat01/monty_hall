library(ggplot2)

x <- seq(0, 10, by = 1)
y <- x*x + 2 + rnorm(length(x), 3, 2)

df <- data.frame(x=x, y=y)
ggplot(df, aes(x = x, y = y)) +
  geom_path(arrow = arrow())

#SAW
v_up <- c(0,1)
vdn <- c(0,-1)
v_left <- c(-1,0)
v_right <- c(1,0)

start <- c(0,0)

start[1]
start[2]
N <- 1000

saw_df <- data.frame(
  x = rep(NA, N),
  y = rep(NA, N)
)

dd <- data.frame(x = c(0,1), y = c(2,3))

dd
key_set <- paste(dd$x, dd$y, sep = "||")
key_set

check_member <- function(x, y) paste(x, y, sep = "||") %in% key_set

check_member(0,1)
check_member(1,3)


# Rademacher
choices <- c(-1,1)
proba <- c(0.75, 0.25)
N <- 100000
sample_data <- sample(choices,
                      N,
                      replace = TRUE,
                      prob = proba)

mean(sample_data)
sd(sample_data) # sqrt(1 - mean_val*mean_val) obv

# Monty hall for fun


# car behind 1
# hall will only open doors 2 or 3
N_experiments <- 10000
N_chances <- 100

succ_df <- data.frame(
  n = rep(NA, N_experiments),
  success = rep(NA, N_experiments),
  success_2 = rep(NA, N_experiments)
  
)


for (e in 1:N_experiments) {
  cat("expt num = ", e, "\n")
# denote car by 1, goat by 0
doors <- c(1,0,0) # Car behind door 1

car <- which(doors == 1)
door_list <- seq(1, length(doors), by = 1)

success <- 0
success_2 <- 0

for (n in 1:N_chances) {
  guess <- sample(door_list, 1)
  
  if (guess == car) {
    door_show <- door_list[c(-guess)]
    hall <- sample(c(door_show), 1)
  } else {
    door_show <- door_list[c(-guess,-car)]
    hall <- sample(c(door_show), 1)
  }
  
  # switch
  new_guess <- door_list[c(-guess,-hall)][1]
  new_guess_2 <- guess
  
  if (new_guess == car) {
    success <- success + 1
  }
  
  if (new_guess_2 == car) {
    success_2 <- success_2 + 1
  }
}

succ_df[e,1] <- e
succ_df[e,2] <- success
succ_df[e,3] <- success_2


} # experiments


# plot
library(ggplot2)

ggplot(
  data = succ_df
) + geom_histogram(aes(x = success), colour = "red", fill = "red", alpha = 0.2) + 
  geom_histogram(aes(x = success_2), colour = "blue", fill = "blue", alpha = 0.2) + 
  ggtitle("Comparing Monty hall successes with switch and not") 

cat("Mean and SD successes with switch = ", mean(succ_df$success), sd(succ_df$success))

cat("Mean and SD successes without switch = ", mean(succ_df$success_2), sd(succ_df$success_2))



