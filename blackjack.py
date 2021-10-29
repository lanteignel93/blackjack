import numpy as np
import random
import time
import matplotlib.pyplot as plt
import sys
import warnings

if not sys.warnoptions:
     warnings.simplefilter("ignore")

class Blackjack:
    def __init__(self):
        self.states = None
        self.actions = ['hit', 'stand']
        self.cards = {'A': 11,
                      '2': 2,
                      '3': 3,
                      '4': 4,
                      '5': 5,
                      '6': 6,
                      '7': 7,
                      '8': 8,
                      '9': 9,
                      '10': 10,
                      'J': 10,
                      'Q': 10,
                      'K': 10}
        self.rewards = None
        self.q_rewards = None
        self.q_values = None
        self.policy = None


    def get_action(self):
        return self.actions

    def get_states(self):
        return self.states

    def get_cards(self):
        return self.cards

    def get_rewards(self):
        return self.rewards

    def get_q_rewards(self):
        return self.q_rewards

    def get_q_values(self):
        return self.q_values

    def get_policy(self):
        return self.policy

    def init_states(self):
        states = [{'cards':cards, 'usable_ace':usable_ace, 'dealer_card':dealer_card}
        for cards in range(12,22)
        for usable_ace in [True,False]
        for dealer_card in range(2,12)]
        self.states = states
        return None

    def init_rewards(self):
        rewards = {}
        for s in self.get_states():
            tmp = [v for k,v in s.items()]
            rewards[tuple(tmp)] = {'count':0, 'reward':0}

        self.rewards = rewards
        return None


    def init_q_rewards(self):
        rewards = {}
        Q = {}
        for s in self.get_states():
            tmp = [v for k,v in s.items()]
            for a in self.get_action():
                rewards[tuple(tmp), a] = {'count':0, 'reward':0}
                Q[tuple(tmp), a] = 0

        self.q_values = Q
        self.q_rewards = rewards
        return None


    def random_card(self):
        card = random.choice(list(self.get_cards().keys()))
        return self.get_cards()[card]

    def hit(self, msg, hand):
        curr_card = hand['cards']
        is_usable_ace = hand['usable_ace']
        new_card = self.random_card()
        new_hand = {'cards': curr_card + new_card, 'usable_ace': is_usable_ace}

        if is_usable_ace and new_hand['cards'] > 21:
            new_hand['cards'] -= 10
            new_hand['usable_ace'] = False

        else:
            if new_card == 11 and new_hand['cards'] <= 21:
                new_hand['usable_ace'] = True
            elif new_card == 11 and new_hand['cards'] > 21:
                new_hand['cards'] -= 10
                new_hand['usable_ace'] = False
        return new_hand

    def deal(self):
        natural = False
        first_card = self.random_card()
        second_card = self.random_card()
        sum_cards = first_card + second_card
        is_Ace = first_card == 11 or second_card == 11

        if sum_cards > 21:
            sum_cards -= 10
        player_hand = {'cards':sum_cards, 'usable_ace':is_Ace}

        if player_hand['cards'] == 21 and player_hand['usable_ace'] == True:
            natural = True

        while player_hand['cards'] < 12:
            new_hand = self.hit('deal',player_hand)
            player_hand = new_hand

        dealer_hidden_card = self.random_card()
        dealer_show_card = self.random_card()

        env = {'player hand': player_hand,
               'natural': natural,
               'dealer_hidden': dealer_hidden_card,
               'dealer_show': dealer_show_card}

        return env


    def play_hand(self, hand, action, dealer_hand):
        player = hand
        dealer = dealer_hand
        if action == 'stand':
            while dealer['cards'] < 17:
                new_hand = self.hit('dealer hit',dealer)
                dealer = new_hand
            if dealer['cards'] > 21 or dealer['cards'] < hand['cards']:
                return (1, 'Game Over')

            elif dealer['cards'] == player['cards']:
                return (0, 'Game Over')

            else:
                return (-1, 'Game Over')

        else:
            new_hand = self.hit('player hit',player)
            player = new_hand
            if player['cards'] > 21:
                return (-1, 'Game Over')

            else:
                return (player, 'Continue')


    def policy_valuation(self, state, rewards, implied_prob = False):
        (count,total_reward) = rewards[state]['count'], rewards[state]['reward']
        if count == 0:
            return 0
        else:
            if not implied_prob:
                return total_reward/count
            else:
                return(count+total_reward)/(2*count)

    def print_q_policy_val(self):
        for k,v in self.get_q_rewards().items():
            print(k, self.policy_valuation(k, self.get_q_rewards()))


    def play_new_game(self):
        curr_env = self.deal()
        player_hand = curr_env['player hand']
        natural = curr_env['natural']
        dealer_hidden_card = curr_env['dealer_hidden']
        dealer_show_card = curr_env['dealer_show']
        dealer_sum_card = dealer_hidden_card + dealer_show_card

        game_state = {'Player Hand': player_hand,
                      'Init Action': None,
                      'Dealer Hand': dealer_show_card,
                      'Outcome': None}

        if natural:
            game_state['Init Action'] = 'stand'
            if dealer_sum_card < 21:
                game_state['Outcome'] = 1.5
            else:
                game_state['Outcome'] = 0
            return game_state

        else:
            if dealer_sum_card == 21:
                game_state['Outcome'] = -1
                game_state['Init Action'] = 'stand'
                return game_state
            else:
                dealer_state = {'cards': dealer_sum_card,
                                'usable_ace': False}
            action = np.random.choice(self.get_action())
            game_state['Init Action'] = action
            game_status = 'Continue'

            outcome = self.play_hand(player_hand, action, dealer_state)

            if outcome[1] == 'Game Over':
                game_state['Outcome'] = outcome[0]
                return game_state
            else:
                player_hand = outcome[0]
                game_status = 'Continue'

                while game_status == 'Continue':
                    action = self.get_policy()[(player_hand['cards'], player_hand['usable_ace'],dealer_show_card)]
                    outcome = self.play_hand(player_hand, action, dealer_state)
                    if type(outcome[0]) == int:
                        game_status = outcome[1]
                        break
                    player_cards, usable_ace_state = outcome[0]['cards'], outcome[0]['usable_ace']
                    player_hand['cards'] = player_cards
                    player_hand['usable_ace'] = usable_ace_state

                    game_status = outcome[1]

            game_outcome = outcome[0]
            game_state['Outcome'] = game_outcome

        return game_state

    def init_policy(self):
        pol = {}
        for s in self.get_states():
            tmp = [v for k,v in s.items()]
            pol[tuple(tmp)] = np.random.choice(self.get_action())
        self.policy = pol


    def get_q_action(self, state):
        Q = self.get_q_values()
        return self.get_action()[np.argmax([Q[state, 'hit'], Q[state,'stand']])]


    def monte_carlo_q_sim(self, iter):
        t1 = time.time()
        for epoch in range(iter):
            if epoch % (iter//10) == 0 and epoch >0:
                t2 = time.time()
                print('{}% Complete in {:.3f}s'.format(int(100*epoch/iter),t2-t1))
            game_outcome = self.play_new_game()
            player = game_outcome['Player Hand']
            dealer = game_outcome['Dealer Hand']
            init_action = game_outcome['Init Action']
            outcome = game_outcome['Outcome']

            key, action = (player['cards'], player['usable_ace'], dealer) , init_action


            self.get_q_values()[key, action] = (self.get_q_rewards()[key, action]['reward'] +
            outcome)/(self.get_q_rewards()[key, action]['count'] + 1)

            self.get_q_rewards()[key, action]['reward'] += outcome
            self.get_q_rewards()[key, action]['count'] += 1

            self.get_policy()[key] = self.get_q_action(key)

        return None

    def optimal_policy(self, implied_prob = False):
        opt = {}
        for s in self.get_states():
            player = s['cards']
            ace = s['usable_ace']
            dealer = s['dealer_card']
            key = (player, ace, dealer)

            action_val = {}
            for a in self.get_action():
                top_action = None
                val = self.policy_valuation((key,a),self.get_q_rewards(), implied_prob)
                action_val[a] = val

            curr_max = -np.inf
            for k, v in action_val.items():
                if v > curr_max:
                    curr_max = v
                    top_action = k
                opt[key] = (top_action, curr_max)

        return opt


    def plot_optimal_policy(self, is_ace = False):

        opt = self.optimal_policy(implied_prob = True)

        fig = plt.figure(figsize=(12,12))
        ax = fig.add_subplot(111)
        data = np.empty((10,10)) * np.nan
        cax = ax.matshow(data, cmap = 'binary')
        is_ace = False
        for j in range(10):
            for i in range(10):
                state_val = opt[(i+12,is_ace,j+2)]
                action, prob = state_val[0], state_val[1]
                prob = '{:.2f}%'.format(100*prob)
                if action == 'hit':
                    c = 'firebrick'
                else:
                    c = 'forestgreen'
                ax.fill_between([i,i+1], j, j+1, facecolor=c)
                ax.text(i+0.5, j+0.5, prob, color='black', ha='center', va='center', fontsize = 12,
                    bbox=dict(boxstyle='round', facecolor='white', edgecolor='black'))

        extent = (0,10,10,0)
        ax.set_xticks(np.arange(0,10,1))
        ax.set_yticks(np.arange(0,10,1))
        ax.set_xticklabels(np.arange(12,22,1), fontsize = 12)
        ax.set_yticklabels(np.arange(2,12,1), fontsize = 12)
        ax.set_xlabel("Players Card", fontsize = 16)
        ax.xaxis.set_label_position('top')
        ax.set_ylabel("Dealer's Cards", fontsize = 16)
        ax.grid(which = 'major', color='k',lw=2)
        ax.imshow(data, extent=extent)
        plt.show()

    def init_game(self):
        self.init_states()
        self.init_rewards()
        self.init_policy()
        self.init_q_rewards()
