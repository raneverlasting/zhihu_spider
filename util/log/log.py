class Counter:
    def __init__(self):
        self.index = 0

    def reset(self):
        self.index = 0

    def increase(self):
        self.index += 1

    def get(self):
        return self.index

    def __str__(self):
        return str(self.index)


class Mate:
    def __init__(self, ):
        pass

class Log:
    def __init__(self, counter, title, author, time, voteup, rate, isrecord):
        self.counter = counter
        self.title = title
        self.author = author
        self.time = time
        self.voteup = voteup
        self.rate = rate
        self.isrecord = isrecord

    def add_event(self, event):
        self.events.append(event)
