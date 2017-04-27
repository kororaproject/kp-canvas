from collections import deque
from datetime import datetime

# Python 2.7 fixes
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

class TextTable(object):
    def __init__(self, header=[], align='l', padding=4, header_padding=0):
        self.align = align
        self.padding = padding
        self.headline = header
        self.header_padding = header_padding

        self._rows = []
        self._data = None

    def __str__(self):
        if self._data is None:
            # use a deque to be able to prepend the table header easily
            data = deque(self._normalize(self._rows))

            # transpose data to get max column widths
            columns = list(zip_longest(*data, fillvalue=''))
            widths = self._get_widths(columns)

            if len(self.headline):
                if self.header_padding:
                    padding_str = ' ' * self.header_padding
                    self.headline = ['{0}{1}{0}'.format(padding_str, col) for col in self.headline]

                # prepend the header to the table and update columns
                header = self._get_header(self.headline, widths)

                # series of left appends results in reversing the order of elements in the iterable argument
                data.extendleft(reversed(header))

                columns = list(zip_longest(*data, fillvalue=''))
                widths = self._get_widths(columns)

            # align columns and then transpose it again to get the table back
            alignments = ['l' for x in range(len(columns))]
            if not isinstance(self.align, list):
                alignments = [self.align for x in range(len(columns))]

            elif len(self.align) == len(columns):
                alignments = self.align

            # unzip and cache
            self._data = list(zip(*self._align(columns, widths, alignments)))

        table = [''.join(line) for line in self._data]
        table = '\n'.join(table)

        return table

    @staticmethod
    def _get_widths(columns):
        """Gets the max width of each column."""
        # at first find the longest value in a column, then calculate its length
        return [len(max(column, key=len)) for column in columns]

    def _align(self, columns, widths, alignments):
        """Aligns the given columns columns depending on self.alignment"""
        aligned_columns = []

        for column, width, alignment in zip(columns, widths, alignments):
            aligned_column = []

            for item in column:
                # add padding to the actual column width
                total_width = width + self.padding

                # build formatstring depending on alignment
                if alignment == 'l':
                    format_str = '{{:<{}}}'.format(total_width)

                elif alignment == 'r':
                    format_str = '{{:>{}}}'.format(total_width)

                elif alignment == 'c':
                    format_str = '{{:^{}}}'.format(total_width)

                else:
                    raise RuntimeError('Wrong alignment string')

                aligned_item = format_str.format(item)
                aligned_column.append(aligned_item)

            aligned_columns.append(aligned_column)

        return aligned_columns

    def _get_header(self, headline, column_widths):
        """Creates the table header"""
        header = []
        header_underline = []
        header_widths = map(len, headline)

        for width, header_width in zip(column_widths, header_widths):
            width = max(header_width, width)

            item = '-' * width
            header_underline.append(item)

        header.append(headline)
        header.append(header_underline)

        return header

    def _normalize(self, data):
        """Converts the given data to strings for usage in a table"""
        norm_data = []

        for row in data:
            norm_row = []

            for column in row:
                # custom format strings for specific objects
                if isinstance(column, float):
                    format_str = '{{:.{}f}}'.format(2)
                    item = format_str.format(column)

                elif isinstance(column, datetime):
                    item = column.strftime('%Y-%m-%d %H:%M')

                else:
                    item = str(column)

                norm_row.append(item)

            norm_data.append(norm_row)

        return norm_data

    # PUBLIC PROPERTIES

    # PUBLIC METHODS
    def add_row(self, cells):
        self._data = None
        self._rows.append(cells)

    def reset(self):
        self._data = None
        self._rows = []

