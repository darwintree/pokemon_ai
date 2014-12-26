from simulator import Action
import logging
logging.basicConfig()

class GameState():
    def __init__(self, teams):
        self.teams = teams

    def deep_copy(self):
        state = GameState([x.copy() for x in self.teams])
        return state

    def get_team(self, team):
        return self.teams[team]

    def to_tuple(self):
        return tuple(x.to_tuple() for x in self.teams)

    def evaluate(self, who):
        win_bonus = 0
        my_team = self.get_team(who)
        opp_team = self.get_team(1 - who)
        if self.is_over():
            if my_team.alive():
                win_bonus = 10000
            else:
                win_bonus = -10000
        my_team_health = sum([x.health/x.final_stats['hp'] for x in my_team.poke_list])
        opp_team_health = sum([x.health/x.final_stats['hp'] for x in opp_team.poke_list])
        my_team_death = len([x for x in my_team.poke_list if not x.alive])
        opp_team_death = len([x for x in opp_team.poke_list if not x.alive])
        if self.is_over():
            my_team_stages, opp_team_stages = 0, 0
        else:
            my_poke = my_team.primary()
            opp_poke = opp_team.primary()
            my_team_stages = my_poke.stages['spatk'] + my_poke.stages['patk']
            opp_team_stages = opp_poke.stages['spatk'] + opp_poke.stages['patk']
        return win_bonus + my_team_health - opp_team_health# - 0.5 * my_team_death + 0.5 * opp_team_death# + 0.07 * (my_team_stages - opp_team_stages)

    def is_over(self):
        return not (self.teams[0].alive() and self.teams[1].alive())

    def switch_pokemon(self, switch_index, who, log=False):
        my_team = self.get_team(who)
        opp_team = self.get_team(1 - who)
        my_team.set_primary(switch_index)
        my_poke = my_team.primary()
        opp_poke = opp_team.primary()
        if log:
            print (
                "%s switched in." % my_poke
            )
        if my_poke.ability == "Intimidate":
            if log:
                print ("%s got intimidated." % opp_poke)
            opp_poke.decrease_stage('patk', 1)

    def get_legal_actions(self, who):
        my_team = self.get_team(who)
        my_poke = my_team.primary()
        opp_team= self.get_team(1 - who)
        opp_poke = opp_team.primary()

        pokemon = range(len(my_team.poke_list))
        valid_switches = [i for i in pokemon if my_team.poke_list[i].alive and i != my_team.primary_poke]
        valid_backup_switches = valid_switches + [my_team.primary_poke]
        if len(valid_switches) == 0:
            valid_switches = [None]


        moves = []
        switches = []
        for move_index in range(len(my_poke.moveset.moves)):
            move_name = my_poke.moveset.moves[move_index]
            mega = my_poke.can_evolve()
            if my_poke.choiced:
                if move_name != my_poke.move_choice:
                    continue
            if move_name == "U-turn" or move_name == "Volt Switch":
                for j in valid_switches:
                    for k in valid_backup_switches:
                        if j == None:
                            moves.append(
                                Action(
                                    "move",
                                    move_index=move_index,
                                    mega=mega,
                                    volt_turn=j,
                                    backup_switch=None
                                )
                            )
                        elif j != None and k != None:
                            moves.append(
                                Action(
                                    "move",
                                    move_index=move_index,
                                    volt_turn=j,
                                    backup_switch=k,
                                    mega=mega
                                )
                            )
            else:
                moves.extend([
                    Action("move", move_index=move_index, mega=mega, backup_switch=j)
                    for j in valid_switches
                ])
        switches.extend([Action("switch", switch_index=i, backup_switch=j) for i in valid_switches for j in valid_backup_switches if j != i and i is not None])

        if opp_poke.ability == "Magnet Pull" and "Steel" in my_poke.typing and "Ghost" not in my_poke.typing:
            switches = []
        elif my_poke.ability == "Shadow Tag" and "Ghost" not in opp_poke.typing:
            switches = []
        elif my_poke.ability == "Arena Trap" and "Ghost" not in opp_poke.typing and "Flying" not in opp_poke.typing:
            switches = []
        return moves + switches