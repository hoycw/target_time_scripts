instr_strs = ['This is a simple (but not easy!) timing game. A light will move around this circle.',
               'Your goal is to respond at the exact moment when it completes the circle.',
               "The light always starts at the bottom and moves at the same speed,\n"+\
               'so the perfect response will always be at the same time: the Target Time!',
#                   '                                                               '+\
               'The gray bar at the bottom is the target zone.',
               'If you respond in the target zone, it will turn green and you win points!',
               'If you miss the target zone, it will turn red and you lose points.',
               "Let's get started with a few examples..."]
train_str = {'easy': "Good job! From now on, only the first part of the circle will light up.",
                    "That means you need to time your response without seeing the light go all the way around.",
                    "Let's try some more examples...",
             'hard': "Great, now you're ready to try the hard level!",
                    "Don't get discouraged - hard levels are designed to make you miss most of the time.\n"+\
                    "Challenge yourself to see how many you can win!",
                    "Let's try some examples..."}
main_str = "Ready to try the real deal? We'll start keeping score now."+\
            "You'll do {0} easy and {0} hard blocks, each lasting {1} trials.\n".format(n_blocks,n_trials)+\
            'Press Q/escape to do more practice rounds first,\n'+\
            'or press {0} to start playing Target Time!'.format(key)
