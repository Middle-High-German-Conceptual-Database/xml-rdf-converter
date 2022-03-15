#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import uuid

from lxml import etree
from rdflib import RDF, RDFS, XSD, BNode, Graph, Literal, Namespace, URIRef
from tqdm import tqdm

patternXmlNs = re.compile("\{([^}]+)\}(.+)")
XMLO = Namespace("https://mhdbdbd.plus.ac.at/xml-ontology#")
XMLNS_PREFIX = 'mhdbdbxml'


class Node:
    uri: URIRef = None
    document: 'Document' = None

    def __init__(self, document: 'Document'):
        self.document = document
        self.document.nodeList.append(self)

    def _addToGraph(self, g, addOWLClassesProperties: bool):
        if self.document is not None and self.uri is not None:
            g.add((self.uri, XMLO.partOf, self.document.uri))

    def __str__(self):
        return f"""
            uri: {self.uri}
        """


class Attribute():
    name: str = None
    nameSpace: str = None
    value: str = None
    uri: URIRef = None
    document: 'Document' = None

    def __init__(self, document, name: str, value: str, nameSpace: str = None):
        self.name = name
        self.nameSpace = nameSpace
        self.value = value
        self.document = document
        self.uri = generateUri(ns=self.document.instanceNs,
                               instancesXmlidPrefix=self.document.instancesXmlidPrefix)

    def _addToGraph(self, g, addOWLClassesProperties: bool):
        g.add((self.uri, RDF.type, XMLO.Attribute))
        g.add((self.uri, XMLO.name, Literal(self.name, datatype=XSD.string)))
        if self.nameSpace is not None:
            g.add((self.uri, XMLO.nameSpace, Literal(
                self.nameSpace, datatype=XSD.anyURI)))
        g.add((self.uri, XMLO.value, Literal(self.value, datatype=XSD.string)))

    def __str__(self):
        return f"""
            Attribute
            name: {self.name}
            nameSpace: {self.nameSpace}
            value: {self.value}
        """


class Comment(Node):
    content: str = None

    def __init__(self, document: 'Document', content: str):
        super().__init__(document=document)
        self.content = content
        self.uri = generateUri(
            instancesXmlidPrefix=document.instancesXmlidPrefix)

    def _addToGraph(self, g, addOWLClassesProperties: bool):
        g.add((self.uri, RDF.type, XMLO.Comment))
        g.add((self.uri, XMLO.content, Literal(
            self.content, datatype=XSD.string)))

    def __str__(self):
        return f"""
            Comment
            content: {self.content}
        """


class Document:
    uri: URIRef = None
    root: 'Element' = None
    xmlSource: str = None
    nodeList: ['Node'] = []
    instanceNs: str = None
    instanceNsPrefix: str = None
    instancesXmlidPrefix: str = 'id#'
    nsMapXML: dict() = {}
    nsMapRDF: dict() = {}

    def __init__(
        self,
        uri: URIRef = None,
        root: 'Element' = None,
        xmlSource: str = None,
        nodeList: ['Node'] = [],
        instanceNs=None,
        instanceNsPrefix=None,
        instancesXmlidPrefix='id#'
    ):
        if uri is None:
            uri = generateUri()
        self.uri = uri
        self.root = root
        self.xmlSource = xmlSource
        self.uri = generateUri()
        self.nodeList = nodeList
        self.instanceNs = instanceNs
        self.instanceNsPrefix = instanceNsPrefix
        self.instancesXmlidPrefix = instancesXmlidPrefix

    @classmethod
    def from_xml(
        cls,
        path: str,
        docId: str,
        instanceNamespace: Namespace = None,
        instanceNamespacePrefix: str = None,
        instancesXmlidPrefix: str = 'id#',
        includeXMLsource: bool = False,
        ignoreWhitespace: bool = True,
        xPathRoot: str = None
    ):
        tree = etree.parse(path)
        uri = generateUri(instancesXmlidPrefix='',
                          xmlId=docId, ns=instanceNamespace)
        newDocument = cls()
        if includeXMLsource is True:
            newDocument.xmlSource = str(etree.tostring(tree))
        newDocument.uri = uri
        newDocument.instanceNs = instanceNamespace
        newDocument.instanceNsPrefix = instanceNamespacePrefix
        newDocument.instancesXmlidPrefix = instancesXmlidPrefix
        newDocument.nodeList = []
        root = tree.getroot()
        newDocument.nsMapXML = _getNameSpacesXml(root)
        newDocument.nsMapRDF = _getNameSpacesRDF(newDocument.nsMapXML)

        if xPathRoot is not None:
            try:
                root = root.xpath(
                    xPathRoot, namespaces=newDocument.nsMapXML)[0]

            except:
                print(
                    f'xPathRoot "{xPathRoot}" not found, fall back to document root.')

        _traverseXml(
            document=newDocument, xmlElement=root, ignoreWhitespace=ignoreWhitespace)
        return newDocument

    @classmethod
    def from_rdf(cls, path: str):
        NotImplementedError()

    def serialize(
        self,
        mode: str,
        format: str = 'turtle',
        destination: str = None,
        generateSubClasses: bool = True,
    ):
        if mode == "graph":
            print("Serialize to graph")
            g = Graph()
            g.namespace_manager.bind(XMLNS_PREFIX, XMLO)
            g.namespace_manager.bind(self.instanceNsPrefix, self.instanceNs)
            for prefix, ns in self.nsMapRDF.items():
                g.namespace_manager.bind(
                    prefix, ns)
            g.add((self.uri, RDF.type, XMLO.Document))
            if self.xmlSource is not None:
                g.add((self.uri, XMLO.xmlSource, Literal(
                    self.xmlSource, datatype=XSD.string)))
            g.add((self.uri, XMLO.root, self.root.uri))
            pbar = tqdm(total=len(self.nodeList))
            for node in self.nodeList:
                node._addToGraph(
                    g, addOWLClassesProperties=generateSubClasses)
                pbar.update()
            return g.serialize(format=format, destination=destination)
        elif mode == "xml":
            NotImplementedError()

    def __str__(self):
        return f"""
            Document
            root: {self.root}            
            xmlSource: {self.xmlSource}
        """


class Element(Node):
    name: str = None
    nameSpace: str = None
    attributes: ['Attribute'] = []
    children: ['Node'] = []

    def __init__(
        self,
        document: 'Document',
        name: str,
        nameSpace: str = None,
        attributes: ['Attribute'] = [],
        children: ['Node'] = [],
        xmlId: str = None,
        n: int = None
    ):
        super().__init__(document=document)
        self.name = name
        self.nameSpace = nameSpace
        self.attributes = attributes
        self.children = children
        self.document = document
        self.uri = generateUri(
            xmlId=xmlId,
            instancesXmlidPrefix=document.instancesXmlidPrefix
        )
        self.n = n

    def _addToGraph(self, g, addOWLClassesProperties: bool):
        super()._addToGraph(g, addOWLClassesProperties)
        g.add((self.uri, XMLO.name, Literal(self.name, datatype=XSD.string)))
        if self.n is not None:
            g.add((self.uri, XMLO.n, Literal(self.n, datatype=XSD.integer)))
        if self.nameSpace is not None:
            g.add((self.uri, XMLO.nameSpace, Literal(
                self.nameSpace, datatype=XSD.anyURI)))
        if (addOWLClassesProperties is True) and self.nameSpace is not None:
            owlClass = URIRef(
                self.nameSpace + ('#' if not(self.nameSpace.endswith('/') or self.nameSpace.endswith('#')) else '') + self.name)
            g.add((owlClass, RDFS.subClassOf, XMLO.Element))
            g.add((self.uri, RDF.type, owlClass))
        else:
            g.add((self.uri, RDF.type, XMLO.Element))

        try:
            if self.children[0] is not None:
                g.add((self.uri, XMLO.firstChild, self.children[0].uri))
            if self.children[-1] is not None:
                g.add((self.uri, XMLO.lastChild, self.children[-1].uri))
            for i in range(len(self.children)):
                g.add((self.children[i].uri, URIRef(
                    f"{str(XMLO)}index"), Literal(i, datatype=XSD.integer)))
                g.add((self.children[i].uri, XMLO.parent, self.uri))
                if i + 1 < len(self.children):
                    g.add((self.children[i].uri, XMLO.nextSibling,
                           self.children[i + 1].uri))
        except:
            pass

        for a in self.attributes:
            a._addToGraph(g, addOWLClassesProperties=addOWLClassesProperties)
            g.add((self.uri, XMLO.attribute, a.uri))

    def __str__(self):
        return f"""
            Element
            name: {self.name}       
            nameSpace: {self.nameSpace}     
            attributes: {[a for a in self.attributes] } 
        """


class Text(Node):
    content: str = None

    def __init__(self, document: 'Document', content: str):
        super().__init__(document=document)
        self.content = content
        self.uri = generateUri(
            instancesXmlidPrefix=document.instancesXmlidPrefix)

    def _addToGraph(self, g, addOWLClassesProperties: bool):
        super()._addToGraph(g, addOWLClassesProperties)
        g.add((self.uri, RDF.type, XMLO.Text))
        g.add((self.uri, XMLO.content, Literal(self.content)))

    def __str__(self):
        return f"""
            Text
            content: {self.content}            
            next: {self.nextNode}
        """


def _getNameSpacesXml(root: etree.Element, parseAllElements: bool = False) -> dict:
    if parseAllElements is True:
        nsmap = {}
        for element in root.find('.//*'):
            nsmap = {**nsmap, **element.nsmap}
        pass
    else:
        return root.nsmap


def _getNameSpacesRDF(nsMapXML: dict) -> dict:
    nsMapRDF = {}
    for prefix, ns in nsMapXML.items():
        owlClass = URIRef(
            ns + ('#' if not(ns.endswith('/') or ns.endswith('#')) else ''))
        nsMapRDF[prefix] = owlClass
    return nsMapRDF


def _traverseXml(document: 'Document', xmlElement: etree.Element, parentNode: 'Element' = None, ignoreWhitespace=True, pbar=None, nElements=None, rootPos=0):
    if parentNode is None:
        nElements = int(xmlElement.xpath("count(//*)")) - int(xmlElement.xpath(
            "count(preceding::*)")) - int(xmlElement.xpath("count(ancestor::*)"))
        rootPos = int(xmlElement.xpath("count(preceding::*)")) + \
            int(xmlElement.xpath("count(ancestor::*)"))
        pbar = tqdm(total=nElements)
    # Variables
    while xmlElement is not None:

        # Variables
        try:
            xmlId = xmlElement.get("{http://www.w3.org/XML/1998/namespace}id")
        except:
            xmlId = None

        m = patternXmlNs.match(xmlElement.tag)
        if m is not None:
            nameSpace = m[1]
            name = m[2]
        else:
            name = xmlElement.tag
            nameSpace = None

        try:
            text = xmlElement.text
            if text.isspace() and ignoreWhitespace is True:
                text = None
        except:
            text = None

        try:
            tail = xmlElement.tail
            if tail.isspace() and ignoreWhitespace is True:
                tail = None
        except:
            tail = None

        try:
            firstChildXml = xmlElement.getchildren()[0]
        except:
            firstChildXml = None

        try:
            nextElement = xmlElement.getnext()
        except:
            nextElement = None

        n = int(xmlElement.xpath("count(preceding::*)")) + \
            int(xmlElement.xpath("count(ancestor::*)")) - rootPos
        pbar.update()

        # Generate current Element
        elementNode = Element(
            document=document,
            name=name,
            nameSpace=nameSpace,
            xmlId=xmlId,
            children=[],
            n=n,
            attributes=[]
        )

        for _attribute, _value in xmlElement.attrib.items():
            m = patternXmlNs.match(_attribute)
            if m is not None:
                nameSpaceA = m[1]
                nameA = m[2]
            else:
                nameA = _attribute
                nameSpaceA = nameSpace
            attribute = Attribute(
                document=document,
                name=nameA,
                nameSpace=nameSpaceA,
                value=_value
            )
            elementNode.attributes.append(attribute)

        if parentNode is not None:
            parentNode.children.append(elementNode)
        else:
            document.root = elementNode

        # Process Tail
        if tail is not None and parentNode is not None:
            tailNode = Text(
                document=document,
                content=tail
            )
            parentNode.children.append(tailNode)

        # Process Text
        if text is not None:
            textNode = Text(
                document=document,
                content=text,
            )
            elementNode.children.append(textNode)

        # Call _traverseXml with firstChildXml
        if firstChildXml is not None:
            _traverseXml(
                document=document,
                xmlElement=firstChildXml,
                parentNode=elementNode,
                ignoreWhitespace=ignoreWhitespace,
                pbar=pbar,
                nElements=nElements,
                rootPos=rootPos
            )

        # Process nextElement
        xmlElement = nextElement


def generateUri(ns: Namespace = None, xmlId: str = None, instancesXmlidPrefix: str = 'id#') -> URIRef:
    if xmlId is None:
        uri = URIRef(str(f"{str(ns)}{instancesXmlidPrefix}{uuid.uuid4()}"))
    else:
        uri = URIRef(str(f"{str(ns)}{instancesXmlidPrefix}{xmlId}"))
    return uri
