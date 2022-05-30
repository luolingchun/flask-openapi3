# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/4/16 14:21
import json

from flask import current_app
from flask.cli import click
from flask.cli import with_appcontext

from .markdown import openapi_to_markdown


@click.command(name='openapi')
@click.option('--output', '-o', type=click.Path(), help='The output file path.')
@click.option('--format', '-f', type=click.Choice(['json', 'yaml', 'markdown']), help='The output file format.')
@click.option('--indent', '-i', type=int, help='The indentation for JSON dumps.')
@click.option('--ensure_ascii', '-a', is_flag=True, help='Ensure ASCII characters or not. Defaults to False.')
@with_appcontext
def openapi_command(output, format, indent, ensure_ascii):
    """Export the OpenAPI Specification to console or a file"""
    if hasattr(current_app, 'api_doc'):
        obj = current_app.api_doc
        if format == 'yaml':
            import yaml
            openapi = yaml.safe_dump(obj, allow_unicode=True)
        elif format == 'markdown':
            openapi = openapi_to_markdown(obj)
        else:
            openapi = json.dumps(obj, indent=indent, ensure_ascii=ensure_ascii)
        if output:
            with open(output, 'w', encoding='utf8') as f:
                f.write(openapi)
            click.echo(f"Saved to {output}.")
        else:
            click.echo(openapi)
