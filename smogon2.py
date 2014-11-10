import requests
import json
from pokemon import Pokemon

class Smogon():
    BASE_URL = "http://www.smogon.com/dex/api/query"
    def __init__(self):
        self.url = self.BASE_URL

    def get_pokemon_info(self, pokemon):
        moveset_fields = ["name", "alias", {"movesets":["name",
                                                {"items":["alias","name"]},
                                                {"abilities":["alias","name","gen"]},
                                                {"evconfigs":["hp","patk","pdef","spatk","spdef","spe"]},
                                                {"natures":["hp","patk","pdef","spatk","spdef","spe"]},
                                                {"$groupby":"slot","moveslots":["slot",{"move":["name","alias","gen"]}]},"description"]},{"moves":["name","alias","gen","category","power","accuracy","pp","description",{"type":["alias","name","gen"]}]}
                                                ]
        moveset_query = {"pokemon":{"gen":"xy","alias":"%s" % pokemon}, "$": moveset_fields}
        moveset_params = {"q": json.dumps(moveset_query)}
        moveset_output = requests.get(self.url, params=moveset_params)
        moveset_output = moveset_output.json()
        typing_fields = ["name","alias","gen",{"types":["alias","name","gen"]}]
        typing_query = {"pokemonalt":{"gen":"xy","alias":"%s" % pokemon}, "$": typing_fields}
        typing_params = {"q": json.dumps(typing_query)}
        typing_output = requests.get(self.url, params=typing_params)
        typing_output = typing_output.json()
        return moveset_output, typing_output

    def convert_to_pokemon(self, moveset_output, typing_output):
        moveset_results = moveset_output['result']
        movesets = moveset_results[0]['movesets']
        poke_movesets = []
        for moveset in movesets:
            name = moveset['name']
            ability = moveset['abilities'][0]['alias']
            item = moveset['items'][0]['alias']
            evs = moveset['evconfigs'][0]
            moveslots = moveset['moveslots']
            nature = moveset['natures'][0]
            moves = []
            for moveslot in moveslots:
                for move in moveslot['moves']:
                    moves.append(move['alias'])
            moves = moves
            poke_moveset = SmogonMoveset(name, item, ability, evs, nature, moves)
            poke_movesets.append(poke_moveset)
        type_list = []
        typing_results = typing_output['result']
        types = typing_results[0]['types']
        for poke_type in types:
            type_list.append(poke_type['alias'])
        poke = SmogonPokemon(type_list, poke_movesets)
        return poke
        #for moveset in movesets:
            #print moveset['name']

class SmogonPokemon():
    def __init__(self, typing, movesets):
        #self.name = name
        self.typing = typing
        self.movesets = movesets
    def set_name(self, name):
        self.name = name
    def set_typing(self, typing):
        self.typing = typing
    def set_movesets(self, movesets):
        self.movesets = movesets

class SmogonMoveset():
    def __init__(self, name, item, ability, evs, nature, moves):
        self.name = name
        self.item = item
        self.ability = ability
        self.evs = evs
        self.nature = nature
        self.moves = moves
    def set_name(self, name):
        self.name = name
    def set_item(self, item):
        self.item = item
    def set_ability(self, ability):
        self.ability = ability
    def set_evs(self, evs):
        self.evs = evs
    def set_nature(self, nature):
        self.nature = nature
    def set_moves(self, moves):
        self.moves = moves

if __name__ == "__main__":
    smogon = Smogon()
    name = "infernape"
    typing, movesets = smogon.get_pokemon_info(name)
    poke = smogon.convert_to_pokemon(typing, movesets)
    print poke.typing
    #poke = smogon.convert_to_pokemon(output)
    #print poke.movesets[0].nature