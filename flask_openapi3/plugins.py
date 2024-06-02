# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2024/4/23 14:31


class BasePlugin:
    name = None
    display_name = None

    @classmethod
    def register(cls, doc_url: str) -> None:
        """
        Register the plugin.

        Args:
            doc_url (str): The API doc url.
        """
