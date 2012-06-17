
# Contains functions and variables that control the building of 
# distributions.

init -1000 python in build:
    
    def make_file_lists(s):
        """
        Turns `s` into a (perhaps empty) list of file_lists.
        
        If `s` is a list or None, then returns it. If it's a string, splits
        it on whitespace. Otherwise, errors out.
        """
        
        if s is None:
            return s
        elif isinstance(s, list):
            return s
        elif isinstance(s, basestring):
            return s.split()
            
        raise Exception("Expected a string, list, or None.")
    


    def pattern_list(l):
        """
        Apply file_lists to the second argument of each tuple in a list.
        """
        
        rv = [ ]
        
        for pattern, groups in l:
            rv.append((pattern, make_file_lists(groups)))
            
        return rv

    # Patterns that are used to classify Ren'Py.
    renpy_patterns = pattern_list([
        ( "**~", None),
        ( "**/.*", None),
        ( "**.old", None),
        ( "**.new", None),
        ( "**.rpa", None),

        ( "**/*.pyc", None),

        ( "renpy.py", "all"),
        ( "renpy/**", "all"),
        ( "common/**", "all"),

        # Windows-specific patterns.
        ( "python*.dll", "windows" ),
        ( "msvcr*.dll", "windows"),
        ( "Microsoft.VC*.CRT.manifest", "windows"),
        ( "lib/dxwebsetup.exe", "windows"),
        ( "lib/windows-x86/**", "windows"),
        
        # Linux patterns. 
        ( "renpy.sh", "linux"),
        ( "lib/linux-x86/**", "linux"),
        ( "lib/linux-x64/**", "linux"),
        ( "lib/python", "linux"),
        
        # Mac patterns.
        ( "renpy.app/Contents/Ren'Py Launcher", None),
        ( "renpy.app/Contents/Info.plist", None),
        ( "renpy.app/Contents/Resources/launcher.py", None),
        ( "renpy.app/Contents/Resources/launcher.icns", None),
        ( "renpy.app/**", "mac"),
        
        # Shared patterns.
        ( "/lib/", "windows linux"),
    ])

 
    def classify_renpy(pattern, groups):
        """
        Classifies files in the Ren'Py base directory according to pattern.
        """
        
        renpy_patterns.append(pattern, make_file_lists(groups))

    # Patterns that are relative to the base directory.
    
    early_base_patterns = pattern_list([ 
        ("*.py", None),
        ("*.sh", None),
        ("*.app/", None),
        ("*.dll", None),
        ("*.manifest", None),
        
        ("lib/", None),
        ("renpy/", None),
        ("update/", None),
        ("common/", None),
        ("update/", None),

        ("icon.ico", None),
        ("icon.icns", None),
        ("project.json", None),
        ("tmp/", None),

        ("archived/", None),
        ("launcherinfo.py", None),
        ("android.txt", None),
        ])
    
    base_patterns = [ ]
    
    late_base_patterns = pattern_list([
        ("**", "all")
        ])
    
    def classify(pattern, file_list):
        """
        :doc: build
        
        Classifies files that match `pattern` into `file_list`.
        """
        
        base_patterns.append((pattern, make_file_lists(file_list)))
        
    def clear():
        """
        :doc: build
        
        Clears the list of patterns used to classify files.
        """
        
        base_patterns[:] = [ ]
      
    # Archiving.
      
    archives = [ ]
    
    def archive(name, file_list="all"):
        """
        :doc: build
        
        Declares the existence of an archive. If one or more files are 
        classified with `name`, `name`.rpa is build as an archive. The 
        archive is included in the named file lists.
        """
        
        archives.append((name, make_file_lists(file_list)))
        
    archive("archive", "all") 
        
    # Documentation patterns.
    
    documentation_patterns = [ ]
    
    def documentation(pattern):
        """
        :doc: build
        
        Declares a pattern that matches documentation. In a mac app build, 
        files matching the documentation pattern are stored twice - once
        inside the app package, and again outside of it.
        """
        
    # Packaging.
        
    packages = [ ]
    
    def package(name, format, file_lists, description=None):
        """
        :doc: build
        
        Declares a package that can be built by the packaging
        tool. 
        
        `name`
            The name of the package.
        
        `format`
            The format of the package. One of:
        
            zip
                A zip file. 
            app-zip
                A zip file containing a macintosh application.
            tar.bz2
                A tar.bz2 file.

        `file_lists`
            A list containing the file lists that will be contained
            within the package.
        
        `description`
            An optional description of the package to be built.
        """

        if format not in [ "zip", "app-zip", "tar.bz2" ]:
            raise Exception("Format {} not known.".format(format))
            
        if description is None:
            description = Name
            
        d = {
            "name" : name,
            "format" : format,
            "file_lists" : make_file_lists(file_lists),
            "description" : description
            }
            
        packages.append(d)

    package("all", "zip", "windows mac linux all", "All Desktop Platforms")
    package("linux", "tar.bz2", "linux all", "Linux x86/x86_64")
    package("mac", "app-zip", "mac all", "Macintosh x86")
    package("win", "zip", "windows all", "Windows x86")
        
    # Data that we expect the user to set.
    
    # The name of directories in the archives.
    directory_name = ""

    # The name of executables.
    executable_name = ""
    
    # Should we include update information into the archives?
    include_update = False
    
    # This function is called by the json_dump command to dump the build data 
    # into the json file.
    def dump():
        rv = { }
        
        rv["directory_name"] = directory_name
        rv["executable_name"] = executable_name
        rv["include_update"] = include_update
        
        rv["packages"] = packages
        rv["archives"] = archives
        rv["documentation_patterns"] = documentation_patterns
        rv["base_patterns"] = early_base_patterns + base_patterns + late_base_patterns
        rv["renpy_patterns"] = renpy_patterns
    
        return rv
