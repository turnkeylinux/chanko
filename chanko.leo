<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.486246672582">
	<global_window_position top="0" left="5" height="709" width="1127"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="loni.20100902123045" a="E"><vh>Project</vh>
<v t="loni.20100902123045.1" a="E"><vh>design</vh>
<v t="loni.20100902123045.2"><vh>brainstorming</vh></v>
<v t="loni.20100902123045.3"><vh>file/data structure</vh></v>
<v t="loni.20100902123045.4"><vh>cli syntax</vh></v>
<v t="loni.20100902123045.5"><vh>usage examples</vh></v>
</v>
<v t="loni.20100902123045.6" a="E"><vh>implementation</vh>
<v t="loni.20100902123045.7" a="M"><vh>create test environment</vh>
<v t="loni.20100902123045.8"><vh>conf</vh></v>
<v t="loni.20100902123045.9"><vh>init</vh></v>
<v t="loni.20100902123045.10"><vh>refresh-r</vh></v>
<v t="loni.20100902123045.11"><vh>refresh-l</vh></v>
<v t="loni.20100902123045.12"><vh>get</vh></v>
<v t="loni.20100902123045.13"><vh>query-r</vh></v>
<v t="loni.20100902123045.14"><vh>query-l</vh></v>
</v>
<v t="loni.20100902180534"><vh>refresh</vh></v>
<v t="loni.20100903152430"><vh>query</vh></v>
<v t="loni.20100904214912" a="E"><vh>sumo integration</vh>
<v t="loni.20100904214912.1"><vh>use case</vh></v>
<v t="loni.20100904215050" a="TV"><vh>file/data structure</vh></v>
</v>
<v t="loni.20100902123045.15"><vh>TODO</vh></v>
</v>
</v>
</vnodes>
<tnodes>
<t tx="loni.20100902123045">@nocolor
</t>
<t tx="loni.20100902123045.1"></t>
<t tx="loni.20100902123045.2">Q: what should i call this project?

alternatives:
    prestine
    upstream
    sumoapt
    vanilla
    cosmos
    debin
    debimport
    chanko
    sushi
    aptly
    aptic


A:  chanko
    short for chanko-nabe, which is a stew (a type of nabemono or one-pot dish) commonly
    eaten in vast quantity by sumo wrestlers as part of a weight gain diet.
    
    chanko leverages sumo, hence the perfect name



leverage apt?
    interface directly with apt-get|cache
    interface directly with the apt library
    use the python interface
        python-apt
        proxy-apt

    problem?: apt is integrated with the local systems package management
    not a problem: apt's configuration can be very tweaked in fine detail

exploration
    see if we can manipulate using apt-get and/or apt-cache directly
    see if we can leverage python-apt as is
    consider leverageing python-apt code as opposed to using what i already have
    
    tests
        setup confined apt configuration (sources.list, preferences + directories)
            + test apt-cache and apt-get
            + test python-apt

    note: i CANNOT use apt-get for the actual download when in sumo, defeats the purpose
            but maybe i can get it to just print out the URI instead

test: apt-cache and apt-get
    this whole project can leverage apt-get and apt-cache, basically high-level wrappers
    less code for us to write
    more powerful options available
    
    we just gotta setup the directory structure and a custom apt.conf,
    and pass apt-get|cache -c /path/to/conf
    
    we pass apt-get --print-uri so instead of downloading, it prints out the uri,
    which we take and pass to sumo-get
    
    we can then hardlink the deb in archives so apt knows about it
    
    this is a *hack*, although powerful and would work, not very extendable
        Q: what if we can do the same thing, but leverage python-apt to do our bidding
           instead of apt-get

test: python-apt
    not very high-level code.
    it does what it is meant to though, give you access to the apt library, but the user 
    has to code in the functionality
    
    is it worth the effort?
        from the code i have seen that uses python-apt, no, atleast not for everything we need
        
    basically what we need are wrappers to apt utility's, which give us the ability to manipulate
    what happens...
    
    and maybe write our own code using python-apt for low level stuff...
    
    Note: see liraz notes on wrapping curl instead of interfacing with the curl library...
    
    
    </t>
<t tx="loni.20100902123045.3">FILE/DATA STRUCTURE

.chanko/
    config/
        sources.list
    cache/
        local/
            sources.list
            pkgcache.bin
            archives/        
            lists/
        remote/
            pkgcache.bin
            archives/        
            lists/
    state/
        dpkg/



GENERIC     Dir                         -&gt; $BASE/                           # BASE="`pwd`/.chanko"
GENERIC     Dir::Etc                    -&gt; config/
REMOTE      Dir::Cache                  -&gt; cache/remote
LOCAL       Dir::Cache                  -&gt; cache/local
LOCAL       Dir::Etc::SourceList        -&gt; $BASE/cache/local/sources.list   # created on the fly...
GENERIC     Dir::State                  -&gt; state/apt/
REMOTE      Dir::State::Lists           -&gt; $BASE/cache/remote/lists
LOCAL       Dir::State::Lists           -&gt; $BASE/cache/local/lists
GENERIC     Dir::State::status          -&gt; $BASE/state/dpkg/status

</t>
<t tx="loni.20100902123045.4">CLI SYNTAX

chanko-init [/path/to/sources.list]
    initialize a new chanko container
    if sources.list is specified, post initialization the chanko will be refreshed.
    if --dummy is specified, a dummy sources.list will be created, and the user will

chanko-refresh [-r | -l]
    refresh/resynchronize the package index files and cache as specified in sources.list
    by default, both remote and local will be refreshed

    Arguments:
        -r --remote
            refresh remote cache
    
        -l --local
            refresh local cache

chanko-get [-options] package[=version] ...
    get package(s) and their dependencies
        if a specific package version is requested, get that
        if a specific version is not requested, retrieve the newest version
    
    -f --force
        dont ask for confirmation before downloading
    
    -d --dir
        directory in which to store the package, default is CHANKO_DIR

    -t --tree
        output dir is in package tree format (like an automatic repository)
            $dir/n/neverland/neverland-&lt;version&gt;.&lt;arch&gt;.deb

        instead of
            $dir/neverland-&lt;version&gt;.&lt;arch&gt;.deb

chanko-query (-r | -l) [-options] [package_glob]
    if package_glob is provided, print only those packages whose names match the glob
    otherwise, by default, print a list of all packages
    
    Arguments:
        -r --remote
            query remote packages
    
        -l --local
            query local packages stored in the container

    Options:
        -i --info
            print full package information

        -a --all-versions
            print all available versions of a package
        
        -n --name-only
            print only the names of packages (without the package summary)
            incompatible with -info option


FUTURE 

upgrade
    get newest versions of packages in container

get options
    --source         # get source tarball (and diff)
    --build-dep      # get source package build-dependencies

add
    add manually downloaded deb so chanko knows about them

remove
    remove package

purge
    remove packages that are no longer needed which were pulled in to satisfy dependencies




</t>
<t tx="loni.20100902123045.5">cd prestine/karmic-i386

chanko-init --dummy
    initialize a new container with a dummy sources.list
    
xjed .chanko/config/sources.list
    update sources list to my liking...
        eg. deb http://archive.ubuntu.com/ubuntu jaunty main

chanko-refresh
    refresh/resynchronize the package index files and cache as specified in sources.list
    why? because we initialized with a dummy sources.list

chanko-query ...

chanko-get ...


</t>
<t tx="loni.20100902123045.6"></t>
<t tx="loni.20100902123045.7">
* create and document apt configuration
    * create prototype shell scripts for testing


directory structure
.chanko/
    etc/
        apt/
            apt.conf
            sources.list
    var/
        cache/
          apt/
            pkgcache.bin
            srcpkgcache.bin  
            archives/
                &lt;*.deb&gt;
                lock
                partial/
        lib/
            apt/
                extended_states
                lists/
                    &lt;*Packages&gt;
                    &lt;*Release&gt;
                    lock
                    partial/
            dpkg/
                lock
                status


more simplified...

.chanko/
    config/
        sources.list
    cache/
        pkgcache.bin
        srcpkgcache.bin  
        archives/
        lists/
    state/
        dpkg/
    

updated for local caching aswell (allows us to leverage apt-cache for local queries...)

.chanko/
    config/
        sources.list
    cache/
        local/
            sources.list
            pkgcache.bin
            archives/        
            lists/
        remote/
            pkgcache.bin
            archives/        
            lists/
    state/
        dpkg/


configuration options (to pass on cli)

Dir                         -&gt; $BASE
Dir::Etc                    -&gt; config/
Dir::Cache                  -&gt; cache/
Dir::State                  -&gt; state/apt/
Dir::State::Lists           -&gt; $BASE/cache/lists
Dir::State::status          -&gt; $BASE/state/dpkg/status

(has been updated, see file/data structure)

Q: how should we set the APT::Architecture?
    chanko-config arch=???
    manually in apt.conf
    config/arch &lt;- best option
        This is a FUTURE option, let the future take care of itself...


Q: how do i get local packages information?
Idea:
    create a package index:
        cd $chanko
        apt-ftparchive packages ./ &gt; .chanko/cache/local/Packages ????
            IDEA: use archives folder as it contains all the debs
        
    REMINDER: use --db option
        
    Q: how do i get apt-cache to spit out info from the local Packages file?
    
    IDEA:
        the "remote" pkgcache.bin is being created from lists/... according to sources.list
        we need a "local" pkgcache.bin,
            split cache/* into remote &amp; local
            create local sources.list and use it when running on local...


    update conf for local &amp; remote
    update init
    update refresh to create index and cache for local
    update query to get option (-r | -l), and pass it appropriate conf options
    
    IDEA: before a local query, refresh automatically
    TODO: research and test --db option

    Q: what should then Packages filename be?
    A:
        depends on sources.list entry
        ENTRY:      deb file:/// local debs
        FILENAME:   _dists_local_debs_binary-i386_Packages

    Q: what directory with the downloaded debs should we cache for local?
        ./
            we can then perform actions on manually downloaded debs
        .chanko/cache/remote/archives
            should include all downloaded debs
        .chanko/cache/local/archives -&gt; ../../remote/archives
            we are caching "local" debs
        
        easy things should be easy, hard things should be possible
        simple is good
        
        options 2 (or 3), and give user option to add a deb so chanko knows about it
            chanko-add path/to/manually/added/deb ??
            
TEST:
    multiple sources which include different versions of packages
    eg. jaunty , jaunty-backports
    
    RESULT: works beautifully....
        query on both
        get package gets latest version
        get package=VERSION gets the version
</t>
<t tx="loni.20100902123045.8">           
BASE="`pwd`/.chanko"

CONFIG="$BASE/config"
L_CACHE="$BASE/cache/local"
R_CACHE="$BASE/cache/remote"
STATE="$BASE/state"

opt1="-o Dir=$BASE/"
opt2="-o Dir::Etc=config/"
l_src="-o Dir::Etc::SourceList=$L_CACHE/sources.list"
l_opt3="-o Dir::Cache=cache/local"
r_opt3="-o Dir::Cache=cache/remote"
opt4="-o Dir::State=state/apt/"
l_opt5="-o Dir::State::Lists=$L_CACHE/lists"
r_opt5="-o Dir::State::Lists=$R_CACHE/lists"
opt6="-o Dir::State::status=$STATE/dpkg/status"

L_OPTIONS="$opt1 $opt2 $l_opt3 $opt4 $l_opt5 $opt6 $l_src"
R_OPTIONS="$opt1 $opt2 $r_opt3 $opt4 $r_opt5 $opt6"
</t>
<t tx="loni.20100902123045.9">#!/bin/bash

. conf
rm -rf $BASE

mkdir -p $CONFIG
echo "deb http://archive.ubuntu.com/ubuntu jaunty main" &gt; $CONFIG/sources.list

mkdir -p $L_CACHE/lists/partial
mkdir -p $L_CACHE/archives/partial
mkdir -p $R_CACHE/lists/partial
mkdir -p $R_CACHE/archives/partial

mkdir -p $STATE
mkdir -p $STATE/dpkg
touch $STATE/dpkg/status


</t>
<t tx="loni.20100902123045.10">#!/bin/bash

. conf

#apt-get $R_OPTIONS --print-uris update
apt-get $R_OPTIONS update

</t>
<t tx="loni.20100902123045.11">#!/bin/bash

. conf

echo "deb file:/// local debs" &gt; $L_CACHE/sources.list
apt-ftparchive packages $R_CACHE/archives &gt; $L_CACHE/lists/_dists_local_debs_binary-i386_Packages
apt-cache $L_OPTIONS gencaches


</t>
<t tx="loni.20100902123045.12">#!/bin/bash

. conf

apt-get $R_OPTIONS --print-uris install $@

</t>
<t tx="loni.20100902123045.13">#!/bin/bash

. conf

apt-cache $R_OPTIONS $@
</t>
<t tx="loni.20100902123045.14">#!/bin/bash

. conf

apt-cache $L_OPTIONS $@


</t>
<t tx="loni.20100902123045.15">* clean up and refactor code

</t>
<t tx="loni.20100902180534">flow:
    * get list of index files to download from sources.list
        options:
            write parser, or
            apt-get $OPTIONS --print-urisupdate (then just parse the uris)
    
    * ignore translation entries
    
    * get the release.gpg file (and corresponding Release file)
        (print-uris dont contain them, only the gpg's)
        verify the Release file
        if we already have a (compressed) Packages file
            parse the release files and test md5 to see if we have the latest
            if match, exit (we are up to date)
    
    * get the compressed Package files
    * verify integrity (md5)
    * uncompress Package files
    * regenerate cache

</t>
<t tx="loni.20100903152430">Syntax: query (-r | -l) [-options] [package_glob]
Query chanko container

If package_glob is provided, print only those packages whose names match the
glob otherwise, by default, print a list of all packages

Arguments:
  -r  --remote   Query remote packages
  -l  --local    Query local packages stored in the container

Options:
  --info         Print full package information
  --names-only   Print only the names of packages (without the package summary)
                 Incompatible with --info option


queries:
    print list of all packages with short description
        chanko-query (-r|-l)
        apt-cache search . | sort
    
    print list of all packages (without description)
        chanko-query (-r|-l) --names-only
        apt-cache pkgnames | sort
        
    print full package information on all packages
        chanko-query (-r|-l) --info
        apt-cache dumpavail

    print list of all packages with short description that match a package_glob
        chanko-query (-r|-l) package_glob
        apt-cache search package_glob | sort    

    print list of all packages (without description) that match a package_glob
        chanko-query (-r|-l) --names-only package_glob
        apt-cache pkgnames package_glob | sort
        
    print info on specific package
        chanko-query (-r|-l) --info package
        apt-cache show package</t>
<t tx="loni.20100904214912">
</t>
<t tx="loni.20100904214912.1">
* alon sets up a sumo arena with chanko, and gets files A, B, C
* alon then registers the arena with covin
* liraz registers the arena on his side, and merges
    * the merge replays the journal and downloads files A, B, C
* liraz now wants to use chanko to get/query
    * for that, he needs to create the cache
    * liraz does a chanko-refresh -a (maybe automatically on a get/query?)
        which downloads the Package and Release files for alons sources.list
        and indexes and caches both remote/local</t>
<t tx="loni.20100904215050">
current data structure is not very optimized for sumo, as it will
be "doing stuff" in the arena, which will included in the git-repo, 
and it shouldn't be.

we cannot use git-ignore, so we are going to seperate the data structure.
this will also allow us to create a download cache (similar to sumo's 
cache) available to all chanko containers.

Current data structure
----------------------
.chanko/
    config/
        sources.list
    cache/
        local/
            sources.list
            pkgcache.bin
            lists/
        remote/
            pkgcache.bin
            archives/
            lists/
    state/
        dpkg/

Proposed data structure
-----------------------

~/.chanko/                          # CHANKO_HOME
    caches/
        65sf36d6sdfs4dfsgdfs/
            local/
                sources.list
                pkgcache.bin
                lists/
            remote/
                pkgcache.bin
                lists/
    state/
        dpkg/


arena/.container/                   # CHANKO_BASE
    config/
        sources.list
        arch
        hash
    archives/               # leverage sumo-cp -l (hardlink copy)



implementation

* use new data structure
    * init should only create .container
    * refresh (cache init) should have init_create (and run it if it doesn't exist)
        Q: who/when should state/dpkg be created...

* consider using Paths class
    
    
    </t>
</tnodes>
</leo_file>
