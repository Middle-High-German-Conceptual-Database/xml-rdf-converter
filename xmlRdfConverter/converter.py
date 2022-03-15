#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import glob
import json
from pathlib import Path

from xmlClasses import Document

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Converter xml2rdf or rdf2xml'
    )
    parser.add_argument(
        "--xml2rdf",
        type=bool,
        default=True,
        required=False,
        help="If true, convert xml to rdf. If false convert rdf to xml [currently not implemented!].")
    parser.add_argument(
        '--xml2rdfOptions',
        type=json.loads,
        default='''
            {
                "instanceNamespace":"https://dh.plus.ac.at/mhdbdb/text/",
                "instanceNamespacePrefix":"mhdbdb",
                "useDocNameAsXmlIdPrefix":true, 
                "ignoreWhitespace":true, 
                "xPathRoot":".//tei:text",
                "generateSubClasses":true
            }''',
        required=False,
        help="""
            Options for xml to rdf conversion. See default for example. Options:
            
            instanceNamespace: Namespace for the creation of new rdf instances
            instanceNamespacePrefix: Prefix for that namespace
            useDocNameAsXmlIdPrefix: If true, adds 'document_name#' as prefix to xml:id from tree
            ignoreWhitespace: If true, ignores all whitespace text nodes
            xPathRoot: xPath to element, which should be used as root in conversion
            generateSubClasses: If true, generates rdfs subclasses for mhdbdbxml:Element for each parsed class of the xml document
        """)
    parser.add_argument(
        "--inDir",
        type=str,
        default="./in",
        required=False,
        help="Path to input directory")
    parser.add_argument(
        "--outDir",
        type=str,
        default="./out",
        required=False,
        help="Path to output directory")
    parser.add_argument(
        "--startFile",
        type=str,
        default=None,
        required=False,
        help="If set, conversion starts with Filename (in ascending order)")

    args = parser.parse_args()

    if args.xml2rdf is True:
        print(args.xml2rdfOptions)
        pathList = list(glob.glob(f"{args.inDir}/*.xml"))
        pathList.sort()
        if args.startFile is not None:
            try:
                mPath = list(
                    filter(lambda x: args.startFile in x, pathList))[0]
                pathList = pathList[pathList.index(mPath):]
            except ValueError:
                print(f'{args.startFile} is not present in {args.inDir}')
        for path in pathList:
            path = Path(path)
            docId = path.name
            print(f"Converting {docId}")
            for suffix in path.suffixes:
                docId = docId.replace(suffix, '')

            # Xml2Rdf Options
            if "instanceNamespace" in args.xml2rdfOptions:
                instanceNamespace = args.xml2rdfOptions["instanceNamespace"]
            else:
                instanceNamespace = "http://example.org/"
            if "instanceNamespacePrefix" in args.xml2rdfOptions:
                instanceNamespacePrefix = args.xml2rdfOptions["instanceNamespacePrefix"]
            else:
                instanceNamespace = "example"
            if "useDocNameAsXmlIdPrefix" in args.xml2rdfOptions and args.xml2rdfOptions["useDocNameAsXmlIdPrefix"] is True:
                instancesXmlidPrefix = f"{docId}#"
            else:
                instancesXmlidPrefix = ''
            if "ignoreWhitespace" in args.xml2rdfOptions:
                ignoreWhitespace = args.xml2rdfOptions["ignoreWhitespace"]
            else:
                ignoreWhitespace = False
            if "xPathRoot" in args.xml2rdfOptions:
                xPathRoot = args.xml2rdfOptions["xPathRoot"]
            else:
                xPathRoot = None
            if "generateSubClasses" in args.xml2rdfOptions:
                generateSubClasses = args.xml2rdfOptions["generateSubClasses"]
            else:
                generateSubClasses = False

            document = Document().from_xml(
                instanceNamespace=instanceNamespace,
                instanceNamespacePrefix=instanceNamespacePrefix,
                path=path,
                docId=docId,
                ignoreWhitespace=ignoreWhitespace,
                instancesXmlidPrefix=instancesXmlidPrefix,
                xPathRoot=xPathRoot,
            )
            document.serialize(
                generateSubClasses=generateSubClasses,
                mode='graph',
                destination=f"{args.outDir}/{docId}.ttl"
            )
    else:
        NotImplemented
