
'''This is a completely independent module to extract comments from source code.

You can either directly call the relevant function for the source file or you can
call 'check_file' that would eventually call the required function based on source
file extension.

Each function yields tuple having (comment, line number of the comment, starting index
of the comment within the line) reading source file line by line, so you must call
function multiple times treating it like an iterator.

When reading source file, Python counts TAB as a single character so TAB has to be
resolved into corresponding number of space characters to calculate accurate start index of
comment. User can set module variable to control number of space characters a TAB should be
translated to.

Example:

    >>> from extract_comments import check_file
    >>> for comm in check_file(src_file_path):
    >>>     print(comm[0])  # the comment
    >>>     print(comm[1])  # line number of the comment
    >>>     print(comm[2])  # starting index of the comment within the line

    Same example is applicable to other functions in the module.

MIT License

Copyright (c) 2017 Muhammad Mohsin Khan muhammadmohsenkhan@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


# number of spaces for a tab character
SPACES_FOR_TAB = 4
'''int: Number of spaces represented by a TAB character'''


def check_file(src_file):
    '''Calls appropriate method based on file extension for extracting comments.

    Args:
        src_file (string):  Path to the source file.

    Yields:
        tuple: A tuple containing (comment, line number of comment, index of
        comment within the line). Returns *None* if file extension does not
        match any of known types.
 '''

    if src_file.lower().endswith('.py'):
        return py_style(src_file)
    elif src_file.lower().endswith(('.cpp', '.c', '.h')):
        return c_style(src_file)
    elif src_file.lower().endswith(('.xml', '.html', '.htm')):
        return xml_style(src_file)
    else:
        return None


def c_style(src_file):
    '''Find C style comments in source file.

    Args:
        src_file (string):  Path to the source file.

    Yields:
        tuple: A tuple containing (comment, line number of comment, index of
        comment within the line).
    '''

    with open(src_file) as src_file:

        # variable to hold line number
        line_num = 1
        # state of the state machine
        state = 0

        # loop through all the lines in source file
        for line in src_file:

            # if we are not processing multi line comment block,
            # ignore the line not having //, /* or */.
            if all(x not in line for x in ['//', '/*', '*/']) and state != 2:
                line_num += 1
                continue

            # index at which string (line) is being read
            index = 0

            # loop over the string (line)
            while index < (len(line) - 1):

                # state 0:
                # start looking for //, /*, " or ' character
                if state == 0:
                    # check if current and next character makes //
                    if line[index:index+2] == '//':
                        # return everything after // as it would be a comment
                        yield line[index+2:], line_num, index + 2 + \
                            (line.count('\t', 0, index+2))*(SPACES_FOR_TAB-1)
                        # nothing more needs to be done for this line so break
                        break
                    # # check if current and next character makes /*
                    elif line[index:index+2] == '/*':
                        # check if we have */ within the same line,
                        # by trying to find index of */ within the string
                        pos = line.find("*/", index+2)
                        if pos == -1:
                            # if no, return everything after /* as it would be a comment
                            yield line[index+2:], line_num, index + 2 + \
                                (line.count('\t', 0, index+2))*(SPACES_FOR_TAB-1)
                            # move to state 2 and process multi-line comment
                            state = 2
                            # nothing more needs to be done for this line so break
                            break
                        else:
                            # if yes, return everything between /* and */
                            yield line[index+2:pos], line_num, index + 2 + \
                                (line.count('\t', 0, index+2))*(SPACES_FOR_TAB-1)
                            # set index to point to the character after */
                            index = pos + 1
                            state = 0
                    # two checks below are to avoid // and /* within quotes
                    # that could be printf statements, string declarations etc

                    # check if we have read "
                    elif  line[index] == '\"':
                        # save the character ' is a variable
                        string_start = '\"'
                        state = 1
                    # check if we have read '
                    elif line[index] == '\'':
                        # save the character " is a variable
                        string_start = '\''
                        state = 1
                # state 1:
                # find end of the quote
                elif  state == 1:
                    # keep reading till we find end of the quote
                    if (line[index] == string_start) and (line[index-1] != '\\'):
                        state = 0
                # state 2:
                # handle multi-line comment block
                elif state == 2:
                    # check if */ is there in current line
                    pos = line.find("*/", index)
                    if pos == -1:
                        # if no, return whole line as this is a comment
                        yield line[index:], line_num, index
                        # move to next line
                        break
                    else:
                        # if yes, return everything before */
                        yield line[index:pos], line_num, index
                        # set index to point to the character after */
                        index = pos + 1
                        state = 0

                index += 1

            line_num += 1


def py_style(src_file):
    '''Find Python style comments in source file.

    Args:
        src_file (string):  Path to the source file.

    Yields:
        tuple: A tuple containing (comment, line number of comment, index of
        comment within the line).
    '''

    with open(src_file) as src_file:

        line_num = 1
        state = 0
        for line in src_file:

            if all(x not in line for x in ['#', "\'''", '\"""']) and state != 1:
                line_num += 1
                continue

            index = 0
            while index < (len(line) - 1):

                if state == 0:
                    if line[index] == '#':
                        yield line[index+1:], line_num, index + 1 + \
                            (line.count('\t', 0, index+2))*(SPACES_FOR_TAB-1)
                        state = 0
                    elif line[index:index+3] == "\'''":
                        block_start = "\'''"
                        comment_block = True
                    elif line[index:index+3] == '\"""':
                        block_start = '\"""'
                        comment_block = True

                    if comment_block:
                        comment_block = False
                        pos = line.find(block_start, index+3)
                        if pos == -1:
                            yield line[index+3:], line_num, index + 3 + \
                                (line.count('\t', 0, index+2))*(SPACES_FOR_TAB-1)
                            state = 1
                            break
                        else:
                            yield line[index+3:pos], line_num, index + 3 + \
                                (line.count('\t', 0, index+2))*(SPACES_FOR_TAB-1)
                            index = pos + 2
                            state = 0

                elif state == 1:
                    pos = line.find(block_start, index)
                    if pos == -1:
                        yield line[index:], line_num, index
                        break
                    else:
                        yield line[index:pos], line_num, index
                        index = pos + 2
                        state = 0

                index += 1

            line_num += 1


def xml_style(src_file):
    '''Find XML/HTML style comments in source file.

    Args:
        src_file (string):  Path to the source file.

    Yields:
        tuple: A tuple containing (comment, line number of comment, index of
        comment within the line).
    '''

    with open(src_file) as src_file:

        line_num = 1
        state = 0
        for line in src_file:

            if all(x not in line for x in ['<!--', '-->']) and state != 1:
                line_num += 1
                continue

            index = 0
            while index < (len(line) - 1):

                if state == 0:
                    if line[index:index+4] == '<!--':
                        pos = line.find('-->', index+3)
                        if pos == -1:
                            yield line[index+4:], line_num, index + 4 + \
                                (line.count('\t', 0, index+2))*(SPACES_FOR_TAB-1)
                            state = 1
                            break
                        else:
                            yield line[index+4:], line_num, index + 4
                            index = pos + 2
                            state = 0
                elif state == 1:
                    pos = line.find('-->', index)
                    if pos == -1:
                        yield line[index:], line_num, index
                        break
                    else:
                        yield line[index:pos], line_num, index
                        index = pos + 2
                        state = 0

                index += 1

            line_num += 1
