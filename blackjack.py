import numpy as np
import random

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

    def get_action(self):
        return self.actions

    def get_states(self):
        return self.states

    def get_cards(self):
        return self.cards

    def init_states(self):
        states = [{'cards':cards, 'usable_ace':usable_ace, 'dealer_card':dealer_card}
        for cards in range(12,22)
        for usable_ace in [True,False]
        for dealer_card in range(2,12)]
        self.states = states

        return None

    def random_card(self):
        card = random.choice(list(self.get_cards().keys()))
        return self.get_cards()[card]

    def hit(self, hand):
        curr_card = hand['cards']
        is_usable_ace = hand['usable_ace']
        new_card = self.random_card()
        new_hand = curr_card + new_card

        if is_usable_ace:
            if new_hand > 21:
                new_hand = (new_hand, False)
            else:
                new_hand = (new_hand, True)

        else:
            if new_card == 11 and curr_card + 11 <= 21:
                new_hand = (new_hand, True)
            elif new_card == 11 and curr_card + 11 > 21:
                new_hand = (new_hand-10, False)
            else:
                new_hand = (new_hand, is_usable_ace)

        new_hand = {'cards': new_hand[0], 'usable_ace': new_hand[1]}
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

        if player_hand == (21, True):
            natural = True

        if sum_cards < 12:
            while sum_cards < 12:
                player_hand = self.hit(player_hand)
                sum_cards = player_hand['cards']

        dealer_hidden_card = self.random_card()
        dealer_show_card = self.random_card()

        env = {'player hand': player_hand,
               'natural': natural,
               'dealer_hidden': dealer_hidden_card,
               'dealer_show': dealer_show_card}

        return env


    def play_hand(self, hand, action, dealer_hand):

        if action == 'stand':
            while dealer_hand['cards'] < 17:
                dealer_hand = self.hit(dealer_hand)

            if dealer_hand['cards'] > 21 or dealer_hand['cards'] < hand['cards']:
                return (1, 'Game Over')

            elif dealer_hand['cards'] == hand['cards']:
                return (0, 'Game Over')

            else:
                return (-1, 'Game Over')

        else:
            hand = self.hit(hand)
            if hand['cards'] > 21:
                return (-1, 'Game Over')

            else:
                return (hand, 'Continue')

    def play_game(self, policy):
        curr_env = self.deal()
        player_hand = curr_env['player hand']
        natural = curr_env['natural']
        dealer_hidden_card = curr_env['dealer_hidden']
        dealer_show_card = curr_env['dealer_show']
        dealer_sum_card = dealer_hidden_card + dealer_show_card

        game_state = {'Player Hand': player_hand,
                      'Dealer Hand': dealer_show_card,
                      'Outcome': None}

        policy_state = player_hand
        policy_state['dealer_card'] = dealer_show_card

        if natural:
            if dealer_sum_card < 21:
                game_state['Outcome'] = 1
            return game_state

        else:
            if dealer_sum_card == 21:
                game_state['Outcome'] = -1
                return game_state
            else:
                dealer_state = {'cards': dealer_sum_card,
                                'usable_ace': False}
            action = policy(policy_state)
            game_status = 'Continue'

            outcome = self.play_hand(player_hand, action, dealer_state)

            if outcome[1] == 'Game Over':
                game_state['Outcome'] = outcome[0]
                return game_state
            else:
                player_hand = outcome[0]
                game_status = 'Continue'

                while game_status == 'Continue':
                    action = policy(policy_state)
                    outcome = self.play_hand(player_hand, action, dealer_state)
                    if type(outcome[0] == int):
                        game_status = outcome[1]
                        break
                    player_cards, usable_ace_state = outcome[0]['cards'], outcome[1]['usable_ace']
                    policy_state['cards'] = player_cards
                    policy_state['usable_ace'] = usable_ace_state
                    game_status = outcome[1]

            game_outcome = outcome[0]
            game_state['Outcome'] = game_outcome

        return game_state


    def stupid_policy(self, state):
        if state['cards'] < 20:
            return 'hit'
        else:
            return 'stand'


game = Blackjack()
game.init_states()
for k in range(10):
    print('After', game.play_game(game.stupid_policy))
