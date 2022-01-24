import time
import logging
from collections import abc
from typing import *

class Watchdog:
    """ A watchdog to recover from problems that don't completely halt code. """

    def __init__(self, name: str):
        self.name = name
        self.active = False

    def send_to_kennel(self) -> None:
        """Mark this watchdog as inactive (at the kennel; you don't need to feed it)"""
        self.active = False

    def send_to_home(self) -> None:
        """Mark this watchdog as active (at home; you do need to feed it)"""
        self.feed() # automatically feeds so it doesn't bark immediately
        self.active = True

    def feed(self) -> None:
        raise NotImplementedError()

    def starve(self) -> None:
        raise NotImplementedError()

    def should_bark(self, now: float) :
        raise NotImplementedError()

class TimeDog(Watchdog):
    """ A watch watchdog that operates off a timeout, as standard. """

    def __init__(self, name: str, timeout_s: int):
        super().__init__(name)
        self.timeout_s = timeout_s
        self.last_feed = time.time()

    def feed(self) -> None:
        self.last_feed = time.time()

    def starve(self) -> None:
        pass

    def should_bark(self, now) -> bool:
        if self.active:
            return now - self.last_feed > self.timeout_s


class EventDog(Watchdog):
    """ A watch watchdog that runs off a number of events, rather than off time. """

    def __init__(self, name, max_events):
        super().__init__(name)
        self.max_events = max_events
        self.current_events = 0

    def feed(self) -> None:
        self.current_events = 0

    def starve(self) -> None:
        self.current_events += 1

    def should_bark(self, _: float):
        if self.active:
            return self.current_events > self.max_events

class DogHouse(MutableMapping[str, Watchdog]):
    """ Watchdog manager """
    def __init__(self, reset_function: Callable[[Watchdog], Any], logger: logging.Logger=None, **kwargs):
        self.dogs = dict()
        self._reset_function = reset_function
        self.logger = (logger or logging.getLogger()).getChild('doghouse')
        if kwargs:
            self.update(kwargs)

    def __getitem__(self, key: str):
        return self.dogs[self._keytransform(key)]

    def __setitem__(self, key: str, value: Watchdog):
        self.logger.warning('We recommend adopting a dog instead!')
        self.dogs[self._keytransform(key)] = value

    def __delitem__(self, key: str):
        del self.dogs[self._keytransform(key)]

    def __iter__(self):
        return iter(self.dogs)
    
    def __len__(self):
        return len(self.dogs)

    def _keytransform(self, key: str):
        return key.lower()
        
    @classmethod
    def fromkeys(cls, iterable: Iterable[str], value: Watchdog) -> "DogHouse":
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def update(self, other: Any=(), **kwargs: Watchdog) -> None:
        """Updates the dictionary from an iterable or mapping object."""
        if isinstance(other, abc.Mapping):
            for key in other:
                self.dogs[key] = other[key]
        elif hasattr(other, "keys"):
            for key in other.keys():
                self.dogs[key] = other[key]
        else:
            for key, value in other:
                self.dogs[key] = value
        for key, value in kwargs.items():
            self.dogs[key] = value

    def adopt(self, name: str, timeout_s: int=None, max_events: int=None) -> Watchdog:
        """Register a new Watchdog"""
        if self._reset_function is None or not callable(self._reset_function):
            self.logger.warning('No reset function is set')
        if name in self.dogs:
            # If already adopted, it's a no-op, because that means we accidentally adopted it twice
            self.logger.debug(f'Attempted to adopt Watchdog {name} twice!')
            return self.dogs.get(name)
        if timeout_s is not None:
            self.logger.debug(f'Adopted Watchdog {name} (Timedog)')
            return self.dogs.setdefault(name, TimeDog(name, timeout_s))
        if max_events is not None:
            self.logger.debug(f'Adopted Watchdog {name} (Eventdog)')
            return self.dogs.setdefault(name, EventDog(name, max_events))
        raise ValueError('Must supply timeout_s or max_events!')

    def check(self) -> None:
        """Check all our Watchdogs are healthy"""
        now = time.time()
        for name, watchdog in self.dogs.items():
            if watchdog.should_bark(now):
                self.logger.error(f'Watchdog {name} has starved!!!')
                if self._reset_function and callable(self._reset_function):
                    self._reset_function(watchdog)
                break