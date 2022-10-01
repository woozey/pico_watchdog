# MIT License

# Copyright (c) 2022 Pico Watchdog developers

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Parts adopted with modifications from:
# https://auth0.com/blog/state-pattern-in-python/


class Context:

    _state = None

    def __init__(self, state) -> None:
        self.set_state(state)

    def set_state(self, state):
        self._state = state
        self._state.context = self

    def run(self):
        self._state.run()


# class DogCtx(Context):

#     def __init__(self, state):
#         self.set_state(state)

    # def set_state(self, state):
    #     super().set_state(state)
    #     # self._state.blinker.setup()
    
    # def run(self):
    #     super().run()
    #     self._state.blinker.run()

class State:
    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    def run(self) -> None:
        pass


class DogState(State):
    blinker = None
    b_period = None
    b_number = None
    b_duration = None
    b_pin = None
    
    def __init__(self) -> None:
        super().__init__()
        self.blinker = self.blinker(self.b_period,
                                    self.b_number,
                                    self.b_duration,
                                    self.b_pin)
        self.blinker.setup()

    def run(self):
        super().run()
        self.blinker.run()