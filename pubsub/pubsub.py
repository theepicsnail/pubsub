from collections import defaultdict
__subscriptions = defaultdict(list) # map of channel to callback function

def pub(channel, *args, **kwargs):
    for callback in __subscriptions[channel]:
        callback(*args, **kwargs)

def sub(channel, function):
    __subscriptions[channel].append(function)

def unsub(channel, function):
    __subscriptions[channel] = filter(lambda func: func is not function,
        __subscriptions[channel])

