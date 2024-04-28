# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2024/4/23 14:31

from typing import Dict, Any, Optional


class BasePlugin:
    name = None
    display_name = None

    @classmethod
    def register(
            cls,
            doc_url: str,
            config: Optional[Dict[str, Any]] = None,
            oauth_config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register the plugin with the provided config and oauth_config.

        Args:
            doc_url (str): The API doc url.
            config (Dict[str, Any]): Configuration options for the plugin.
            oauth_config (Dict[str, Any]): OAuth configuration options for the plugin.
        """
