#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import re
import copy
from onto import Onto


class Console:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @classmethod
    def log(klass, string):
        print(klass.OKGREEN + string + klass.ENDC)

    @classmethod
    def llog(klass, string):
        print("  " + klass.OKBLUE + string + klass.ENDC)

    @classmethod
    def lllog(klass, string):
        print("    " + string)

    @classmethod
    def warn(klass, string):
        print(klass.WARNING + string + klass.ENDC)

    @classmethod
    def err(klass, string):
        print(klass.FAIL + string + klass.ENDC, file=sys.stderr)

    @classmethod
    def info(klass, string):
        print(string)

class CodeHolder:
    def __init__(self, code):
        self.code = re.sub(r"\\", r"\\\\", code)

    def replace_mask(self, mask, value):
        self.code = re.sub("%<" + mask + ">", value, self.code)
        return self

    def copy(self):
        return CodeHolder(self.code)

    def depends_on_instance(self):
        return "%<instance_id>" in self.code

    def resolve_scivi_include_masked(self, mask):
        includes = re.findall("#" + mask + "<(.*?)>", self.code)
        for include in includes:
            Console.lllog("Including code from <" + include + ">")
            with open(include) as f:
                # HINT: split+merge is more than 110 times faster than re.sub on large files o_O
                # content = re.sub(r"\\", r"\\\\", f.read())
                # self.code = re.sub("#scivi_include_thirdparty<" + include + ">", content, self.code)
                content = f.read()
                parts = self.code.split("#" + mask + "<" + include + ">")
                newCode = ""
                for i in xrange(0, len(parts) - 1, 2):
                    newCode = newCode + parts[i] + content + parts[i + 1]
                self.code = newCode
        return self

    def resolve_scivi_includes(self):
        return self.resolve_scivi_include_masked("scivi_include")

    def resolve_thirdparty_includes(self):
        return self.resolve_scivi_include_masked("scivi_include_thirdparty")

    def include_code(self, code, mask):
        return self.replace_mask(mask, code + "\n%<" + mask + ">")

    def remove_mask(self, mask):
        return self.replace_mask(mask, "")

class Generator:
    def __init__(self, dataflow):
        self.dataFlow = dataflow
        self.onto = Onto(self.dataFlow["onto"])
        Console.log("Ontology loaded from <" + self.dataFlow["onto"] + ">")
        self.workingCodeBlocks = []
        self.defaultLanguage = None

    def is_meta_code_block(self, codeBlock):
        if self.onto.is_node_of_type(codeBlock, "Code Block"):
            return False
        if self.onto.first(self.onto.get_nodes_linked_from(codeBlock, "language")) == None:
            raise ValueError("node <" + codeBlock["name"] + "> treated as meta code block has no language defined")
        return True

    def get_code(self, codeBlock, instanceID):
        if self.is_meta_code_block(codeBlock):
            return None
        code = None
        if "code" in codeBlock:
            code = codeBlock["code"]
        else:
            attr = codeBlock["attributes"]
            if "inline" in attr:
                Console.lllog("Using inline code from <" + codeBlock["name"] + ">")
                code = CodeHolder(attr["inline"])
                codeBlock["code"] = code
            elif "path" in attr:
                filename = attr["path"]
                with open(filename) as f:
                    code = CodeHolder(f.read())
                codeBlock["code"] = code
                Console.lllog("Using code from <" + filename + ">")
            else:
                raise ValueError("empty code block <" + codeBlock["name"] + ">")
            code.resolve_scivi_includes()
        impls = None
        if "impls" in codeBlock:
            impls = codeBlock["impls"]
        if not impls:
            if code.depends_on_instance():
                impls = {}
                codeBlock["impls"] = impls
            else:
                return code
        if instanceID in impls:
            return impls[instanceID]
        else:
            c = code.copy().replace_mask("instance_id", instanceID)
            impls[instanceID] = c
            return c

    def get_implementations(self, codeBlock):
        if "impls" in codeBlock:
            return codeBlock["impls"].values()
        elif "code" in codeBlock:
            return [codeBlock["code"]]
        else:
            raise ValueError("code block <" + codeBlock["name"] + "> used but not proessed")

    def get_language(self, codeBlock):
        return self.onto.first(self.onto.get_nodes_linked_from(codeBlock, "language"))["name"]

    def apply_setting(self, node, value, instanceID):
        codeBlocks = self.onto.get_nodes_linked_from(node, "use_for")
        for cb in codeBlocks:
            self.get_code(cb, instanceID).replace_mask(node["name"], value)

    def process_settings(self, node, values, instanceID):
        settings = self.onto.get_typed_nodes_linked_from(node, "has", "Setting")
        for s in settings:
            if s["id"] in values:
                self.apply_setting(s, values[s["id"]], instanceID)
            elif "default" in s["attributes"]:
                self.apply_setting(s, s["attributes"]["default"], instanceID)
            else:
                raise ValueError("setting <" + s["name"] + "> has no value nor default")

    def get_suitable_code_block(self, codeBlocks, language):
        if language == None:
            return self.onto.first(codeBlocks)
        for cb in codeBlocks:
            if self.get_language(cb) == language:
                return cb
        for cb in codeBlocks:
            if self.get_language(cb) == self.defaultLanguage:
                return cb
        return None

    def append_code_block(self, codeBlock, instanceID):
        self.get_code(codeBlock, instanceID)
        if not (codeBlock in self.workingCodeBlocks):
            self.workingCodeBlocks.append(codeBlock)
        children = self.onto.get_typed_nodes_linked_to(codeBlock, "a_part_of", "Code Block")
        for child in children:
            self.append_code_block(child, instanceID)

    def get_output_socket_and_src_df_node(self, inSocket):
        for link in self.dataFlow["links"]:
            if link["socket_to"] == inSocket["id"]:
                return self.onto.get_node_by_id(link["socket_from"]), self.dataFlow["nodes"][link["node_from"]]
        return None, None

    def process_node(self, dfNode, dstLanguage):
        node = self.onto.get_node_by_id(dfNode["id"])

        instanceID = str(dfNode["instance_id"])
        instances = self.onto.get_nodes_linked_to(node, "instance_of")
        requiredLanguage = dstLanguage
        if len(instances) == 1:
            requiredLanguage = self.get_language(instances[0])
        codeBlock = self.get_suitable_code_block(instances, dstLanguage)
        if codeBlock == None:
            raise ValueError("no suitable code block of <" + node["name"] + "> found")
        self.append_code_block(codeBlock, str(dfNode["instance_id"]))

        if "settings" in dfNode:
            self.process_settings(node, dfNode["settings"], instanceID)

        inSockets = self.onto.get_typed_nodes_linked_from(node, "has", "Input")
        for inSocket in inSockets:
            inCodeBlocks = self.onto.get_typed_nodes_linked_from(inSocket, "use_for", "Code Block")
            if (inCodeBlocks == None) or (len(inCodeBlocks) == 0):
                raise ValueError("no code blocks use input socket <" + inSocket["name"] + "> of node <" + node["name"] + ">")
            result = None
            outSocket, sourceDFNode = self.get_output_socket_and_src_df_node(inSocket)
            if outSocket != None:
                self.process_node(sourceDFNode, requiredLanguage)
                result = outSocket["result"]
            elif "default" in inSocket["attributes"]:
                result = inSocket["attributes"]["default"]
            else:
                raise ValueError("input socket <" + inSocket["name"] + "> of node <" + node["name"] + "> is not connected to anything nor has default")
            for cb in inCodeBlocks:
                self.get_code(cb, instanceID).replace_mask(inSocket["name"], result)

        outSockets = self.onto.get_typed_nodes_linked_from(node, "has", "Output")
        for outSocket in outSockets:
            outCodeBlock = self.get_suitable_code_block(self.onto.get_typed_nodes_linked_to(outSocket, "use_for", "Code Block"), dstLanguage)
            if outCodeBlock == None:
                raise ValueError("no code block found for output socket <" + outSocket["name"] + "> of node <" + node["name"] + ">")
            outSocket["result"] = self.get_code(outCodeBlock, instanceID).code

    def process_code_block(self, codeBlock):
        masks = self.onto.get_typed_nodes_linked_from(codeBlock, "has", "Code Mask")
        dstImpls = self.get_implementations(codeBlock)
        for mask in masks:
            usedCodeBlocks = self.onto.get_typed_nodes_linked_to(mask, "use_for", "Code Block")
            for cb in usedCodeBlocks:
                if cb in self.workingCodeBlocks:
                    self.process_code_block(cb)
                    srcImpls = self.get_implementations(cb)
                    for src in srcImpls:
                        for dst in dstImpls:
                            dst.include_code(src.code, mask["name"])
            for dst in dstImpls:
                dst.remove_mask(mask["name"])

    def run(self):
        Console.log("Firmware generation started")

        hostNode = self.onto.get_node_by_id(self.dataFlow["host"]["id"])
        Console.llog("Host is " + hostNode["name"])
        self.frame = self.onto.first(self.onto.get_typed_nodes_linked_from(hostNode, "has", "Code Block"))
        if self.frame == None:
            raise ValueError("firmware template not found")

        self.defaultLanguage = self.get_language(self.frame)
        Console.llog("Ouput language is " + self.defaultLanguage)

        self.get_code(self.frame, None)
        self.process_settings(hostNode, self.dataFlow["host"]["settings"], "")

        dataFlowNodes = self.dataFlow["nodes"]
        index = 0
        for df in dataFlowNodes:
            df["instance_id"] = index
            index = index + 1
        for df in dataFlowNodes:
            if ("endPoint" in df) and (df["endPoint"] == True):
                self.process_node(df, None)

        self.process_code_block(self.frame)

        self.frame["code"].resolve_thirdparty_includes()

        Console.log("Firmware generation successfull")

    def code(self):
        return self.frame["code"].code

def generate(dataflow):
    generator = Generator(dataflow)
    try:
        generator.run()
    except ValueError as e:
        Console.err("Firmware generation failed: " + e.message);
        exit(0)
    return generator.code()

################ MAIN ################
if __name__ == '__main__':
    if len(sys.argv) != 3:
        Console.warn("Usage: codegen.py dataflow.json firmware.ino")
        exit(0)

    with open(sys.argv[1]) as f:
        dataflow = json.load(f)
        Console.log("Data flow diagram loaded from <" + sys.argv[1] + ">")
        code = generate(dataflow)
        with open(sys.argv[2], "w") as f:
            f.write(code)

    Console.log("Output written to " + sys.argv[2])
