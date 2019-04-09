#!/usr/bin/env python

import random
import uuid
import requests
import time
import json

numplayers = 200
starttime = int(time.time()) + 1

hostname = 'http://localhost:5000/'

redt = "\033[1;31;40m"
greent = "\033[1;32;40m"
yellowt = "\033[1;33;40m"
regulart = "\033[0;37;40m"


def genname():
    prefix = ('Battle',
              'Mecha',
              'Riot',
              'Iron',
              'MEGA',
              'Heavy',
              'Rust',
              'Surreal',
              'Immortal',
              'Mad',
              'Neo',
              "Devil's",
              'Psycho')
    nm = ('Crusher',
          'Annihilator',
          'Machine',
          'Desintegrator',
          'Killer',
          'Destroyer',
          'Terminator',
          'Exterminator',
          'Destructor')
    postfix = ('OfHorror',
               'Terrorist',
               'FromHell',
               '-2000',
               '-3000',
               '-9000',
               '-2001',
               '666',)
    return random.choice(prefix)+random.choice(nm)+random.choice(postfix)


players = []
for i in range(numplayers):
    player = {'name': genname(),
              'id': uuid.uuid4(),
              'power': random.randint(1, 1000),
              'medals': 1000,
              'money': 0,
              }
    players.append(player)

print('Trying to add {} random players'.format(numplayers))
for p in players:
    r = requests.post(hostname + "player/", data=p)
    # print(r.status_code, r.reason)
    # print(r.text)
    result = json.loads(r.text)
    if result['success']:
        print('{} {} {}'.format(greent, result['result'], regulart))
    else:
        print('{} {} {}'.format(redt, result['error'], regulart))

r = requests.post(hostname + "tournament/",
                  data={'start_timestamp': starttime}
                  )
# print(r.status_code, r.reason)
print(r.text)

finished = False
r = requests.get(hostname + "tournament/",)
if json.loads(r.text)['status'][0] == 1:
    finished = True

while not finished:
    r = requests.get(hostname + "tournament/",)
    if json.loads(r.text)['status'][0] == 1:
        finished = True

    from_player_id = str(random.choice(players)['id'])
    print('Searching opponent for {}'.format(from_player_id))
    r = requests.get(hostname + "opponent/",
                     data={'player_id': from_player_id})
    # print(r.status_code, r.reason)
    # to_player_id = str(random.choice(players)['id'])
    try:
        result = json.loads(r.text)
        if result['success']:
            # print(result)
            print('{} FOUND opponent for {} {}'.format(greent,
                                                       from_player_id,
                                                       regulart))
            to_player_id = json.loads(r.text)['opponent_id']

            print('Try to ATTACK from {} to: {}'.format(from_player_id,
                                                        to_player_id))
            try:
                r = requests.post(hostname + "attack/",
                                  data={'from_player_id': from_player_id,
                                        'to_player_id': to_player_id})
                # print(r.text)
                a_result = json.loads(r.text)
                if a_result['success']:
                    print('{} {} {}'.format(yellowt,
                                            a_result['result'],
                                            regulart))
                else:
                    print('{} FAILED with {} {}'.format(redt,
                                                        a_result['error'],
                                                        regulart))
            except Exception as e:
                print('{} FAILED with {} {}'.format(redt, e, regulart))
            # print(r.status_code, r.reason)
        else:
            print('{} FAILED with {} {}'.format(redt,
                                                result['error'],
                                                regulart))
    except Exception as e:
        print(e)

r = requests.get(hostname + "tournament/",)

players = json.loads(r.text)['players']
for group in json.loads(r.text)['players']:
    print('\n{} Results in group {}: {}'.format(yellowt, group, regulart))
    print('{}id Name{}Medals  Money  Power'.format(' '*34, ' '*28))
    for p in players[group]:
        namestr = p['name'] + (' ' * (32 - len(p['name'])))
        medalstr = str(p['medals']) + ' ' * (8 - len(str(p['medals'])))
        moneystr = str(p['money']) + ' ' * (7 - len(str(p['money'])))
        pstr = str(p['id']) + ' ' + str(namestr)
        pstr += str(medalstr) + str(moneystr) + str(p['power'])
        print(pstr)

