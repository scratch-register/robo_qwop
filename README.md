# Robo QWOP

An OpenAI Gym-compatible, human-playable game to teach a uniped to walk.

## BUT WHY?

Well, the short version is "WHY NOT?"

The long version is that, back in college, I had the thought that, by senior year, I ought to be able to make a bipedal robot that taught itself to walk via reinforcement learning.

Of course, this would be both extremely unrealistic, and extremely budget-unfriendly.

My dreams of creating and destroying hundreds of thousands of dollars worth of robotics hardware crushed, I turned to physical simulations.

Unfortunately, as it turns out, creating a realistic 3D physics simulator is really, really hard. Heck, even a 2D simulator isn't exactly a piece of cake. If I wanted to ever get to the reinforcement learning part of my project, I had to use something out-of-the-box. Out-of-the-`Box2D`, that is. -_cue crickets_-

So here we are! A Box2D + Pygame powered simulation of unipedal locomotion with elastic (ish) joints!

And it's QWOP-able! Learn how to do your very own jerky leg motions across a 2D field of grass in a simulated single-occupancy universe!

I know, I know. It's all incredibly exciting and you just can't wait to get started. So how do you use this thing?

## Usage

There are two different unipedal locomotion simlulations. (Yes, that's what the cook kids are calling our QWOP ripoffs now.)

One is a "kangaroo", which you will see specified in "kangaroo.py". It looks like a one-legged kangaroo, as you will see if you run the game.

The other is a "pogo" stick, which you will see specified in "pogo.py". It looks like a pogo stick with a mass at the top (which is suposed to represent the body).

### Running as a playable game

#### Kangaroo

```bash
# Run the python main() function to get the human-playable GUI
python3 kangaroo.py
```

Available commands:

- `x` - break all the joints and watch the poor simulated creature fall apart completely
- `r` - reset the game
- `q`, `w`, `o`, `p`, `e`,`i`, `left click` - controls for moving the unipedal creature

#### Pogo

```bash
# Run the python main() function to get the human-playable GUI
python3 pogo.py
```

Available commands:

- `x` - break all the joints and watch the poor simulated creature fall apart completely
- `r` - reset the game
- `q`, `w`, `o`, `p`, `left click` - controls for moving the unipedal creature


### Running for AI training

These games are compatible with the OpenAI Gym APIs, and you only need to import the relevant file to train an AI on the game. (The relevant files being `kangaroo.py` and `pogo.py`.)

## Ok, but your code is spaghetti. Like, reading it is an even worse experience than playing your horrible game.

Believe me, I know. Like I said, it was made for a college project.

I had some thoughts after the project to clean up the code and actually contribute it to OpenAI Gym, but never got around to it.

It has been more than a year since then, so I thought I might as well just publish what I have in case anyone else has the urge to throw their computer at the wall - uh, I mean, train an AI to do some kind of unipedal locomotion and have some premade training environment.

So here we are...

One day, I might still come back and clean it up, but don't bet on it.

