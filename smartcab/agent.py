import random
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

'''
1. Basic Agent Simulation 
Only change the following arguments: enforce_deadline, update_delay, log_metrics, n_test
and implement choose_action()
'''

'''
2. Default Learning Agent:
Set the states for the agent and implement all TODOs
Set learning = True
Set decay function => epsilon = epsilon - 0.005
'''

'''
3. Optimized Learning Agent: 
Set optimized=True
and change the decay function
Modify the alpha, epsilon and tolerance
'''

'''
Resource(s): 
[1]: https://medium.com/@m.alzantot/deep-reinforcement-learning-demysitifed-episode-2-policy-iteration-value-iteration-and-q-978f9e89ddaa
'''

class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """ 

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5):
        super(LearningAgent, self).__init__(env)     # Set the agent in the evironment 
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning # Whether the agent is expected to learn
        self.Q = dict()          # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon   # Random exploration factor
        self.alpha = alpha       # Learning factor

        self.t = 0 #Initialize the number of trials


    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)

        # Update epsilon using a decay function of your choice
        # Update additional class parameters as needed
        # If 'testing' is True, set epsilon and alpha to 0
        if testing:
            self.epsilon = 0
            self.alpha = 0
        else:
            # Need to decrease the exploration factor with the increase of number of trials
            # Basic learning decay function
            # f(x) = e - 0.05
            # self.epsilon = self.epsilon - 0.05
            # Optimized learning decay function
            # f(x) = 1/t^2
            self.t = self.t + 1 # Update the number of trials
            self.epsilon = 1/math.pow(self.t, 2)
            # f(x) = cos(alpha * t)
            # self.epsilon = math.cos(self.alpha * self.t)
            # f(x) = a ^ t
            # self.epsilon = math.pow(self.alpha, self.t)
            # f(x) = e ^ -at
            # self.epsilon = math.exp(-(self.alpha * self.t))

        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
            environment. The next waypoint, the intersection inputs, and the deadline 
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint() # The next waypoint 
        inputs = self.env.sense(self)           # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline

        # NOTE : you are not allowed to engineer eatures outside of the inputs available.
        # Because the aim of this project is to teach Reinforcement Learning, we have placed 
        # constraints in order for you to learn how to adjust epsilon and alpha, and thus learn about the balance between exploration and exploitation.
        # With the hand-engineered features, this learning process gets entirely negated.
        
        # Set 'state' as a tuple of relevant data for the agent
        # light => Traffic light
        # oncoming => the direction of any oncoming traffic in an intersection
        state = (inputs['light'], inputs['oncoming'], inputs['left'], waypoint)

        return state


    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        #TODO: Try to implement the tie breaker here.
        # Calculate the maximum Q-value of all actions for a given state
        return max(self.Q[state].values())


    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        # When learning, check if the 'state' is not in the Q-table
        if self.learning:
            if not self.Q.has_key(state):
                # If it is not, create a new dictionary for that state
                # Then, for each action available, set the initial Q-value to 0.0
                self.Q[state] = {}
                for action in self.valid_actions:
                    self.Q[state][action] = 0.0
                # Another solution => self.Q = {None: 0.0, 'right': 0.0, 'left': 0.0, 'forward': 0.0}
        return


    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        action = None

        if not self.learning:
            # If the agent is not learning then choose a random action
            action = random.choice(self.valid_actions)
        else:
            # When learning, choose a random action with 'epsilon' probability
            if random.random() < self.epsilon:
                action = random.choice(self.valid_actions)
                # numpy.random.choice(self.valid_actions, p=[self.epsilon])
            else:
                # Otherwise, choose an action with the highest Q-value for the current state
                max_actions_list = []
                for action in self.valid_actions:
                  if self.valid_actions:
                    if self.Q[state][action] >= self.get_maxQ(state):
                        max_actions_list.append(action)
                # Choose randomly among actions. (Tie breaker)
                action = random.choice(max_actions_list)

        return action


    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives a reward. This function does not consider future rewards 
            when conducting learning. """
        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')
        if self.learning:
            old_q_value = self.Q[state][action]
            max_q_value = self.get_maxQ(state)
            # Q(s,a) = oldQValue + alpha * (reward + discountFactor * maxQ(st, a) - oldQValue)
            # self.Q[state][action] = old_q_value + self.alpha * (reward - old_q_value)

            #Q(s,a) = (1 - alpha) * old_q_value + self.alpha * reward
            self.Q[state][action] = (1 - self.alpha) * old_q_value + self.alpha * reward
        return


    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()          # Get current state
        self.createQ(state)                 # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action) # Receive a reward
        self.learn(state, action, reward)   # Q-learn

        return
        

def run():
    """ Driving function for running the simulation. 
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment(verbose=True)
    
    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    agent = env.create_agent(LearningAgent, learning=True, alpha=0.4)
    
    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    env.set_primary_agent(agent, enforce_deadline=True)

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    sim = Simulator(env, update_delay=0.01, log_metrics=True, optimized=True)
    
    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05 
    #   n_test     - discrete number of testing trials to perform, default is 0
    sim.run(n_test=20, tolerance=0.0000003)


if __name__ == '__main__':
    run()
