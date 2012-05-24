#!/usr/bin/env python

#########################################################################
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#########################################################################

"""
    Conversion Utility for C#.NET to Python.
    
    5-1-2012 NSC
    
    Use is simple:
    1) create a file called convert.in, and place the block of C# code in it.
        (This utility works best one function at a time.)
    2) run this script (./convert.py)
    3) the results of the conversion will be written to convert.out.
    
    NOTE: there is a mode that makes a fair attempt at converting .aspx files to standard html.
    To try that:
    1) place your .aspx markup in convert.in
    2) run this script with an argument (./convert.py aspx)
    3) results are in convert.out.
"""

import re
import sys

out = ""

with open("convert.in", 'r') as f_in:
    if not f_in:
        print "ERROR: convert.in not found."

    for line in f_in:
        # FIRST THINGS FIRST ... for Python, we wanna fix tabs into spaces...
        # we want all our output to have spaces instead of tabs
        line = line.replace("\t", "    ")

        
        # we look for a command line arg to tell us if the input file might be .aspx (html)
        # if it is it's this special block.
        # the default is below
        if (len(sys.argv) > 1):
            if( sys.argv[1] == 'aspx' ):
                # this is the aspx -> html conversion

                line = line.replace(" runat=\"server\"", "")
                line = line.replace("CssClass", "class")
                
                # this before the TextBox replace
                if "TextMode=\"MultiLine\"" in line:
                    line = line.replace("<asp:TextBox ID", "<textarea id").replace("></asp:TextBox>", "></textarea>")
                    line = line.replace(" TextMode=\"MultiLine\"", "").replace("Rows", "rows")

                line = line.replace("<asp:TextBox ID", "<input type=\"text\" id").replace("></asp:TextBox>", " />")
                line = line.replace("<asp:Label ID", "<span id").replace("></asp:Label>", "></span>")
                line = line.replace("<asp:HiddenField ID", "<input type=\"hidden\" id").replace("></asp:HiddenField>", " />")
                line = line.replace("<asp:DropDownList ID", "<select id").replace("</asp:DropDownList>", "</select>")
                line = line.replace("<asp:ListItem", "<option").replace("</asp:ListItem>", "</option>")

                # not all placeholders or literals convert to divs...
                line = line.replace("<asp:PlaceHolder", "#######<asp:PlaceHolder")
                line = line.replace("<asp:Literal", "#######<asp:Literal")

        else:
            
            # This is the C# -> Python conversion
            INDENT = 0
            sINDENTp4 = "    "
    
            
            # now that the tabs are fixed, 
            # we wanna count the whitespace at the beginning of the line
            # might use it later for indent validation, etc.
            p = re.compile(r"^\s+")
            m = p.match(line)
            if m:
                INDENT = len(m.group())
            
            #if INDENT > 0 and INDENT < 4:
            #    line = "SHORT INDENT\n" + line
                
            #if INDENT >= 4:
            #    if INDENT % 4:
            #        line = "!! BAD INDENT\n" + line
    
            sINDENT = " " * INDENT
            # this string global contains the current indent level + 4
            sINDENTp4 = " " * (INDENT+4)
            # + 8
            sINDENTp8 = " " * (INDENT+8)
            
            # braces are a tricky, but lets first just remove any lines that only contain an open/close brace
            if line.strip() == "{": continue
            if line.strip() == "}": continue
                  
            # if the brace appears at the end of a line (like after an "if")
            if len(line.strip()) > 1:
                s = line.strip()
                if s[-1] == "{":
                    line = s[:-1]
            
            # comments
            if line.strip()[:2] == "//":
                line = line.replace("//", "# ")
            line = line.replace("/*", "\"\"\"").replace("*/", "\"\"\"")
            # some comments are at the end of a line
            line = line.replace("; //", " # ")
    
            
            
            # Fixing semicolon line endings (not otherwise, may be in a sql statement or something)
            line = line.replace(";\n", "\n")
    
            # Fixing line wrapped string concatenations
            line = line.replace(") +\n", ") + \\\n") # lines that had an inline if still need the +
            line = line.replace("+\n", "\\\n")
    
            
            # Fixing function declarations...    
            line = line.replace("public ", "def ")
            line = line.replace("private ", "def ")
            if line.strip()[:3] == "def":
                line = line.replace(")", "):")
            
            # Fixing variable declarations...    
            # doing "string" and "int" again down below with a regex, because they could be a line starter, or part of a bigger word
            line = line.replace(" int ", " ").replace(" string ", " ").replace(" bool ", " ").replace(" void ", " ")
            line = line.replace("(int ", "(").replace("(string ", "(").replace("(bool ", "(")
    
            # common C# functions and keywords
            line = line.replace(".ToString()", "") # no equivalent, not necessary
            line = line.replace(".ToLower()", ".lower()")
            line = line.replace(".IndexOf(", ".find(")
            line = line.replace(".Replace", ".replace")
            line = line.replace(".Split", ".split")
            line = line.replace(".Trim()", ".strip()")
            line = line.replace("else if", "elif")
            line = line.replace("!string.IsNullOrEmpty(", "")
            line = line.replace("string.IsNullOrEmpty(", "not ")
            line = line.replace("this.", "self.")

            # Try/Catch blocks
            line = line.replace("try", "try:")
            line = line.replace("catch (Exception ex)", "except Exception:")
            # I often threw "new exceptions" - python doesn't need the extra stuff
            line = line.replace("new Exception", "Exception")
            line = line.replace("throw", "raise")

            # NULL testing
            line = line.replace("== null", "is None")
            line = line.replace("!= null", "is not None")
            

#            ##### CUSTOM REPLACEMENTS #####
#            line = line.replace("\" + Environment.NewLine", "\\n\"")
#            line = line.replace("HttpContext.Current.Server.MapPath(", "") # this will leave a trailing paren !
#            line = line.replace(").Value", ", \"\") # WAS A .Value - confirm") #should work most of the time for Cato code
#            line = line.replace(".Length", ".__LENGTH")
#    
#            #these commonly appear on a line alone, and we aren't using them any more
#            if line.strip() == "dataAccess dc = new dataAccess()": continue
#            if line.strip() == "acUI.acUI ui = new acUI.acUI()": continue
#            if line.strip() == "sErr = \"\"": continue
#            if line.lower().strip() == "ssql = \"\"": continue # there's mixed case usage of "sSql"
#            if "dataAccess.acTransaction" in line: continue
#            if line.strip() == "DataRow dr = null": continue
#            if line.strip() == "DataTable dt = new DataTable()": continue
#            if "FunctionTemplates.HTMLTemplates ft" in line: continue
#    
#            
#            # a whole bunch of common phrases from Cato C# code
#            line = line.replace("Globals.acObjectTypes", "uiGlobals.CatoObjectTypes")
#            line = line.replace("ui.", "uiCommon.")
#            line = line.replace("ft.", "ST.") # "FunctionTemplates ft is now import stepTemplates as sST"
#            line = line.replace("dc.IsTrue", "uiCommon.IsTrue")
#            line = line.replace("../images", "static/images")
#            line = line.replace("dc.EnCrypt", "catocommon.cato_encrypt")
#    
#            #99% of the time we won't want a None return, but an empty string instead
#            line = line.replace("return\n", "return \"\"\n")
#            
#            
#            
#            # this will *usually work
#            line = line.replace("if (!dc.sqlExecuteUpdate(sSQL, ref sErr))", "if not uiGlobals.request.db.exec_db_noexcep(sSQL):")
#            if "!dc.sqlGetSingleString" in line:
#                line = sINDENT + "00000 = uiGlobals.request.db.select_col_noexcep(sSQL)\n" + sINDENT + "if uiGlobals.request.db.error:\n"
#
#            if "!dc.sqlGetDataTable" in line:
#                line = sINDENT + "00000 = uiGlobals.request.db.select_all_dict(sSQL)\n" + sINDENT + "if uiGlobals.request.db.error:\n"
#
#            line = line.replace("+ sErr", "+ uiGlobals.request.db.error") # + sErr is *usually used for displaying a db error.  Just switch it.
#            line = line.replace("(sErr)", "(uiGlobals.request.db.error)") # sometimes it's in a log message as the only arg
#            line = line.replace("if (!oTrans.ExecUpdate(ref sErr))", "if not uiGlobals.request.db.tran_exec_noexcep(sSQL):")
#            line = line.replace("oTrans.Command.CommandText", "sSQL") # transactions are different, regular sSQL variable
#            line = line.replace("oTrans.Commit()", "uiGlobals.request.db.tran_commit()")
#            line = line.replace("oTrans.RollBack()", "uiGlobals.request.db.tran_rollback()")
#            line = line.replace("DataRow dr in dt.Rows", "dr in dt")
#            line = line.replace("dt.Rows.Count > 0", "dt")
#            line = line.replace("Step oStep", "oStep")
#            line = line.replace("+ i +", "+ str(i) +")
#            line = line.replace("i+\\", "i += 1")
#            
#            # this will be helpful
#            if " CommonAttribs" in line:
#                line = "### CommonAttribsWithID ????\nuiCommon.NewGUID()\n" + line
#
#
#            # random stuff that may or may not work
#            if line.strip() == "if (!dc.sqlGetDataRow(ref dr, sSQL, ref sErr))":
#                line = sINDENT + "dr = uiGlobals.request.db.select_row_dict(sSQL)\n" + sINDENT + "if uiGlobals.request.db.error:\n" + sINDENTp4 + "raise Exception(uiGlobals.request.db.error)\n"
#            if line.strip() == "if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))":
#                line = sINDENT + "dt = uiGlobals.request.db.select_all_dict(sSQL)\n" + sINDENT + "if uiGlobals.request.db.error:\n" + sINDENTp4 + "raise Exception(uiGlobals.request.db.error)\n"
#
#            # true/false may be problematic, but these should be ok
#            line = line.replace(", true", ", True").replace(", false", ", False")
#            
#            ##### END CUSTOM #####

            
            # xml/Linq stuff
            # the following lines were useful, but NOT foolproof, in converting some Linq XDocument/XElement stuff
            # to Python's ElementTree module.
            line = line.replace(".Attribute(", ".get(")
            line = line.replace(".Element(", ".find(")
            
            line = line.replace("XDocument.Load", "ET.parse")
            line = line.replace("XDocument ", "").replace("XElement ", "")
            line = line.replace("XDocument.Parse", "ET.fromstring")
            line = line.replace("IEnumerable<XElement> ", "")
            
            # note the order of the following
            line = line.replace(".XPathSelectElements", ".findall").replace(".XPathSelectElement", ".find") 
            line = line.replace(".SetValue", ".text")
            
            line = line.replace("ex.Message", "traceback.format_exc()")
    
    
#            ##### CUSTOM #####
#            #!!! this has to be done after the database stuff, because they all use a "ref sErr" and we're matching on that!
#            # passing arguments by "ref" doesn't work in python, mark that code obviously
#            # because it need attention
#            line = line.replace("ref ", "0000BYREF_ARG0000")
#    
#            # the new way of doing exceptions - not raising them, appending them to an output object
#            line = line.replace("raise ex", "uiGlobals.request.Messages.append(traceback.format_exc())")
#            line = line.replace("raise Exception(", "uiGlobals.request.Messages.append(")
#            
#    
#            # if this is a function declaration and it's a "wm" web method, 
#            # throw the new argument getter line on there
#            if "def wm" in line:
#                s = ""
#                p = re.compile("\(.*\)")
#                m = p.search(line)
#                if m:
#                    args = m.group().replace("(","").replace(")","")
#                    for arg in args.split(","):
#                        s = s + sINDENTp4 + "%s = uiCommon.getAjaxArg(\"%s\")\n" % (arg.strip(), arg.strip())
#                    
#                line = line.replace(args, "self") + s
#    
#            ##### END CUSTOM #####
            
            # else statements on their own line
            if line.strip() == "else":
                line = line.replace("else", "else:")

    
            # let's try some stuff with regular expressions
            # string and int declarations
            p = re.compile("^int ")
            m = p.match(line)
            if m:
                line = line.replace("int ", "")
            p = re.compile("^string ")
            m = p.match(line)
            if m:
                line = line.replace("string ", "")
            
            # if statements
            p = re.compile(".*if \(.*\)")
            m = p.match(line)
            if m:
                line = line.replace("if (", "if ")
                line = line[:-2] + ":\n"
                line = line.replace("):", ":")
    
            # foreach statements (also marking them because type declarations may need fixing)
            p = re.compile(".*foreach \(.*\)")
            m = p.match(line)
            if m:
                line = line.replace("foreach (", "for ")
                line = line[:-2] + ":\n"
                line = "### CHECK NEXT LINE for type declarations !!!\n" + line
    
            p = re.compile(".*while \(.*\)")
            m = p.match(line)
            if m:
                line = line.replace("while (", "while ")
                line = line[:-2] + ":\n"
                line = "### CHECK NEXT LINE for type declarations !!!\n" + line
    
            # this is a crazy one.  Trying to convert inline 'if' statements
            #first, does it look like a C# inline if?
            p = re.compile("\(.*\?.*:.*\)")
            m = p.search(line)
            if m:
                pre_munge = m.group()
                
                # ok, let's pick apart the pieces
                p = re.compile("\(.*\?")
                m = p.search(line)
                if_part = m.group().replace("(", "").replace("?", "").replace(")", "").strip()
                
                p = re.compile("\?.*:")
                m = p.search(line)
                then_part = m.group().replace(":", "").replace("?", "").strip()
                
                p = re.compile(":.*\)")
                m = p.search(line)
                else_part = m.group().replace(":", "").replace("?", "").replace(")", "").strip()
                
                #now reconstitute it (don't forget the rest of the line
                post_munge = "(%s if %s else %s)" % (then_part, if_part, else_part)
                line = line.replace(pre_munge, post_munge)
                
            # && and || comparison operators in an "if" statement
            p = re.compile("^.*if.*&&")
            m = p.search(line)
            if m:
                line = line.replace("&&", "and")
                # line = "### VERIFY 'ANDs' !!!\n" + line
    
            p = re.compile("^.*if.*\|\|")
            m = p.search(line)
            if m:
                line = line.replace("||", "or")
                # line = "### VERIFY 'ORs' !!!\n" + line
        

        # ALL DONE!
        out += line
    
with open("convert.out", 'w') as f_out:
    if not f_out:
        print "ERROR: unable to create convert.out."

    f_out.write(out)
