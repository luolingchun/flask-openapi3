# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 14:25
import os

from flask import Flask, render_template, Blueprint, current_app

from flask_openapi3.models import APIDoc
from flask_openapi3.models.info import Info


class OpenAPI:
    def __init__(self, info: Info, app=None):
        self.openapi_version = "3.0.3"

        if not isinstance(info, Info):
            raise TypeError(f"Info is required (got type {type(info)})")
        self.info = info
        self.paths = None
        self.components = None
        self.tags = None
        self.name = 'openapi'
        self.api_doc_url = f"/{self.name}.json"
        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        _here = os.path.dirname(__file__)
        template_folder = os.path.join(_here, 'templates')
        static_folder = os.path.join(template_folder, 'static')

        blueprint = Blueprint(
            self.name,
            __name__,
            url_prefix=f'/{self.name}',
            template_folder=template_folder,
            static_folder=static_folder
        )
        blueprint.add_url_rule(rule=self.api_doc_url, endpoint=self.name, view_func=lambda: self.api_doc)
        blueprint.add_url_rule(rule='/redoc', endpoint='redoc',
                               view_func=lambda: render_template("redoc.html", api_doc_url=f'{self.name}.json'))
        blueprint.add_url_rule(rule='/swagger', endpoint='swagger',
                               view_func=lambda: render_template("swagger.html", api_doc_url=f'{self.name}.json'))
        blueprint.add_url_rule(rule='/', endpoint='index',
                               view_func=lambda: render_template("index.html", api_doc_url=f'{self.name}.json'))
        app.register_blueprint(blueprint)

    @property
    def api_doc(self):
        api_doc = APIDoc(openapi=self.openapi_version, info=self.info)
        print(self.get_routes())
        return api_doc.dict()

    def get_routes(self):
        for rule in current_app.url_map.iter_rules():
            if any(str(rule).startswith(path) for path in (f"/{self.name}", "/static")):
                continue
            print(rule)


if __name__ == '__main__':
    OpenAPI(info='sss')
