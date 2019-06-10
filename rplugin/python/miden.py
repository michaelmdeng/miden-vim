import neovim

def _strip_suffix(string, suffix):
    if string.endswith(suffix):
        return string[::len(string) - len(suffix)]

    return string

@neovim.plugin
class Miden:
    def __init__(self, vim):
        self.vim = vim

    @neovim.command('ScAddPackage', nargs='*')
    def sc_add_package(self, args):
        curr_file = self.vim.eval('expand("%:t")')
        curr_path = _strip_suffix(self.vim.eval('@%'), curr_file)

        nodes = curr_path.split('/')
        rev_idx = nodes[::-1].index('src') if 'src' in nodes else -1
        src_idx = len(nodes) - rev_idx - 1

        if src_idx < 0 or src_idx > (len(nodes) - 3):
            self.vim.async_call(
                self.vim.command,
                'echo "Error: Could not parse current file into a valid Scala namespace."'
            )
            return

        (orig_cursor_row, orig_cursor_col) = self.vim.current.window.cursor

        post_src_nodes = [node for node in nodes[src_idx + 1::]
                          if node]
        relevant_nodes = [node for node in post_src_nodes[2::]
                          if not node.endswith('.scala')]

        package_str = 'package ' + '.'.join(relevant_nodes)

        self.vim.command(
            'call append(0, ["{}", ""])'.format(package_str))
        self.vim.command(
            'call cursor({}, {})'.format(orig_cursor_row + 2, orig_cursor_col))

