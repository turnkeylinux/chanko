Chanko - Efficiently get packages from public sources
=====================================================

Why the name 'Chanko'?
----------------------

Chanko, short for chanko-nabe, is a stew (a type of nabemono or one-pot
dish) commonly eaten in vast quantity by sumo wrestlers as part of a
weight gain diet.

Chanko initially leveraged a project called sumo for caching and sharing
the public data sets (hence the name - chanko feeds sumo), but has since
dropped it's dependency of sumo, but the name has stuck.

Commands
--------

Chanko has 5 commands::

    get         - Get package(s) and their dependencies
    upgrade     - Upgrade packages according to plan
    purge       - Purge superseded packages
    refresh     - Refresh the index files and cache
    query       - Query the chanko

Refer to the commands help for more information, for example::

    chanko-get --help

Filesystem anatomy
------------------

::

    .internal/  - created automatically, used internally
    archives/   - created automatically, stores downloaded packages
    config/     - configuration folder, see below
    plan/       - create automatically, see below

Configuration
-------------

A chanko requires 3 files stored in the sub-folder config/

For example::

    $ cat config/sources.list
    deb http://cdn.debian.net/debian squeeze main
    deb http://security.debian.org/ squeeze/updates main

    $ gpg --keyring ./config/trustedkeys.gpg --list-keys
    pub   4096R/473041FA 2010-08-27 [expires: 2018-03-05]
    uid                  Debian Archive Automatic Signing Key (6.0/sq...

    pub   4096R/B98321F9 2010-08-07 [expires: 2017-08-05]
    uid                  Squeeze Stable Release Key <debian-release@l...

    $ cat config/chanko.conf
    RELEASE=debian/squeeze
    PLAN_CPP=-DFOO=y

Plans
-----

Plans are stored in the plans sub-folder. A plan can be named anything
but there are 2 'special' plan names::

    - plan/main     - new packages added to the chanko with chanko-get
                      will be appended to this plan by default.

    - plan/nodeps   - if the --no-deps flag is specified with
                      chanko-get, new packages will be appended here.
                      When chanko-upgrade is executed, the packages
                      specified in this plan will not pull dependencies.

Due to the nature of chanko, there might be instances where packages
conflict with one another, in which case chanko-upgrade will fail. In
this case, another plan should be used to specify one of the conflicting
packages.

Plans are processed through cpp which give plans some intelligence, as
well as support for cpp comments. Automatically, the architecture and
plan folder will be specified as additional cpp_opts.

For example::

    #ifdef FOO
    #include <include/foo>
    #endif

    #ifdef I386
    linux-image-686
    #endif

    #ifdef AMD64
    linux-image-amd64
    #endif

Usage examples
--------------

Creating a chanko from scratch (ie. transition)::

    CODENAME=...

    mkdir $FAB_PATH/chankos/$CODENAME.chanko
    cd $FAB_PATH/chankos/$CODENAME.chanko

    mkdir config
    echo RELEASE=debian/$CODENAME > config/chanko.conf
    echo PLAN_CPP=-DTURNKEY=y >> config/chanko.conf

    cp ../PREVIOUS_CODENAME.chanko/config/sources.list config/sources.list
    sed -i "s|PREVIOUS_CODENAME|$CODENAME|g" config/sources.list

    mkdir -p plan/include
    cp ../PREVIOUS_CODENAME.chanko/plan/main plan/main
    cp ../PREVIOUS_CODENAME.chanko/plan/include/turnkey plan/include/turnkey

    # http://packages.debian.org/debian-archive-keyring
    # download deb from same directory as dsc link
    mkdir tmp
    dpkg-deb -x debian-archive-keyring_*_all.deb tmp
    gpg --list-keys --keyring=./tmp/usr/share/keyrings/debian-archive-keyring.gpg
    cp tmp/usr/share/keyrings/debian-archive-keyring.gpg config/trustedkeys.gpg
    rm -rf tmp *.deb

    git-init
    echo .internal > .gitignore
    echo archives >> .gitignore
    git-add .
    git-commit -m "initial commit"

    chanko-upgrade

