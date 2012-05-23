csharp-to-python
================

Python script for converting C# code to Python.

    5-1-2012 NSC
    
    When tasked with redeveloping an existing (and very robust) ASP.NET application
    using Python, a search for converters yielded minimal useful results.  Several 
    commercial tools exists, as well as a handful of online services (one of which has been 
    down for at least six months as of today), but none were really working for the 
    task at hand.
    
    While prototyping and familiarizing myself with Python, several pages
    and webmethods were converted by hand.  In doing so a repeatable process emerged.
    
    Under the hood Python and C# have more differences than can be discussed, 
    however the pure syntax of a source file, line by line, is moderately translatable.
    
    This conversion script was created to speed up the repetitive refactoring operations
    for each function in C#.  It greatly reduced overall conversion time.
    
    Keep in mind, since C# and Python are both OO languages, this process is by no means foolproof.
    
    It should be noted, as you would expect, that language specific classes and types are not 
    easily converted, and this script does not attempt to do so.
    
    What it does is simple - find and replace operations on a block of source code, line by line.
    Converting common C# language keywords to their Python equivalent.
    
    
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
    
    FINAL NOTE:
    Every programmer has different habits, naming conventions, etc.  Certain parts of this
    process were specifically intended for converting *my own naming conventions* in the C# code.
    
    Those lines are commented out, but left here as a reference/guide as you create your own 
    customized replacements.