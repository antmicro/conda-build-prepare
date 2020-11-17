#!/usr/bin/env python
import argparse
import os
import sys

from .conda_cmds import prepare_environment, prepare_recipe, restore_config_files
from .prepare import prepare_directory

def existingDir(dir_name):
    if dir_name == 'restore':
        restore_config_files()
        sys.exit(0)

    dir_name = os.path.join(os.path.abspath(os.path.curdir), dir_name)
    if(not os.path.isdir(dir_name)):
        raise argparse.ArgumentTypeError(f"{dir_name} is not a valid directory")
    return dir_name

def newDir(dir_name):
    dir_name = os.path.join(os.path.abspath(os.path.curdir), dir_name)
    if(os.path.exists(dir_name)):
        raise argparse.ArgumentTypeError(f"{dir_name} already exists")
    return dir_name

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="conda-build-prepare", description="Conda helper tool for repository preparation")
    parser.add_argument("package", action="store", type=existingDir, help="Target package directory; use 'restore' to restore commented out conda configuration files")
    parser.add_argument("-v", "--verbose", action="store_true", help="Add more verbosity to output")
    parser.add_argument("--dir", action="store", required=True, type=newDir, dest="directory", help="Use DIRECTORY to store generated files and cloned repository")
    parser.add_argument("--channels", action="store", required=False, metavar="CHANNEL", nargs="+", help="Each CHANNEL will be added to the environment's '.condarc' (with the last one on top)")
    parser.add_argument("--packages", action="store", required=False, metavar="PACKAGE", nargs="+", help="Each PACKAGE will be installed in the output environment alongside 'conda-build'")
    args = parser.parse_args()

    os.mkdir(args.directory)
    recipe_dir = os.path.join(args.directory, 'recipe')
    env_dir = os.path.join(args.directory, 'conda-env')
    git_dir = os.path.join(args.directory, 'git-repos')

    prepare_directory(args.package, recipe_dir)

    # Those will be applied in the prepared environment
    env_settings = {
            'set': {
                'safety_checks': 'disabled',
                'channel_priority': 'strict',
                'always_yes': 'yes',
                },
            }
    if args.channels is not None:
        env_settings['prepend'] = { 'channels': args.channels }

    prepare_environment(recipe_dir, env_dir, args.packages or [], env_settings)
    prepare_recipe(recipe_dir, git_dir, env_dir)

    # Print information about building
    recipe_relpath = os.path.relpath(recipe_dir)
    variants_path = os.path.join(recipe_relpath, 'rendering_variants.yaml')
    build_args = f"-m {variants_path} {recipe_relpath}" if os.path.exists(variants_path) \
            else recipe_relpath

    print()
    print("To build the package in the prepared environment, run:")
    print(f"  conda activate {os.path.relpath(env_dir)}")
    print(f"  conda build {build_args}")
    print("or:")
    print(f"  conda run -p {os.path.relpath(env_dir)} conda build {build_args}")
    print()

