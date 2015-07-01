# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Registration of sub-tabs for under Dashboard > Analytics."""

__author__ = 'Mike Gainer (mgainer@google.com)'

import bisect
import collections
import re

class BaseTab(object):
    def __cmp__(self, obj):
        assert isinstance(obj, BaseTab)
        return cmp(self.placement, obj.placement)

    @property
    def name(self):
        return self._name

    @property
    def title(self):
        return self._title

    @property
    def placement(self):
        return self._placement


class NavTab(BaseTab):
    def __init__(self, name, title, placement=None):
        self._name = name
        self._title = title
        self._placement = placement or float('inf')


class Registry(object):

    class _Tab(BaseTab):

        def __init__(
                self, group, name, title, contents, href=None, placement=None,
                target=None):
            if not re.match('^[a-z0-9_]+$', name):
                raise ValueError('Sub-tabs under Dashboard must '
                                 'have names consisting only of lowercase '
                                 'letters, numbers, and underscore.')
            self._group = group
            self._name = name
            self._title = title
            self._contents = contents
            self._href = href
            self._target = target

            if placement is None:
                placement = 1000000
            self._placement = placement

        @property
        def group(self):
            return self._group

        @property
        def contents(self):
            return self._contents

        @contents.setter
        def contents(self, contents):
            self._contents = contents

        @property
        def href(self):
            return self._href

        def computed_href(self, destination='/dashboard'):
            if self.href:
                return '/{}'.format(self._href)
            else:
                return "{destination}?action={action}&tab={tab}".format(
                    action=self.group, destination=destination, tab=self.name)

        @property
        def target(self):
            return self._target

    _tabs_by_group = collections.defaultdict(list)

    @classmethod
    def register(
            cls, group_name, tab_name, tab_title, contents=None, href=None,
            target=None, placement=None):
        if cls.get_tab(group_name, tab_name):
            raise ValueError(
                'There is already a sub-tab named "%s" ' % tab_name +
                'registered in group %s.' % group_name)

        tab = Registry._Tab(
            group_name, tab_name, tab_title, contents=contents, href=href,
            placement=placement, target=target)
        bisect.insort(cls._tabs_by_group[group_name], tab)

    @classmethod
    def unregister_group(cls, group_name):
        # This method is deprecated.
        if group_name in cls._tabs_by_group:
            del cls._tabs_by_group[group_name]

    @classmethod
    def get_tab(cls, group_name, tab_name):
        matches = [tab for tab in cls._tabs_by_group.get(group_name, [])
                   if tab.name == tab_name]
        return matches[0] if matches else None

    @classmethod
    def get_tab_group(cls, group_name):
        return cls._tabs_by_group.get(group_name, None)

    @classmethod
    def get_group_name_for_tab(cls, tab_name):
        for group_name, group in cls._tabs_by_group.iteritems():
            for tab in group:
                if tab.name == tab_name:
                    return group_name
