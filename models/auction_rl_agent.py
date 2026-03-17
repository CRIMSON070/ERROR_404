"""
Reinforcement Learning Auction Agent
Learns optimal bidding strategy under budget constraints using PPO/DQN
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.env_checker import check_env
import pandas as pd


class AuctionEnvironment(gym.Env):
    """
    Custom Gym Environment for IPL Auction Simulation
    """
    
    metadata = {'render_modes': ['human']}
    
    def __init__(self, players_df, initial_budget=120.0, max_players=25):
        super(AuctionEnvironment, self).__init__()
        
        self.players_df = players_df
        self.initial_budget = initial_budget
        self.max_players = max_players
        
        # Action space: 0=Pass, 1-10=Bid amounts (in crores)
        self.action_space = spaces.Discrete(11)
        
        # Observation space: [budget_remaining, players_selected, current_player_impact, 
        #                     current_player_price, team_balance, auction_round]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, -10, 0], dtype=np.float32),
            high=np.array([initial_budget, max_players, 100, 20, 10, 10], dtype=np.float32),
            dtype=np.float32
        )
        
        self.reset()
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        self.budget_remaining = self.initial_budget
        self.players_selected = []
        self.current_player_idx = 0
        self.auction_round = 0
        self.total_spent = 0
        
        # Shuffle players
        self.shuffled_players = self.players_df.sample(frac=1).reset_index(drop=True)
        
        return self._get_observation(), {}
    
    def step(self, action):
        """
        Execute one step in auction
        action: 0=Pass, 1-10=Bid that amount in crores
        """
        
        reward = 0.0
        done = False
        info = {}
        
        if self.current_player_idx >= len(self.shuffled_players):
            done = True
            return self._get_observation(), reward, done, False, info
        
        current_player = self.shuffled_players.iloc[self.current_player_idx]
        player_impact = current_player.get('overall_impact', 50)
        player_price = current_player.get('sold_price', 1.0)
        
        # Process action
        if action == 0:
            # Pass
            reward = -0.1  # Small penalty for passing
            self.current_player_idx += 1
        else:
            # Bid
            bid_amount = action  # Simple mapping: action 1 = 1 Cr, etc.
            
            if bid_amount >= player_price:
                # Won the bid
                if len(self.players_selected) < self.max_players and bid_amount <= self.budget_remaining:
                    self.players_selected.append(current_player)
                    self.budget_remaining -= bid_amount
                    self.total_spent += bid_amount
                    
                    # Reward based on value gained
                    value_score = player_impact / (bid_amount * 10)
                    reward = value_score + 0.5  # Positive reward for good purchase
                else:
                    # Invalid bid (over budget or squad full)
                    reward = -1.0  # Large penalty
            else:
                # Lost the bid
                reward = -0.2
                self.current_player_idx += 1
        
        # Team balance reward/penalty
        if len(self.players_selected) > 0:
            balance_score = self._calculate_team_balance()
            reward += balance_score * 0.1
        
        # Budget management reward
        budget_efficiency = self.total_spent / self.initial_budget
        if budget_efficiency > 0.8 and budget_efficiency <= 1.0:
            reward += 0.5  # Bonus for spending optimally
        elif budget_efficiency > 1.0:
            reward -= 0.5  # Penalty for overspending
        
        self.auction_round += 1
        
        # End conditions
        if self.auction_round >= 100 or len(self.players_selected) >= self.max_players:
            done = True
        
        return self._get_observation(), reward, done, False, info
    
    def _get_observation(self):
        """Get current state observation"""
        
        if self.current_player_idx < len(self.shuffled_players):
            current_player = self.shuffled_players.iloc[self.current_player_idx]
            player_impact = current_player.get('overall_impact', 50)
            player_price = current_player.get('sold_price', 1.0)
        else:
            player_impact = 0
            player_price = 0
        
        team_balance = self._calculate_team_balance()
        
        obs = np.array([
            self.budget_remaining,
            len(self.players_selected),
            player_impact,
            player_price,
            team_balance,
            self.auction_round
        ], dtype=np.float32)
        
        return obs
    
    def _calculate_team_balance(self):
        """Calculate team composition balance"""
        
        if len(self.players_selected) == 0:
            return 0.0
        
        roles = [p.get('role', 'Unknown') for p in self.players_selected]
        
        batsmen = roles.count('Batsman') + roles.count('Wicket-keeper')
        bowlers = roles.count('Bowler')
        allrounders = roles.count('All-rounder')
        
        # Ideal ratio: 6 batsmen, 5 bowlers, 4 all-rounders, 1 WK
        ideal_balance = np.array([6, 5, 4])
        current_balance = np.array([batsmen, bowlers, allrounders])
        
        balance_error = np.sum(np.abs(ideal_balance - current_balance))
        balance_score = 1.0 - (balance_error / 15.0)
        
        return balance_score
    
    def render(self, mode='human'):
        print(f"Round {self.auction_round}: Budget: {self.budget_remaining:.2f}, "
              f"Players: {len(self.players_selected)}, Spent: {self.total_spent:.2f}")


class AuctionAgent:
    """
    RL Agent for Auction Strategy
    """
    
    def __init__(self, env):
        self.env = env
        
        # Try PPO first (better for continuous-like decisions)
        try:
            self.model = PPO(
                policy="MlpPolicy",
                env=env,
                verbose=1,
                tensorboard_log="./logs/auction_ppo/",
                learning_rate=3e-4,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95
            )
            self.algorithm = "PPO"
        except Exception as e:
            print(f"PPO initialization failed: {e}")
            print("Falling back to DQN...")
            
            self.model = DQN(
                policy="MlpPolicy",
                env=env,
                verbose=1,
                tensorboard_log="./logs/auction_dqn/",
                learning_rate=1e-4,
                buffer_size=100000,
                batch_size=64,
                gamma=0.99,
                exploration_fraction=0.1,
                exploration_final_eps=0.02
            )
            self.algorithm = "DQN"
    
    def train(self, total_timesteps=100000):
        """Train the agent"""
        
        print(f"\nTraining {self.algorithm} agent for {total_timesteps} timesteps...")
        
        self.model.learn(total_timesteps=total_timesteps)
        
        # Save model
        self.model.save("models/saved_models/auction_rl_agent")
        
        print(f"✅ Training completed! Model saved.")
    
    def predict_action(self, observation):
        """Predict best action for given state"""
        
        action, _states = self.model.predict(observation, deterministic=True)
        return action
    
    def simulate_auction(self, verbose=True):
        """Simulate complete auction with trained agent"""
        
        obs, _ = self.env.reset()
        done = False
        total_reward = 0
        
        if verbose:
            print("\n=== Simulating Auction ===")
        
        while not done:
            action = self.predict_action(obs)
            
            obs, reward, done, truncated, info = self.env.step(action)
            total_reward += reward
            
            if verbose and action != 0:  # Only show bids
                self.env.render()
        
        if verbose:
            print(f"\nAuction Complete!")
            print(f"Total Reward: {total_reward:.2f}")
            print(f"Players Selected: {len(self.env.players_selected)}")
            print(f"Budget Remaining: ₹{self.env.budget_remaining:.2f} Cr")
            print(f"Total Spent: ₹{self.env.total_spent:.2f} Cr")
        
        return {
            'total_reward': total_reward,
            'players_selected': self.env.players_selected,
            'budget_remaining': self.env.budget_remaining,
            'total_spent': self.env.total_spent
        }


def generate_synthetic_players(n_players=622):
    """Generate synthetic player data for training"""
    
    roles = ['Batsman', 'Bowler', 'All-rounder', 'Wicket-keeper']
    
    data = {
        'player_name': [f'Player_{i}' for i in range(n_players)],
        'role': np.random.choice(roles, n_players),
        'sold_price': np.random.uniform(0.5, 20.0, n_players),
        'overall_impact': np.random.uniform(20, 100, n_players),
        'consistency_rating': np.random.uniform(30, 90, n_players)
    }
    
    return pd.DataFrame(data)


def main():
    """Main training pipeline"""
    
    print("=== RL Auction Agent Training ===\n")
    
    # Generate player data
    players_df = generate_synthetic_players()
    print(f"Generated {len(players_df)} players")
    
    # Create environment
    env = AuctionEnvironment(players_df, initial_budget=120.0, max_players=25)
    
    # Validate environment
    print("Validating environment...")
    check_env(env, warn=True)
    
    # Create agent
    agent = AuctionAgent(env)
    
    # Train agent
    agent.train(total_timesteps=50000)
    
    # Simulate auction
    results = agent.simulate_auction(verbose=True)
    
    # Analyze selected team
    if len(results['players_selected']) > 0:
        selected_df = pd.DataFrame(results['players_selected'])
        
        print("\n=== Selected Team Analysis ===")
        print(f"Average Impact: {selected_df['overall_impact'].mean():.1f}")
        print(f"Role Distribution:")
        print(selected_df['role'].value_counts())
    
    print("\n✅ RL Auction Agent training completed!")
    
    return agent, results


if __name__ == "__main__":
    agent, results = main()
