#=*- coding: utf-8 -*-
import sys
class RedBlue_Nim:
    def __init__(self, red_marbles, blue_marbles, version = 'standard', first_player = 'computer'):
        self.red_marbles = red_marbles
        self.blue_marbles = blue_marbles
        self.version = version
        self.current_player = first_player.capitalize()
        
        
        print(f"Initializing Red-Blue Nim Game in {self.version.capitalize()} mode with {self.current_player} as starting player.....")
        print(f"Starting with {red_marbles} Red Marbles and {blue_marbles} Blue Marbles.")

    def switch_btw_player(self):
        switch_player = {'computer': 'human', 'human': 'computer'}
        self.current_player = switch_player[self.current_player.lower()]

    #Possible Moves for the versions
    def possible_moves(self):
        move_ordering = {
            'standard': [('red', 2), ('blue', 2), ('red', 1), ('blue', 1)],
            'misere': [('blue', 1), ('red', 1), ('blue', 2), ('red', 2)]
        }

        order = move_ordering[self.version]
        move = []
        for color, marble_count in order:
            if getattr(self, f'{color}_marbles') >= marble_count:
                move.append((color, marble_count))

        return move

    #Implementing computer side moves
    def computer_turn(self):
        print("Computer's turn - Evaluating moves .....")
        init_scores = {'standard':float('inf'), 'misere': float('-inf')}
        bestscore = init_scores[self.version]
        best_move = None

        for poss_move in self.possible_moves():
            self.make_move(*poss_move)
        # Temporarily switch the player to evaluate the move's impact from the opponent's perspective
            self.switch_btw_player()
            movescore = self.eval_function()  # Directly use evaluate_state to assess the move
            self.undo_a_move(*poss_move)
        # Switch back the player to continue evaluation from the computer's perspective
            self.switch_btw_player()

        # For the standard version, lower scores (opponent's perspective) are preferred; for mis?re, higher scores are preferred
            if(self.version == 'standard' and movescore < bestscore) or \
               (self.version == 'misere' and movescore > bestscore) or \
               (movescore == bestscore and not best_move):
                bestscore = movescore
                best_move = poss_move
        print(f"Computer's best move: {best_move} with score: {bestscore}")
        return best_move
      
    def human_prompt(self):
        pile_valid = False
        count_valid = False
        pile =''
        marble_count = 0
        #Validation for Pile
        while not pile_valid:
            pile = input("Enter pile (red/blue): ").lower()
            if pile in ['red', 'blue']:
                pile_valid = True
            else:
                print("Ivalid pile selection. Please choose either 'red' or 'blue'.")
        #Validation for choosing marbles
        while not count_valid:
            input_count = input("""
            How many marbles will you take?
            1           2
         [ One ]     [ Two ]
         Enter count (1/2): 
         """)
            if input_count in ['1', '2']:
                count_valid = True
                marble_count = int(input_count)
            else:
                print("INVALID Count. You can either pick 1 or 2 marbles.")

        return pile, marble_count


    def make_move(self, pile, marble_count):
        map_pile = {'red': 'red_marbles', 'blue': 'blue_marbles'}
        if pile in map_pile:
            #Access the pile attribute, and update its count
            setattr(self, map_pile[pile], max(0, getattr(self, map_pile[pile]) - marble_count))

    def game_is_over(self):
        return self.red_marbles == 0 or self.blue_marbles == 0

    def border(self, msg):
        border_topbottom = '+' + '-' * (len(msg) + 4) + '+'
        line_empty = '|' + ' ' * (len(msg) + 4) + '|'
        win_line = f"|  {msg}  |"

        # Printing the final score in a creative way
        print(f"\n{border_topbottom}\n{line_empty}\n{win_line}\n{line_empty}\n{border_topbottom}\n")
    
    #Final Score calculation
    def cal_final_score(self):
        fscore = 2 * self.red_marbles + 3 * self.blue_marbles
        conditions ={
            'standard': {
                'computer': f"Computer lOSES with a score of {fscore}.",
                'human': f"Human LOSES with a score of {fscore}."
                },
            'misere': {
                'computer': f"Computer WINS with a score of {fscore}.",
                'human': f"Human WINS with a score of {fscore}."
                }
            }
        msg = conditions[self.version][self.current_player]
        self.border(msg)
           
    #Print the state
    def print_state(self):
        redmarble_count = '(R)'
        bluemarble_count = '(B)'
        display_redmarblecount = ' '.join([redmarble_count for _ in range(self.red_marbles)])
        display_bluemarblecount = ' '.join([bluemarble_count for _ in range(self.blue_marbles)])
        print(f"\nRed Marbles: {display_redmarblecount}\nBlue Marbles: {display_bluemarblecount}\n")

    #Play the game
    def play_game(self):
        methods_to_move = {
            'computer': self.computer_turn,
            'human': self.human_prompt}
        while not self.game_is_over():
            self.print_state()
            pile, marble_count = methods_to_move[self.current_player.lower()]()
            print("--------------------------------------------")
            print(f"{self.current_player} removes {marble_count} marble(s) from {pile} pile.")
            print("--------------------------------------------")

            self.make_move(pile, marble_count)

            if self.game_is_over():
                self.cal_final_score()
                print("*** GAME OVER ***\n Thankyou for playing Red-Blue Nim Game.\n")
                return
            self.switch_btw_player()

    #Undo Move
    def undo_a_move(self, pile, marble_count):
        piles = { 'red': 'red_marbles', 'blue': 'blue_marbles'}
        if pile in piles:
            setattr(self, piles[pile], getattr(self, piles[pile]) + marble_count)

    #Evalaution Function
    def eval_function(self):
        #Goal is to maximize score leaving as many marbles as possible
        #Negative is for computer to lose, and positive - human
        if self.version == 'standard':
            return -(2 * self.red_marbles + 3 * self.blue_marbles)
        else:#For Misere it is better to have fewer marbles (options)
            return 2 * self.red_marbles + 3 * self.blue_marbles

    #For the decision making - To determine the best move to make and perform the move.
    #Min-Max with alpha-beta pruning is implemented
    def MinMaxwithAlphaBeta(self, alpha, beta, max_player):
        if self.game_is_over():
            return self.eval_function()

        if max_player:
            return self.maxi(alpha, beta, max_player)
        else:
            return self.mini(alpha, beta, max_player)
    #Maximizing Player
    def maxi(self, alpha, beta, max_player):
        maxi_eval = float('-inf')
        for moves in self.possible_moves():
            self.make_move(*moves)
            #Minmax is called recursively for opponent's turn by flipping perspectives
            #Negation - Adjust scores from minimizing perspective back to maximizing
            evaluation = -self.MinMaxwithAlphaBeta(-beta, -alpha, not max_player)
            #undo move to restore the game state for next possible move
            self.undo_a_move(*moves)
            if evaluation > maxi_eval:
                maxi_eval = evaluation
            if evaluation > alpha:
                alpha = evaluation
            #If the best possible outcome of current branch is worse than already found outcome, Prune it.
            if alpha >= beta:
                break
        return maxi_eval

    #Minimizing Player
    def mini(self, alpha, beta, max_player):
        mini_eval = float('inf')
        for moves in self.possible_moves():
            self.make_move(*moves)
            #Call Minmax to evaluate maximizing player's response, by flipping perspectives
            #Negation - Adjust score for maximizing perspective
            evaluation = -self.MinMaxwithAlphaBeta(-beta, -alpha, not max_player)
            self.undo_a_move(*moves)
            if evaluation < mini_eval:
                mini_eval = evaluation
            if evaluation < beta:
                beta = evaluation
            #Prune if higher score already found for maximizing player
            if beta <= alpha:
                break
        return mini_eval  

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error Usage!!! Expected Usage: red_blue_nim.py <num-red> <num-blue> <version> <first-player>")
        sys.exit(1)

    red_marbles = int(sys.argv[1])
    blue_marbles = int(sys.argv[2])
    version = sys.argv[3] if len(sys.argv) > 3 else 'standard'
    first_player = sys.argv[4] if len(sys.argv) > 4 else 'computer'

    redbluenim_game = RedBlue_Nim(red_marbles, blue_marbles, version, first_player)
    redbluenim_game.play_game()
    

            

