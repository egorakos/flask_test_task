#!/usr/bin/env python

import time
from operator import itemgetter
import random
from flask import (Flask,
                   request,
                   make_response,
                   jsonify,)

app = Flask(__name__)

at = None


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class Tournament():
    def __init__(self):
        """Constructor"""
        self.players = []
        self.active = False
        self.starttime = None
        self.duration = 2 * 60
        self.finished = False
        self.counted = False
        self.groupsize = 50

    def refresh(self):
        self.__init__()

    def get_player(self, uid):
        """ Returns player by id"""
        try:
            return next(item for item in self.players if item["id"] == uid)
        except StopIteration:
            return None

    def is_groupmate(self, player1, player2):
        """ Is player1 and player2 belong to one group """
        if player1['group'] == player2['group']:
            return True
        else:
            return False

    def is_self_attack(self, player1, player2):
        """  """
        if player1['id'] == player2['id']:
            return True
        else:
            return False

    def can_attack_player(self, player1, player2):
        """ """
        if player1['id'] in player2.get('attacked_by', []):
            return False
        else:
            return True

    def can_attack_now(self, player, ct):
        """ Return True when no attack timelimit """
        last_attack = player.get('last_attack', None)
        if last_attack:
            attack_delta = time.time() - last_attack
            if attack_delta > 5:
                return True
            else:
                return False
        else:
            return True

    def finish(self):
        if not self.finished:
            self.active = False
            self.finished = True
            res = {}
            for p in self.players:
                try:
                    # print(p['group'])
                    if not p['group'] in res:
                        res[p['group']] = []
                    res[p['group']].append(p)
                except:
                    pass
            # print(res)
            for group in res:
                res[group] = sorted(res[group],
                                    key=itemgetter('medals'),
                                    reverse=True)
                res[group][0]['money'] += 300
                res[group][1]['money'] += 200
                res[group][2]['money'] += 100
            self.players = res

    def status(self):
        ct = time.time()
        if self.starttime:
            timeleft = ct - self.starttime
            if timeleft < 0:
                self.active = False
                return -1, '{} seconds to start'.format(round(timeleft, 4))
            elif timeleft > self.duration:
                self.finish()
                finishtime = str(self.starttime + self.duration)
                return 1, 'Tournament finished at {}'.format(finishtime)
            else:
                return 0, str(timeleft)
        else:
            return -1, 'Will be started soon'

    def get_opponent(self, uid):
        if self.status()[0] == 0:
            player = self.get_player(uid)
            candidates = [d for d in self.players if
                          d['group'] == player['group'] and
                          player['id'] not in d['attacked_by']]
            # print(candidates)
            try:
                return 0, random.choice(candidates)['id']
            except Exception as e:
                return 1, str(e)
        else:
            return self.status()

    def attack(self, uid1, uid2):
        if self.status()[0] == 0:
            player1, player2 = self.get_player(uid1), self.get_player(uid2)
            # print(uid1 + ' attack ' + uid2)
            ct = time.time()
            if not player1 and player2:
                return -1, "Cant't find players with given id's"
            elif self.is_self_attack(player1, player2):
                return -1, "{} can't attack themselve".format(uid1)
            elif not self.is_groupmate(player1, player2):
                return -1, "{} can't attack {}".format(uid1, uid2)
            elif not self.can_attack_player(player1, player2):
                return -1, '{} already attacked {}'.format(uid1, uid2)
            elif not self.can_attack_now(player1, ct):
                delta = abs(player1['last_attack'] - ct)
                return -1, "can't attack for {} seconds".format(delta)
            else:
                result = random.randint(-10, 10)
                player1['last_attack'] = ct
                player1['medals'] = int(player1['medals']) + result
                player2['medals'] = int(player2['medals']) - result
                player2['attacked_by'].append(uid1)
                if result <= 0:
                    return 0, 'attack falied with {} points'.format(abs(result))
                else:
                    return 0, 'attack succeed with {} points'.format(abs(result))
        else:
            return self.status()

    def start(self, timestamp):
        # Sort by power
        self.players = sorted(self.players,
                              key=itemgetter('power'),
                              reverse=True)
        # Can't add players since this:
        self.starttime = timestamp
        # for p in self.players:
        #     print(p)
        n = 0
        # add groups
        while (n) * self.groupsize < len(self.players):
            for p in self.players[n*self.groupsize:(n+1)*self.groupsize]:
                p['group'] = n+1
                p['attacked_by'] = []
                print(p)
            n += 1


@app.route('/player/', defaults={'uid': None}, methods=['POST'])
@app.route('/player/<uid>', methods=['GET'])
def player(uid):
    t = Tournament()
    print(t.status())
    if request.method == 'POST':
        if not t.active and not t.finished and not t.starttime:
            player = request.form.to_dict()
            player['power'] = int(player['power'])
            player['medals'] = int(player['medals'])
            player['money'] = int(player['money'])
            # print(player)
            t.players.append(player)
            result = 'Added player {} with {} of power'.format(player['name'],
                                                               player['power'])
            return make_response(jsonify({'success': True, 'result': result}))
        elif t.finished:
            error = "Can't add new player. Tournament finished."
            return make_response(jsonify({'success': False, 'error': error}))
        elif t.active:
            error = "Can't add new player while tournament in progress"
            return make_response(jsonify({'success': False, 'error': error}))
        elif t.starttime:
            error = 'Too late to add player. Tournament will be started soon'
            return make_response(jsonify({'success': False, 'error': error}))

    if request.method == 'GET':
        # print(uid)
        try:
            return make_response(jsonify({'player': t.get_player(uid),
                                          'success': True}))
        except Exception as e:
            return make_response(jsonify(str(e)), 500)


@app.route('/tournament/refresh', methods=['GET', ])
def refresh():
    t = Tournament()
    try:
        t.refresh()
        return make_response(jsonify({'success': True}))
    except Exception as e:
        return make_response(jsonify(str(e)), 500)


@app.route('/tournament/', methods=['GET', 'POST'])
def tournament():
    t = Tournament()
    if request.method == 'POST':
        tournament = request.form.to_dict()
        # print(tournament)
        if not t.starttime:
            t.start(int(tournament['start_timestamp']))
        return str(t.status())
    if request.method == 'GET':
        result = {'status': t.status(), 'players': t.players}
        return make_response(jsonify(result), 200)


@ app.route('/opponent/', methods=['GET'])
def opponent():
    t = Tournament()
    try:
        f = request.form.to_dict()['player_id']
        opponent = t.get_opponent(f)
        if opponent[0] == 0:
            return make_response(jsonify({'success': True,
                                          'opponent_id': opponent[1]}))
        else:
            return make_response(jsonify({'success': False,
                                          'error': opponent[1]}))
    except Exception as e:
        return make_response(jsonify({'success': False, 'error': str(e)}))


@ app.route('/attack/', methods=['POST'])
def attack():
    t = Tournament()
    try:
        f = request.form.to_dict()
        # print(f)
        uid1 = f['from_player_id']
        uid2 = f['to_player_id']
        attack = t.attack(uid1, uid2)
        if attack[0] == 0:
            return make_response(jsonify({'success': True,
                                          'result': attack[1]}))
        else:
            return make_response(jsonify({'success': False,
                                          'error': attack[1]}))
    except Exception as e:
        return make_response(jsonify({'success': False, 'error': str(e)}), 500)

