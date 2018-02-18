# Comments Parser

Python module that lets you find comments in source code.

## Compatibility Information
Should work with both Python 2.x and 3.x.

## Usage
This is a completely independent module to extract comments from source code.

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

```
Example:

    >>> from extract_comments import check_file
    >>> for comm in check_file(src_file_path):
    >>>     print(comm[0])  # the comment
    >>>     print(comm[1])  # line number of the comment
    >>>     print(comm[2])  # starting index of the comment within the line

    Same example is applicable to other functions in the module.
```
## API Documentation
```
SPACES_FOR_TAB = 4

   int: Number of spaces represented by a TAB character

c_style(src_file)

   Find C style comments in source file.

   Args:
      src_file (string):  Path to the source file.

   Yields:
      tuple: A tuple containing (comment, line number of comment,
      index of comment within the line).

check_file(src_file)

   Calls appropriate method based on file extension for extracting
   comments.

   Args:
      src_file (string):  Path to the source file.

   Yields:
      tuple: A tuple containing (comment, line number of comment,
      index of comment within the line). Returns *None* if file
      extension does not match any of known types.

py_style(src_file)

   Find Python style comments in source file.

   Args:
      src_file (string):  Path to the source file.

   Yields:
      tuple: A tuple containing (comment, line number of comment,
      index of comment within the line).

xml_style(src_file)

   Find XML/HTML style comments in source file.

   Args:
      src_file (string):  Path to the source file.

   Yields:
      tuple: A tuple containing (comment, line number of comment,
      index of comment within the line).
```