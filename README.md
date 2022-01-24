# Watchdog

A little utility for handling softlocks. It's nothing special, and you can probably make better yourself.

## Usage

```
from watchdog import DogHouse

dog_house = DogHouse([reset_function])

spot = dog_house.adopt('Spot', timeout_s=30)
tops = dog_house.adopt('Tops', max_events=5)

spot.feed() # call this whenever you do the thing spot is watching for
tops.starve() # call this whenever you start the thing tops is watching for
tops.feed() # call this whenever the thing tops is watching completes successfully

# later, after activity

dog_house.check() # will run reset function if all the dogs haven't been fed.