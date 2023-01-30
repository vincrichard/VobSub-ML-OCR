"""
This file is to help simplify types, however is has also morphed into the next step from the argument parser.
Essentially here we break up the arguments from the argument parser into separate classes for easier access.
"""
import yaml
import json
import inspect
from copy import deepcopy
from argparse import ArgumentParser, Action
from typing import List, Literal, Tuple, Dict, Optional
from dataclasses import dataclass
from pathlib import Path



@dataclass
class SettingsArgs:
    @dataclass
    class GeneralArgs:
        minimum_milliseconds_between_lines: int = 24
        subtitle_maximum_display_milliseconds: int = 8 * 1000

    general: GeneralArgs = GeneralArgs()


class Config:
    def __init__(
        self,
        settings: Dict = {},
    ) -> None:
        def get_config(local_argument):
            return {k: local_argument[k] for k in inspect.signature(Config.__init__).parameters.keys()}

        self.config = deepcopy(get_config(locals()))
        del self.config["self"]

        self.settings = SettingsArgs(**settings)



    @classmethod
    def from_json(cls, file_path: str):
        with open(file_path) as read_handle:
            return cls(**json.load(read_handle))

    @classmethod
    def from_yaml(cls, file_path: str):
        def load_from_other_config(file_path, path_to_load: List[str]):
            dir_path = Path(file_path).parent
            base_cfg = {}
            for path in path_to_load:
                path = dir_path.joinpath(path).resolve()
                tmp_cfg = get_dict_from_yaml(path)
                base_cfg = cls.update_recursive_dict(base_cfg, tmp_cfg)
            return base_cfg

        def get_dict_from_yaml(file_path):
            with open(file_path) as read_handle:
                cfg = yaml.load(read_handle, Loader=yaml.FullLoader)
            if '__load__' in cfg.keys():
                base_cfg = load_from_other_config(file_path, cfg['__load__'])
                cfg = cls.update_recursive_dict(base_cfg, cfg)
                del cfg['__load__']
            return cfg

        cfg = get_dict_from_yaml(file_path)
        return cls(**cfg)

    def cloned_update(self, **kwargs) -> "Config":
        options = self.update_recursive_dict(self.config, kwargs)
        cfg = Config(**options)
        if hasattr(self, 'job'):
            cfg.job = self.job
        return cfg

    @classmethod
    def update_recursive_dict(cls, current, update):
        output = deepcopy(current)
        for k, v in update.items():
            if type(v) == dict:
                assert type(current.get(k, None)) in [dict, type(None)], "Error setting a dict on to a non dict value"
                if type(current.get(k, None)) == dict:
                    output.update({
                        k: cls.update_recursive_dict(current.get(k, {}), v)
                    })
                else: # is None
                    output.update({k: v})
            else:
                output.update({k: v})

        return output


class store_dict(Action):
    """
    Class used for additional argument path in command line.
    Usage -Dname:subname:subsubname=value
    """
    def ensure_value(self, namespace, dest, default):
        stored = getattr(namespace, dest, None)
        if stored is None:
            return default
        return stored

    def recursive_association(self, name, value, vals):
        if ':' in name:
            parent, _,  child = name.partition(':')
            value = self.recursive_association(child, value, vals.get(parent, {}))
            vals[parent] = value
        else:
            vals[name] = value
        return vals

    def __call__(self, parser, namespace, values, option_string=None):
        vals = dict(self.ensure_value(namespace, self.dest, {}))
        k, _, v = values.partition('=')
        self.recursive_association(k, v, vals)

        setattr(namespace, self.dest, vals)

def retrieve_config(args=None):
    """
    Starting function to return the config from a simple argument parser
    """
    parser = ArgumentParser()
    parser.add_argument("job", default='train', choices=['train', 'eval'])
    parser.add_argument("config")
    parser.add_argument('-D', default={}, action=store_dict, help="Additional argument ex: -Dgeneral:gpu=0")

    args = parser.parse_args(args)

    cfg = Config.from_yaml(args.config)
    if len(args.D) > 0:
        cfg = cfg.cloned_update(**args.D)

    if args.job == 'eval':
        assert cfg.general.checkpoint_name is not None, "For evaluation need a checkpoint"
    cfg.job = args.job

    return cfg