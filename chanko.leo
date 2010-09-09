<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.332741792369">
	<global_window_position top="0" left="5" height="709" width="1127"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="loni.20100902123045" a="E"><vh>Project</vh>
<v t="loni.20100906222353" a="E"><vh>documentation</vh>
<v t="loni.20100906222353.1"><vh>initial release</vh></v>
</v>
<v t="loni.20100902123045.6" a="E"><vh>development log</vh>
<v t="loni.20100906214807" a="TV"><vh>v0.5 - initial release</vh>
<v t="loni.20100902123045.7"><vh>exploration</vh>
<v t="loni.20100902123045.8"><vh>conf</vh></v>
<v t="loni.20100902123045.9"><vh>init</vh></v>
<v t="loni.20100902123045.10"><vh>refresh-r</vh></v>
<v t="loni.20100902123045.11"><vh>refresh-l</vh></v>
<v t="loni.20100902123045.12"><vh>get</vh></v>
<v t="loni.20100902123045.13"><vh>query-r</vh></v>
<v t="loni.20100902123045.14"><vh>query-l</vh></v>
</v>
<v t="loni.20100902123045.1"><vh>design</vh>
<v t="loni.20100902123045.2"><vh>brainstorming</vh></v>
<v t="loni.20100902123045.3"><vh>file/data structure</vh></v>
<v t="loni.20100902123045.4"><vh>cli syntax</vh>
<v t="loni.20100906194713"><vh>init</vh></v>
<v t="loni.20100906194713.1"><vh>refresh</vh></v>
<v t="loni.20100906194713.2"><vh>query</vh></v>
<v t="loni.20100906194713.3"><vh>get</vh></v>
</v>
<v t="loni.20100902123045.5"><vh>usage examples</vh></v>
</v>
<v t="loni.20100906215012"><vh>implementation</vh>
<v t="loni.20100902180534"><vh>refresh</vh></v>
<v t="loni.20100903152430"><vh>query</vh></v>
<v t="loni.20100904214912" a="E"><vh>sumo integration</vh>
<v t="loni.20100904214912.1"><vh>use case</vh></v>
<v t="loni.20100904215050"><vh>file/data structure</vh></v>
<v t="loni.20100906132825"><vh>downloading</vh></v>
</v>
<v t="loni.20100906132825.1"><vh>global packages/releases</vh></v>
</v>
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

Q: how do i describe this project
A: efficiently get packages from public sources to be shared via sumo

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

CHANKO_HOME
-----------
~/.chanko/
    caches/
        65sf36d6sdfs4dfsgdfs/
            local/
                sources.list
                pkgcache.bin
                lists/
            remote/
                pkgcache.bin
                lists/
                    &lt;softlinks to global&gt;
        global/
            ...Packages.bz2
            ...Packages
            ...Releases

    state/
        dpkg/

CHANKO_BASE
-----------
arena/.container/
    config/
        sources.list
        hash
    archives/


</t>
<t tx="loni.20100902123045.4">CLI SYNTAX

Syntax: chanko &lt;command&gt; [args]

Configuration environment variables:
    CHANKO_HOME    Location of caches storage (default: $HOME/.chanko)
    CHANKO_BASE    Location of sumo arena (defaults to cwd)

Commands:
    get        Get package(s) and their dependencies
    init       Initialize a new chanko container
    query      Query chanko container
    refresh    Refresh chanko container index files and cache



</t>
<t tx="loni.20100902123045.5">cd /turnkey/fab/chanko
mkdir rocky
cd rocky

sumo-init
sumo-open
cd arena

chanko-init --dummy
xjed .container/config/sources.list     # update sources list manually
chanko-refresh -r                       # would have been done automatically if we init from sources.list

chanko-query -r                         # print list of all packages with short description
chanko-query -r git                     # print list of all packages with short description that match git glob
chanko-query -r --info git-core         # print info of qgit

chanko-get --tree git-core=1.2.3        # get package git-core (version 1.2.3) with dependencies and store them
                                          in a tree like format

chanko-query -l                         # print list of all local packages


</t>
<t tx="loni.20100902123045.6"></t>
<t tx="loni.20100902123045.7">CREATE TEST ENVIRONMENT

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
<t tx="loni.20100902123045.15">
* container options
    * arch  i386 | amd64 | powerpc | sparc
    * tree  BOOL
    
    cli options override container options

* verify Release files (gpg)
* research binany cache option in apt-ftparchive


FUTURE 

upgrade
    get newest versions of packages in container

get options
    --source         # get source tarball (and patch with diff)
    --build-dep      # get source package build-dependencies

query options
    --depends
    --rdepends

add
    add manually downloaded deb so chanko knows about them

remove
    remove package

purge
    remove packages that are no longer needed which were pulled in to satisfy dependencies




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
<t tx="loni.20100904214912"></t>
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
<t tx="loni.20100906132825">* downloading debs should be done via sumo-get, and sumo-cp -l used for hardlinking
    Q: should sumo be a dependency?
    Q: should we be able to use chanko when not in an arena?
        * we have the --dir option, what happens if the user specifies a directory under CHANKO_BASE
          idea: lets not let him: dont allow ^/(.*)
                append the dir passed to CHANKO_BASE
    
* downloading Packages and Release files should be done directly with curl


implementation
    init sumo test arena
    init chanko in test arena
    manually test sumo-get and sumo-cp -l
    update code...
        GOTCHA: setting SUMO_BASE doesn't work as expected, we have to chdir
    


</t>
<t tx="loni.20100906132825.1">~/.chanko/
    caches/
        65sf36d6sdfs4dfsgdfs/
            local/
                sources.list
                pkgcache.bin
                lists/
            remote/
                pkgcache.bin
                lists/          &lt;----- packages and releases files are stored here
    state/
        dpkg/
        
* we dont need to download and store several copies of the same Packages files in 
  multiple container caches.
* we can't use hardlinks, because then each container will keep its Packages
  we need to use softlinks

Q: what about release files? should they also be in the global cache?
A: it doesn't actually matter - they will have to be downloaded anyway
    but if they are in global they will take up less space... (not major though...)

        a containers cache will not be updated until it is refreshed (chanko-refresh -r)
        when it is refreshed, it will download the latest Release,
        check if the Packages are latest, and get them if need be
    

~/.chanko/
    caches/
        65sf36d6sdfs4dfsgdfs/
            local/
            remote/
                pkgcache.bin
                lists/
                    softlink_to_Packages/Releases_in_global
        global/
            *Packages.bz2
            *Packages
            *Releases
    state/
        dpkg/

</t>
<t tx="loni.20100906194713">Syntax: init /path/to/sources.list | --dummy
Initialize a new chanko container

If sources.list is specified, it will be used and the container will be
refreshed post initialization.

If --dummy is specified, an exemplary sources.list will be created.


</t>
<t tx="loni.20100906194713.1">Syntax: refresh (-r | -l | -a)
Refresh chanko container index files and cache

Arguments:
  -r  --remote   Resynchronize remote index files and refresh remote cache
  -l  --local    Regenerate local index and refresh local cache
  -a  --all      Refresh both remote and local

</t>
<t tx="loni.20100906194713.2">Syntax: query (-r | -l) [-options] [package_glob]
Query chanko container

If package_glob is provided, print only those packages whose names match the
glob otherwise, by default, print a list of all packages

Arguments:
  -r  --remote   Query remote packages
  -l  --local    Query local packages stored in the container

Options:
  --info         Print full package information
                 Incompatible with --names option
  --names        Print only the names of packages (without the package summary)
                 Incompatible with --info option
  --stats        Print statistics of the remote/local cache

</t>
<t tx="loni.20100906194713.3">Syntax: get [-options] package[=version] ...
Get package(s) and their dependencies

If a specific package version is requested, get that
If a specific version is not requested, retrieve the newest version

Options:
  --dir=         Relative directory path to CHANKO_BASE for package storage
                 Default is CHANKO_BASE
  --tree         Package storage in tree format (resembles automatic repository)
                     $dir/c/chanko/chanko-&lt;version&gt;.&lt;arch&gt;.deb
                 instead of
                     $dir/chanko-&lt;version&gt;.&lt;arch&gt;.deb
  --force        Dont ask for confirmation before downloading

</t>
<t tx="loni.20100906214807"></t>
<t tx="loni.20100906215012"></t>
<t tx="loni.20100906222353"></t>
<t tx="loni.20100906222353.1">CHANKO: efficiently get packages from public sources to be shared via sumo

Chanko, short for chanko-nabe, which is a stew (a type of nabemono or one-pot dish) commonly eaten in vast quantity by sumo wrestlers as part of a weight gain diet.

Chanko leverages sumo to share the public data sets it gets, hence the perfect name. in other words, chanko feeds sumo...

Chanko has 4 basic commands,
    init        initialize a new chanko container
    refresh     refresh chanko container index files and cache
    query       query chanko container
    get         get package(s) and their dependencies

and can be configured via 2 environment variables:
    CHANKO_HOME    Location of caches storage (default: $HOME/.chanko)
    CHANKO_BASE    Location of sumo arena (defaults to cwd)

Below is a basic overview of these commands, for more information consult the design notes, help from the commands themselves, or the source.

A chanko container should be initialized inside of a sumo arena, eg.

$ cd /turnkey/fab/chanko
$ mkdir rocky
$ cd rocky

$ sumo-init
$ sumo-open
$ cd arena
    
$ chanko-init --dummy

Initializing a chanko container will create the directory structure as follows in the CHANKO_BASE:
    
.container/
    config/
        sources.list
        hash
    archives/

Because we provided the dummy option, the sources.list in the config/ folder is a copy of the sources.list file found in /usr/share/chanko.

We could have provided a path to our own sources.list to use, which would also automatically initiate a refresh of the remote index and cache.

But, because we used the dummy option, we will edit the sources.list to our liking, and then manually refresh the remote index files and cache.

Note: Remote refers to the remote sources specified in the sources.list file local refers to the packages "got" by chanko

$ xjed .container/config/sources.list
$ chanko-refresh -r

The refreshing command with the -r (--remote) option resynchronize's the remote index files and refreshes the remote cache. It will store the downloaded files in the global cache so they may be shared by other containers. 

The cache is created in CHANKO_HOME and the directory structure looks similar to this once in full use:
    
~/.chanko/
    caches/
        &lt;container_hash&gt;
            local/
                sources.list
                pkgcache.bin
                lists/
            remote/
                pkgcache.bin
                lists/
                    &lt;softlinks to global&gt;
        global/
            &lt;Packages.bz2&gt;
            &lt;Packages&gt;
            &lt;Releases&gt;

    state/
        dpkg/

Now that our container has been "refreshed", we can use query.
Here are some examples:

$ chanko-query -r                  # print list of all packages with short description
$ chanko-query -r git              # print list of all packages with short description that match git glob
                                   
$ chanko-query -r --info git-core  # print info of qgit

Getting a package and its dependencies is as simple as:
    
$ chanko-get git-core

We may specify the exact version to get, if we do not want the newest version, along with other options such as to store the packages in a tree like format.

$ chanko-get --tree git-core=1.2.3

Note: Each package's integrity is checked via an expected md5 checksum.

The local container cache is refreshed automatically after a get operation.
We can verify that we have "got" the packages we requested but printing a list of all local packages

$ chanko-query -l

As mentioned before, consult each commands help documentation for all available options.

Enjoy.


</t>
</tnodes>
</leo_file>
