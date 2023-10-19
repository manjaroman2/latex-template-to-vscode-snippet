## LaTeX template to VsCode snippet converter 



### Get the program  

#### Method 1: Download the executable from releases tab


#### Method 2: Clone the repository

`git clone git@github.com:manjaroman2/latex-template-to-vscode-snippet.git &&`
`cd latex-template-to-vscode-snippet &&`
`python src/latex_template_to_vscode_snippet.py` 

### Usage

`tex2snip <template.tex> <prefix>`

1. If template.tex references a .cls file it needs to be in the same directory 
2. If template.tex references .bib, they will be displayed and required for the template to work