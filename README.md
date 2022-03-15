# MHDBDB XML RDF Converter

This python tool allows the conversion from xml-files into rdf files, based on mhdbdb xml ontology. The tool can be used as a command line application or embedded as a module into python applications.

## Implementation road map

* xml to rdf: complete
* rdf to xml: not implemented yet

## Setup

Recommended usage as a commandline tool. Setup python virtuel enviroment and install requirements.

## Parameters of converter.py

### --xml2rdf [boolean] 

If _true_ convert xml to rdf. If _false_ convert rdf to xml [currently not implemented!].

### --xml2rdfOptions 

Options for xml to rdf conversion. Default:

```json        
{
    "instanceNamespace":"https://dh.plus.ac.at/mhdbdb/text/",
    "instanceNamespacePrefix":"mhdbdb",
    "useDocNameAsXmlIdPrefix":true, 
    "ignoreWhitespace":true, 
    "xPathRoot":".//tei:text",
    "generateSubClasses":true
}
```

* instanceNamespace: Namespace for the creation of new rdf instances
* instanceNamespacePrefix: Prefix for that namespace
* useDocNameAsXmlIdPrefix: If true, adds 'document_name#' as prefix to * xml:id from tree
* ignoreWhitespace: If true, ignores all whitespace text nodes
* xPathRoot: xPath to element, which should be used as root in conversion
* generateSubClasses: If true, generates rdfs subclasses for mhdbdbxml:Element for each parsed class of the xml document

### --inDir

Path to input directory

### --outDir

Path to output directory

### --startFile

If set, conversion starts with Filename (in ascending order)
