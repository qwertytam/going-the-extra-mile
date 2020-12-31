import inspect
from .utility import _INDENT

class _Writer(object):
    '''Writer used to create source files with consistent formatting'''

    def __init__(self, path):
        '''
        Args:
            path (handle): File name and path to write to
        '''
        self._path = path
        self._indent_level = 0
        self._start_of_line = True

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        '''
        Args:
            exception_type: Type of exception that triggered the exit
            exception_value: Value of exception that triggered the exit
            traceback: Traceback when exit was triggered
        '''
        # Clear the path if an uncaught exception occured while writing:
        if exception_type:
            self._path.truncate(0)

    def indent(self):
        '''Indent the writer by one level

        To be used in a similiar fashion to the write() function in this class.
        See documentation on the write() function for further explanation.
        '''
        self._indent_level += 1
        return self

    def dedent(self):
        '''Dedent the writer by one level
        
        To be used in a similiar fashion to the write() function in this class.
        See documentation on the write() function for further explanation.
        '''
        if self._indent_level > 0:
            self._indent_level -= 1

        return self

    def write(self, content='', end_in_newline=True):
        '''
        Write content to the file

        open(path, 'w') needs to be called prior to calling this function,
        typically by
            ````with open(file, 'w') as f:
                    self.write_fn(f)````
            where `self` is a higher level object and `write_fn(self, file)`
            would look something like
            ````def _write_html(self, file):
                    with _Writer(file) as w:
                        w.write('string to write')
                        w.write(self.string_to_write)````

        Args:
            content (str): Content to write, as a string
                Content is cleaned using Python's `inspect.cleandoc()`
            end_in_newline (bool): Whether or not to write a newline at the end.
                Default is True.
        '''
        lines = inspect.cleandoc(content).splitlines()
        for index, line in enumerate(lines):
            # Indent if the start of a line
            if self._start_of_line:
                self._path.write(_INDENT * self._indent_level)

            # Write the line
            self._path.write(line)

            # Write a new line if there's still more content
            if index < len(lines) - 1:
                self._path.write('\n')
                self._start_of_line = True

        # If the content should end in a newline, write it
        if end_in_newline:
            self._path.write('\n')
            self._start_of_line = True
        else:
            self._start_of_line = False

        return self
