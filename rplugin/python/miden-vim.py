import pynvim

@pynvim.plugin
class Miden:
    def __init__(self, vim):
        self.vim = vim

    @pynvim.function('scala_add_package')
    def function_handler(self, args):
        self.vim.raw_message("Hello World!")
