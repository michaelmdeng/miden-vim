import neovim

def _strip_suffix(path, suffix):
    """ strip suffix from string """
    return path[0:len(path) - (path.endswith(suffix) and len(suffix))]

@neovim.plugin
class Miden:
    def __init__(self, vim):
        self.vim = vim

    @neovim.command('ScAddPackage', nargs='*')
    def sc_add_package(self, args):
        curr_file = self.vim.eval('expand("%:t")')
        curr_path = self.vim.eval('@%')
        curr_folder = _strip_suffix(curr_path, curr_file)

        nodes = curr_folder.split('/')
        rev_idx = nodes[::-1].index('src') if 'src' in nodes else -1
        src_idx = len(nodes) - rev_idx - 1

        if src_idx < 0 or src_idx > (len(nodes) - 3):
            self.vim.command(
                'echo "Error: Could not parse current file into a valid Scala namespace."')
            return

        (orig_cursor_row, orig_cursor_col) = self.vim.current.window.cursor
        curr_line = self.vim.current.buffer[0]
        curr_next_line = self.vim.current.buffer[1]

        post_src_nodes = [node for node in nodes[src_idx + 1::]
                          if node]
        relevant_nodes = [node for node in post_src_nodes[2::]
                          if not node.endswith('.scala')]
        package_str = 'package ' + '.'.join(relevant_nodes)

        cmds = []
        lines_deleted = 0
        if curr_line.startswith('package') and (not curr_next_line or curr_next_line.isspace()):
            cmds.append('1d _')
            cmds.append('1d _')
            lines_deleted = 2
        elif curr_line.startswith('package') and not curr_next_line.isspace():
            cmds.append('1d _')
            lines_deleted = 1

        cmds.append('call append(0, ["{}", ""])'.format(package_str))
        cmds.append(
            'call cursor({}, {})'.format(orig_cursor_row + 2 - lines_deleted,
                                         orig_cursor_col))

        self.vim.command(' | '.join(cmds))

    def _sc_add_entity(self, entity):
        curr_file = self.vim.eval('expand("%:t")')
        if not curr_file or not '.scala' in curr_file:
            self.vim.command(
                'echo "Error: Could not parse current file into a valid Scala entity."')
            return

        curr_entity = _strip_suffix(curr_file, '.scala')

        last_line_idx = len(self.vim.current.buffer) - 1
        last_line = self.vim.current.buffer[last_line_idx]
        entity_str = '{} {} {{'.format(entity, curr_entity)
        last_col_idx = len(entity_str) - 1

        if not last_line or last_line.isspace():
            self.vim.command(
                ('call append({}, ["{}", "}}"]) | '
                 'call cursor({}, {})').format(last_line_idx + 1,
                                               entity_str,
                                               last_line_idx + 3,
                                               last_col_idx + 1))
        else:
            self.vim.command(
                ('call append({}, ["", "{}", "}}"]) | '
                 'call cursor({}, {})').format(last_line_idx + 1,
                                              entity_str,
                                              last_line_idx + 3,
                                              last_col_idx + 1))

    @neovim.command('ScAddTrait', nargs='*')
    def sc_add_trait(self, args):
        self._sc_add_entity('trait')

    @neovim.command('ScAddClass', nargs='*')
    def sc_add_class(self, args):
        self._sc_add_entity('class')

    @neovim.command('ScAddObject', nargs='*')
    def sc_add_object(self, args):
        self._sc_add_entity('object')
