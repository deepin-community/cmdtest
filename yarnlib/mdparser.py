# Copyright 2013  Lars Wirzenius
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# =*= License: GPL-3+ =*=


import logging
import html.parser
import markdown
import io
from markdown.treeprocessors import Treeprocessor


#
# Classes for Markdown parsing. See python-markdown documentation
# for details. We want to find all top level code blocks (indented
# four spaces in the Markdown), which we'll parse for scenario test
# stuff later on. We create a Python markdown extension and use
# "tree processor" to analyse the parsed ElementTree at the right
# moment for top level <pre> blocks.
#

# This is a Treeprocessor that iterates over the parsed Markdown,
# as an ElementTree, and finds all top level code blocks.

class GatherCodeBlocks(Treeprocessor):

    def __init__(self, blocks):
        self.blocks = blocks

    def run(self, root):
        h = html.parser.HTMLParser()
        for child in root.getchildren():
            if child.tag == 'pre':
                code = child.find('code')
                text = h.unescape(code.text)
                self.blocks.append(text)
        return root

# This is the Python Markdown extension to call the code block
# gatherer at the right time. It stores the list of top level
# code blocks as the blocks attribute.

class ParseScenarioTestBlocks(markdown.extensions.Extension):

    def extendMarkdown(self, md, md_globals):
        self.blocks = []
        self.gatherer = GatherCodeBlocks(self.blocks)
        md.treeprocessors.add('gathercode', self.gatherer, '_end')


class MarkdownParser(object):

    def __init__(self):
        self.blocks = []

    def parse_string(self, text):
        ext = ParseScenarioTestBlocks()
        f = io.StringIO()
        markdown.markdown(text, output=f, extensions=[ext])
        self.blocks.extend(ext.blocks)
        return ext.blocks

    def parse_file(self, filename): # pragma: no cover
        with open(filename) as f:
            text = f.read()
            return self.parse_string(text)
