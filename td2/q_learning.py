import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt


def update_q_table(Q, s, a, r, sprime, alpha, gamma):
    """
    This function should update the Q function for a given pair of action-state
    following the q-learning algorithm, it takes as input the Q function, the pair action-state,
    the reward, the next state sprime, alpha the learning rate and gamma the discount factor.
    Return the same input Q but updated for the pair s and a.
    """
    Q[s, a] = Q[s, a] + alpha * (r + gamma * np.max(Q[sprime]) - Q[s, a])
    return Q


def epsilon_greedy(Q, s, epsilon):
    """
    This function implements the epsilon greedy algorithm.
    Takes as input the Q function for all states, a state s, and epsilon.
    It should return the action to take following the epsilon greedy algorithm.
    """
    if np.random.random() < epsilon:
        return np.random.randint(0, Q.shape[1])
    else:
        return np.argmax(Q[s])


if __name__ == "__main__":
    # Training environment (no rendering for speed)
    env = gym.make("Taxi-v3", render_mode="ansi")

    Q = np.zeros([env.observation_space.n, env.action_space.n])

    # Hyperparameters
    alpha = 0.1
    gamma = 0.9
    epsilon_max = 1.0
    epsilon_min = 0.01

    # Training settings
    n_epochs = 10000  # Maximum number of epochs
    max_itr_per_epoch = 200  # Maximum iterations per epoch (controls exploration)

    # Early stopping parameters
    use_early_stopping = False  # Enable early stopping
    early_stop_window = 100  # Check last 100 episodes
    early_stop_threshold = 8.0

    rewards = []
    converged = False

    for e in range(n_epochs):
        # Cosine decay for epsilon, more exploration at the start, gradually less
        epsilon = epsilon_min + (epsilon_max - epsilon_min) * (
            0.5 + 0.5 * np.cos(np.pi * e / n_epochs)
        )
        r = 0

        S, _ = env.reset()

        for _ in range(max_itr_per_epoch):
            A = epsilon_greedy(Q=Q, s=S, epsilon=epsilon)
            Sprime, R, done, _, info = env.step(A)
            r += R
            Q = update_q_table(
                Q=Q, s=S, a=A, r=R, sprime=Sprime, alpha=alpha, gamma=gamma
            )

            S = Sprime
            if done:
                break

        print("episode #", e, " : r = ", r)
        rewards.append(r)

        # Early stopping check
        if use_early_stopping and e >= early_stop_window:
            recent_avg = np.mean(rewards[-early_stop_window:])
            if recent_avg >= early_stop_threshold:
                print(f"\n✓ Early stopping triggered at episode {e}")
                print(
                    f"  Average reward over last {early_stop_window} episodes: {recent_avg:.2f}"
                )
                converged = True
                break

    print(f"\nTraining finished after {e+1} episodes")
    if len(rewards) >= 100:
        final_avg = np.mean(rewards[-100:])
        print("Final average reward (last 100 episodes) = ", final_avg)
    else:
        print("Average reward (all episodes) = ", np.mean(rewards))

    if converged:
        print(f"Status: CONVERGED (reward threshold {early_stop_threshold} reached)")
    else:
        print(f"Status: Completed all {n_epochs} epochs")

    plt.plot(rewards)
    plt.savefig("td2_q_learning_taxi_rewards.png")

    print("Training finished.\n")

    # Evaluation environment (with human rendering)
    env_eval = gym.make("Taxi-v3", render_mode="human")

    # Evaluation
    for e in range(10):
        S, _ = env_eval.reset()
        total_reward = 0
        done = False
        while not done:
            A = np.argmax(Q[S])
            S, R, done, _, _ = env_eval.step(A)
            total_reward += R
            env_eval.render()
        print(f"Evaluation episode {e}: total reward = {total_reward}")

    env.close()
    env_eval.close()
