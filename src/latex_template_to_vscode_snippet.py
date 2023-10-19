from pathlib import Path 
from argparse import ArgumentParser
from json import loads, dumps
import subprocess
import sys
import os 
import shutil
import importlib.util

has_color = importlib.util.find_spec("colorama") is not None

match sys.platform: 
    case "win32":
        latex_snippet_path = Path(os.getenv('APPDATA')) / "Code" / "User" / "snippets" / "latex.json"
    case "linux":    
        latex_snippet_path = Path.home() / ".config" / "Code" / "User" / "snippets" / "latex.json"
    case "darwin":
        latex_snippet_path = Path.home() / "Library" / "Application Support" / "Code" / "User" / "snippets" / "latex.json"
    case _:
        raise NotImplementedError(f"Platform {sys.platform} not supported")

if shutil.which("kpsewhich") is None:
    raise FileNotFoundError("kpsewhich not found, please install texlive")

parser = ArgumentParser()
parser.add_argument("template", type=str, help="Path to template file")
parser.add_argument("prefix", type=str, help="Snippet prefix")
parser.add_argument("--name", nargs='?', default=None, type=str, help="Name of the template, if not provided, the name of the template file will be used")
# parser.add_argument("--ask", action="store_true", help="Ask before overwriting existing snippet")
parser.add_argument("bib_resource_dir", nargs='?', default=None, type=str, help="Path to the directory containing the bib resources, if not in the same directory as the template file")
parser.add_argument("cls_resource_dir", nargs='?', default=None, type=str, help="Path to the directory containing the cls resources, if not in the same directory as the template file")

args = parser.parse_args()

print(f"Using snippet file {latex_snippet_path}")
if not latex_snippet_path.exists():
    latex_snippet_path.write_text("{}")
    print(f"    Created {latex_snippet_path}")

texmfhome = Path(subprocess.check_output("kpsewhich -var-value=TEXMFHOME", shell=True).decode().strip())
if not texmfhome.exists():
    texmfhome.mkdir(parents=True)
    print(f"Created {texmfhome}")
tex_common = texmfhome / "tex" / "latex" 
print("Class resources directory: ", tex_common)
if not tex_common.exists():
    tex_common.mkdir(parents=True)
    print(f"    Created {tex_common}")

template_path = Path(args.template)
if not args.cls_resource_dir:
    cls_resource_directory = template_path.parent
else:
    cls_resource_directory = Path(args.cls_resource_dir)
# if not args.bib_resource_directory:
    # bib_resource_directory = template_path.parent 
snippet_name = args.name if args.name else template_path.stem
prefix = args.prefix

print()
print(f"**** Parsing '{template_path}' ****")
_print = print
print = lambda *args, **kwargs: _print('    ', *args, **kwargs)
lines = []
bibs = []
cls_file = None
find_cls_file = False
for line in template_path.read_text().splitlines(): 
    line = line.strip()
    if line.startswith("%"): continue
    # print(line.split("%"))
    if (line := line.split("%")[0]): 
        if not cls_file:
            if "\\documentclass" in line:
                find_cls_file = True
            if find_cls_file:
                if (i := line.find("{")) != -1:
                    find_cls_file = False
                    cls_file = line[i+1:].split("}")[0]
                    print(f"document class: {cls_file}")
        
        # indentify bib resources
        i = 0
        while (i := line.find("addbibresource{", i)) != -1: 
            # print(f"found 'addbibresource{{' at {i}")
            if (j := line.find("}", i)) != -1:
                bibs.append(line[i+15:j])
                i = j
            else:
                raise ValueError("No closing bracket found!")
        lines.append(line.replace("\\\\", "\\\\\\")) # bro why
if bibs:
    print("requires bib resources:")
    for bib in bibs:
        print(f"   {bib}")
if cls_file:
    cls_file = cls_resource_directory / (cls_file + ".cls")
    if not cls_file.exists():
        raise FileNotFoundError(f"Could not find {cls_file}")
    tex_common_cls = tex_common / cls_file.stem / cls_file.name
    if tex_common_cls.exists():
        print(f"{cls_file.name} already exists, skipping")
    else:
        print(f"Copying {cls_file} to {tex_common}")
        if not tex_common_cls.parent.exists():
            tex_common_cls.parent.mkdir(parents=True)
        tex_common_cls.write_text(cls_file.read_text())
# for bib in bibs:
#     bib_path = bib_resource_directory / Path(bib)


latex_snippets = loads(latex_snippet_path.read_text())

new_snippet = {
    "prefix": prefix,
    "body": lines,
}

while snippet_name in latex_snippets:
    print(f"Snippet '{snippet_name}' already exists.")
    if dumps(latex_snippets[snippet_name]) == dumps(new_snippet):
        print(f"Snippet '{snippet_name}' is identical to new snippet, skipping")
        exit() 
    if snippet_name[-1].isdigit():
        snippet_name = snippet_name[:-1] + str(int(snippet_name[-1]) + 1) 
    else:
        snippet_name = snippet_name + "1"
        break
if has_color:
    import colorama
    colorama.init()
    _print(f"+ snippet with name '{colorama.Fore.GREEN}{snippet_name}{colorama.Style.RESET_ALL}' and prefix {colorama.Fore.GREEN}{prefix}{colorama.Style.RESET_ALL}")
else:
    _print(f"+ snippet with name '{snippet_name}' and prefix {prefix}")

latex_snippets[snippet_name] = new_snippet
# if args.ask:
#     input("Press enter to overwrite existing snippet, or Ctrl+C to cancel")
latex_snippet_path.write_text(dumps(latex_snippets, indent=4))

