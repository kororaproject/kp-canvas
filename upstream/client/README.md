# Canvas

Canvas is a Korora Project initiative to simplify the composition, distribution and management of customised Korora (and Fedora) systems. Canvas draws inspiration from a number of existing solutions that provide OS customisation and building including:

* [openSUSE Build Service](https://build.opensuse.org/)
* [Revisor](https://fedorahosted.org/revisor/), and
* [Spacewalk](https://fedorahosted.org/spacewalk/)

Some fundamental goals of the Canvas project include:

* To provide a simple and intuitive interface for system composition,
* Fitted for extensibility, and
* Allow trivial management of your installs.

## Component Overview
The broad components understood to Canvas are:

 * Packages,
 * Repos,
 * Stores,
 * Objects,
 * Templates, and
 * Machines

Packages and Repos are the traditional representations as you know them. A package is an installable piece of software that provides a level of functionality for your system. Your OS is typically composed of 100s to possibly 1000s of individual packages. Repos are the store for where Packages can be fetched from.

Templates are the recipes for how particular systems are to be composed. They will specify the Repos available and the Packages to be installed to make the final compositions.

Machines are managed systems assigned a Template.

## Getting Started

#### Use Case #1
So `firnsy` has has just done a clean install and has his system package and repo selection just how he likes it. Let's make a template out of it for future usage; we'll call it `laptop`.
```
canvas template add firnsy:laptop
canvas template push firnsy:laptop
```

Let's say he then goes and adds some packages for to try out, crawls down some dependency rabbit holes installing packages left, right and centre. We have a problem, `firnsy` wants to go back to exactly how it was before he started messing around. Easy.
```
canvas template pull firnsy:laptop --clean
```

Order restored.

#### Use Case #2
The `kororaproject` have just pushed out their fancy new `steam` template which turns your desktop into an awesome Steam focused gaming console experience and you want in. You've being fussing with this package and that package but couldn't get it quite right.

```
canvas template pull kororaproject:steam --clean
shutdown -r now
```

Game on!

## Command Line Reference
The Canvas command line provides the necessary tools to add, update, remove, synchronise and command your systems to your will.

### Global Options
The following options are global to all commands:
```
-U|--user  # specify canvas user
-H|--host  # specify canvas server host
```

The default user is the name of the system user account invoking the `canvas` command. The default user can also be specified in the `~/.config/canvas.conf`.

The default host is the Korora Project canvas server located at https://canvas.kororaproject.org/. The default host can also be specified in the `~/.config/canvas.conf`.

### Configuration

#### Command Overview
The following commands are available for the management of Canvas templates:
```
canvas config [--unset] option.name [value]
```

You can query/set/replace/unset options with this command. The `option.name` argument is actually the section and the key separated by a dot, and the value will be escaped.

### Templates
The following commands allow adding, removing, modifying, querying, and synchronising Canvas templates.

#### Command Overview
The following commands are available for the management of Canvas templates:
```
canvas template add [user:]template[@version] [--name] [--title] [--description] [--includes] [--public]
canvas template update [user:]template[@version] [--name] [--title] [--description] [--includes] [--public]
canvas template rm [user:]template[@version]
canvas template push [user:]template[@version] [--all] [--kickstart]
canvas template pull [user:]template[@version] [--clean]
canvas template diff [user_from:][template_from[@version]|path_from] [[user_to:]template_to[@version]|path_to] [--output=path]
canvas template copy [user_from:]template_from[@version] [[user_to:]template_to[@version]]
canvas template list [user] [--filter-name] [--filter-version] [--filter-description]
canvas template dump [user:]template[@version] [--json|--yaml]
```

#### Adding Templates
The general usage for adding a new template to a Canvas user is described as:
```
canvas template add [user:]template[@version] [--name] [--title] [--description] [--includes] [--public]
```

For example, adding a new blank template identifed as `htpc` to the Canvas user `firnsy`.
```
canvas template add firnsy:htpc
```

Adding a new template identifed as `htpc` to the Canvas user `firnsy` that is based on the `core` template from Canvas user `kororaproject` can be done with:
```
canvas template add firnsy:htpc --includes kororaproject:core
```

When adding new templates they will be private by default. If you wish to make your templates available for others to see then set the `--public` flag to a value of `true` or `1`.

Template names are restricted to the following character classes: lower and upper case alphabetic letters, digits, `-`, and `_`.

#### Updating Templates
The general usage for updating an existing template of a Canvas user is described as:
```
canvas template update [user:]template[@version] [--name] [--version] [--title] [--description] [--includes] [--public]
```

Updating the name and description of existing template `htpc` of Canvas user `firnsy`.
```
canvas template update firnsy:htpc --name="Firnsy's HTPC" --description="Ultimate HTPC recipe!"
```

#### Removing Templates
The general usage for removing an existing template of a Canvas user is described as:
```
canvas template rm [user:]template[@version]
```

Removing the existing template `htpc` from Canvas user `firnsy`.
```
canvas template rm firnsy:htpc
```

#### Synchronising Templates
The general usage for synchronising an existing template of a Canvas user is described as:
```
canvas template push [user:]template[@version] [--all] [--kickstart]
canvas template pull [user:]template[@version] [--clean]
```

For example the following command would install all packages and repos specified in the template `htpc` from the Canvas user `firnsy` to the current system. No packages would be removed from the current system.
```
canvas template pull firnsy:htpc
```

To ensure the package and repos matched the specified template exactly, just add the `--clean` option. This will remove any packages and repos from the current system that are not specified in the template. You should ensure you have any important data backed up first in case of any issues with the template.
```
canvas template pull firnsy:htpc --clean
```

In order to add the current repos and any packages installed by the user of the current system to the template, simply invoke:
```
canvas template push firnsy:htpc
```

Alternatively if you want to include all packages on the system (including dependencies of user installed packages) then simply add the `--all` option:
```
canvas template push firnsy:htpc --all
```

Another option is pushing the contents of a kickstart file. Just specify the `--kickstart` option with the path to the kickstart file, such as:
```
canvas template push firnsy:htpc --kickstart ~/kickstarts/htpc.ks
```

#### Diff Templates
The general usage for viewing the differences between existing templates and/or the current system configuration is:
```
canvas template diff [user_from:][template_from[@version]|path_from] [[user_to:]template_to[@version]|path_to] [--output=path]
```

Either an existing template or the path to a file on the current system can be specified as arguments. Specifying one argument will compare it to the current system configuration. For example, the following command would show the diff between the current system to the template `htpc` from Canvas user `firnsy`:
```
canvas template diff firnsy:htpc
```

Specifying two arguments will compare them to eachother only instead of to the current system configuration. You may specify either templates or files for one or both arguments. If a file path is specified, it must be the full path to the file.
```
canvas template diff firnsy:htpc kororaproject:htpc
canvas template diff firnsy:htpc ~/templates/htpc.template
canvas template diff ~/templates/htpc.template kororaproject:htpc
canvas template diff ~/templates/htpc.template /tmp/foo.template
```

Specifying no arguments will find the difference between the current Canvas configuration and the packages that are already present on the system itself.
```
canvas template diff
```

You can use the `--output` option to save the diff information to a file in the specified path. If the file already exists, it will be replaced.
```
canvas template diff firnsy:htpc --output=~/templates/htpc.template
```

#### Copying Templates
The general usage for copying an existing template of a Canvas user to a new one is described as:
```
canvas template copy [user_to:]template_from[@version] [[user_to:]template_to[@version]]
```

For example the following command would copy the `htpc` template from `kororaproject` to the template `my-htpc` for the Canvas user `firnsy`.
```
canvas template copy kororaproject:htpc firnsy:my-htpc
```

If `firnsy` wanted to retain the same template name he could have abbreviated to:
```
canvas template copy kororaproject:htpc
```

#### Listing Templates
The general usage for listing templates that are currently accessible is described as:
```
canvas template list [user] [--filter-name] [--filter-version] [--filter-description]
```

If no filters are provided, all public templates and any that belong to you will be listed:
```
canvas template list
```

If a user is specified, only templates owned by that user (and matching given filters) will be shown.
```
canvas template list firnsy
```

If one or more filters are provided, any public templates and templates you own matching all of the provided filters will be shown.
```
canvas template list --filter-description="media center"
```

Multiple filters and multiple items per filter can be specified. Specifying a user as well limits the list to packages matching the filters that belong to that user only. Searching may take longer depending on the query provided.
```
canvas template list kororaproject --filter-name=*workstation* --filter-description=office
```

#### Dumping Templates
The general usage for dumping (or viewing) templates that are currently accessible is described as:
```
canvas template dump [user:]template[@version] [--json|--yaml|--kickstart]
```

By default the template will be dumped in a human readable format. You can dump to a machine readable `json` or `yaml` encoded format by adding the `--json` or `--yaml` options respectively. You can also dump a compliant kickstart file for automating ISO creation or anaconda installs via the `--kickstart` option.

### Template Packages
The following commands allow management of packages from specified Templates.

#### Command Overview
The following commands are available for the management of Canvas template packages:
```
canvas package add [user:]template[@version] [--nodeps] package1 packagelist1 package2 ... packageN
canvas package list [user:]template[@version] [--filter-name] [--filter-summary] [--filter-description] [--filter-arch] [--filter-repo] [--output=path]
canvas package rm [user:]template[@version] [--nodeps] package1 package2 ... packageN
```

#### Package Definition
The syntax for package definitions is described as:
```
name[[#epoch]@version-release][:arch]
```

When specifying packages it is possible to be as generic or explicit as you wish with regard to epoch, version, release and arch.

The version and epoch will default to the latest available if not specified. When arch isn't specified and there is more than one available, the target system's default architecture will be used.

Note that `version` and `release`, if specified, must be specified together, and an `#epoch` cannot be specified without them.

Examples of package definitions include:
```
foo                   # name only
foo:x86_64            # name and arch
foo@2.1-3             # name, version and release
foo#1@2.1-3:x86_64    # name, epoch, version, release and arch
```

#### Adding Packages
The general usage for adding packages from templates is described as:
```
canvas package add [user:]template[@version] [--nodeps] package1 packagelist1 package2 ... packageN
```

One or multiple packages can be listed, or one or more package file lists can be specified in place of or in addition to the packages. The file must contain a space- or newline-separated list of packages.
```
canvas package add firnsy:htpc foo bar:i686 baz#1@2.1-3:x86_64
canvas package add firnsy:htpc buz@2.1-3 ~/templates/htpc.packages /tmp/foo.packages
```

##### Included and Excluded Packages
By default a package is assumed to be an `included` package for a template. That is it will be installed (i.e. `included`) when synchronised to a system. You can specify that a package should be `excluded` by prefixing the package definition with `~`. This will ensure that a package is removed (if installed) from a system when synchronised with the template.

For example:
```
canvas package add firnsy:htpc kodi ~totem ~vlc
```

##### Adding Dependencies

If `--with-deps` is specified, the immediate dependencies of any listed packages will also be added.
```
canvas package add firnsy:htpc --with-deps kodi    #kodi's dependencies will also be pulled in
```

#### Removing Packages
The general usage for removing packages from templates is described as:
```
canvas package rm [user:]template[@version] [--nodeps] package1 package2 ... packageN
```

If `--nodeps` is specified, the dependencies of any listed packages will not be automatically removed.
```
canvas package rm firnsy:htpc bar
canvas package rm firnsy:htpc --nodeps foo baz
```

#### Listing Packages
The general usage for listing packages in templates is described as:
```
canvas package list [user:]template[@version] [--filter-name] [--filter-summary] [--filter-description] [--filter-arch] [--filter-repo] [--output=path]
```

If no filters are provided, all packages belonging to the specified template will be listed.
```
canvas package list firnsy:htpc
```

If one or more filters are provided, only packages belonging to that template which match all of the specified filters will be listed.
```
canvas package list firnsy:htpc --filter-arch=x86_64
```

Multiple filters and multiple items per filter can be specified. Searching may take longer depending on the query provided.
```
canvas package list firnsy:htpc --filter-name=foo --filter-summary=bar --filter-description=baz,buz --filter-arch=i386 --filter-repo=rpmfusion
```

You can use the `--output` option to save the package list to a file in the specified path. If the file already exists, it will be replaced.
```
canvas package list firnsy:htpc --output=/home/firnsy/templates/boom
```

### Template Repos
The following commands allow management of repos from specified Templates.

#### Command Overview
The following commands are available for the management of Canvas template repos:
```
canvas repo add [user:]template[@version] repo_name [--filepath] [--baseurl] [--metalink] [--mirrorlist] [--cost] [--enabled] [--gpgkey] [--name] [--priority]
canvas repo update [user:]template[@version] repo_name [--baseurl] [--metalink] [--mirrorlist] [--cost] [--enabled] [--gpgkey] [--name] [--priority]
canvas repo list [user:] template[@version]
canvas repo rm [user:]template[@version] repo_name
```

#### Repos Definitions
The allowed characters of the `repo` ID string are restricted to the following character classes: lower and upper case alphabetic letters, digits, `-`, and `_` .

##### Repo Options
`cost` (integer)

The relative cost of accessing this repository, defaulting to 1000. This value is compared when the priorities of two repositories are the same. The repository with the lowest cost is picked. It is useful to make the library prefer on-disk repositories to remote ones.

`baseurl` (list)

URLs for the repository.

`enabled` (boolean)

Include this repository as a package source. The default is True.

`gpgkey` (list of strings)

URLs of a GPG key files that can be used for signing metadata and packages of this repository, empty by default. If a file can not be verified using the already imported keys, import of keys from this option is attempted and the keys are then used for verification.

`metalink` (string)

URL of a metalink for the repository.

`mirrorlist` (string)

URL of a mirrorlist for the repository.

`name` (string)

A human-readable name of the repository. Defaults to the ID of the repository.

`priority` (integer)

The priority value of this repository, default is 99. If there is more than one candidate package for a particular operation, the one from a repo with the lowest priority value is picked, possibly despite being less convenient otherwise (e.g. by being a lower version).

`skip_if_unavailable` (boolean)

If enabled, DNF will continue running and disable the repository that couldn’t be contacted for any reason when downloading metadata. This option doesn’t affect skipping of unavailable packages after dependency resolution. To check inaccessibility of repository use it in combination with refresh command line option. The default is True.

#### Adding Repos
The general usage for adding repos from templates is described as:
```
canvas repo add [user:]template[@version] repo_name --repofile [--baseurl] [--metalink] [--mirrorlist] [--cost] [--enabled] [--gpgkey] [--name] [--priority]
```

The following commands would add the `rpmfusion` repo to the `htpc` template of user `firnsy`:
```
canvas repo add firnsy:htpc rpmfusion --mirrorlist='http://mirrors.rpmfusion.org/mirrorlist?repo=nonfree-fedora-$releasever&arch=$basearch'
canvas repo add firnsy:htpc rpmfusion --repofile=/etc/yum.repos.d/rpmfusion.repo
```

##### Included and Excluded Repos
By default a repository is assumed to be an `included` repository for a template. That is it will be configured (i.e. `included`) when synchronising packages to a system. You can specify that a repository should be `excluded` by prefixing the package definition with `~`. This will ensure that a repository is not configured (if defined for inclusion in a parent template) on a system when synchronised with the template.

For example:
```
canvas repo add firnsy:htpc ~fedora ~fedora-updates
```

#### Updating Repos
The general usage for updating repos from templates is described as:
```
canvas repo update [user:]template[@version] repo_name [--baseurl] [--metalink] [--mirrorlist] [--cost] [--enabled] [--gpgkey] [--name] [--priority]
```

```
canvas repo update firnsy:htpc rpmfusion --priority=50
```

#### Listing Repos
The general usage for listing repos in templates is described as:
```
canvas repo list [user:]template[@version]
```

```
canvas repo list firnsy:htpc
```

#### Removing Repos
The general usage for removing repos from templates is described as:
```
canvas repo rm [user:]template repo_name
```

```
canvas repo rm firnsy:htpc rpmfusion
```

### Template Objects
The following commands allow management of objects from specified Templates.

#### Command Overview
The following commands are available for the management of Canvas template objects:
```
canvas object add [user:]template[@version] object_name --source=... --action=... [--action=...]
canvas object list [user:]template[@version] [--filter-source=...] [--filter-name=...]
canvas object rm [user:]template[@version] object_name1 object_name2 ... object_nameN
```

#### Adding Objects
The general usage for adding objects to templates is described as:
```
canvas object add [user:]template[@version] object_name --source=... --action=... [--action=...]
```

One or multiple objects can be listed, or one or more object file lists can be specified in place of or in addition to the objects. The file must contain a space- or newline-separated list of store:object references.
```
canvas object add firnsy:htpc ~/movie.objects --action='copy:"/data"'
canvas object add firnsy:htpc sickbeard --source https://firnsy.com/canvas/sickbeard.tar.gz --action='extract:"/srv/sickbeard"' --action='execute:"/srv/sickbeard/install"'
```

##### Included and Excluded Objects
By default an object is assumed to be an `included` object for a template. That is it will be actioned (i.e. `included`) when synchronised to a system. You can specify that an object should be `excluded` (i.e. not acted upon) by prefixing the object definition with `~`. This will ensure that an object is not actioned (if included) in a parent template.

For example:
```
canvas object add firnsy:htpc ~services:sabnzbd
```

#### Removing Objects
The general usage for removing objects from templates is described as:
```
canvas object rm [user:]template[@version] store1:object_name1 store2:object_name2 ... storeN:object_nameN
```

```
canvas object rm firnsy:htpc services:sickbeard
```

#### Listing Objects
The general usage for listing objects in templates is described as:
```
canvas object list [user:]template[@version] [--filter-store=...] [--filter-name=...] [--filter-description=]
```

If no filters are provided, all objects belonging to the specified template will be listed.
```
canvas object list firnsy:htpc
```

If one or more filters are provided, only objects belonging to that template which match all of the specified filters will be listed.
```
canvas object list firnsy:htpc --filter-store=services
```

Multiple filters and multiple items per filter can be specified. Searching may take longer depending on the query provided.
```
canvas object list firnsy:htpc --filter-name=foo --filter-description=baz,buz
```

You can use the `--output` option to save the object list to a file in the specified path. If the file already exists, it will be replaced.
```
canvas objecte list firnsy:htpc --output=/home/firnsy/templates/boom
```


### Template Stores
The following commands allow management of repos from specified Templates.

#### Command Overview
The following commands are available for the management of Canvas template repos:
```
canvas store add [user:]template[@version] store_name [--type] [--url] [--user] [--pass]
canvas store update [user:]template[@version] store_name [--type] [--url] [--user] [--pass]
canvas store list [user:]template[@version]
canvas store rm [user:]template[@version] store_name

canvas store get [user:]template[@version]/store name1 name2 ... nameN
canvas store put [user:]template[@version]/store file1[:name1] file2[:name1] ... fileN[:nameN]
```

#### Stores Definitions
The allowed characters of the `store_name` are restricted to the following character classes: lower and upper case alphabetic letters, digits, `-`, and `_` .

##### Store Options
`type` (string)

The type of service this store is attached to. Examples include: `google-drive`, `owncloud` and `ssh`.

`url` (string)

URL (or IP) of the service this store is attached to. Not required for `google-drive` stores.

`user` (string)

Username to use when connecting to the attached service.

`pass` (string)

Password to use when connecting to the attached service.

#### Adding Stores
The general usage for adding repos from templates is described as:
```
canvas store add [user:]template store_name [--type] [--url] [--user] [--pass]
```

The following commands would add the `movies` store to the `htpc` template of user `firnsy`:
```
canvas store add firnsy:htpc movies --type=ssh --url=192.168.0.100 --user=admin --pass=supersecret
```

##### Included and Excluded Stores
By default a store is assumed to be an `included` store for a template. That is it will be configured (i.e. `included`) when synchronising objects to a system. You can specify that a store should be `excluded` by prefixing the package definition with `~`. This will ensure that a store is not configured (if defined for inclusion in a parent template) on a system when synchronised with the template.

For example the following command will ensure any stores in parent templates will not propogate to :
```
canvas store add firnsy:htpc ~parent-store
```

#### Updating Stores
The general usage for updating stores from templates is described as:
```
canvas store update [user:]template[@version] store_name [--type] [--url] [--user] [--pass]
```

```
canvas store update firnsy:htpc movies --url=192.168.0.10
```

#### Listing Stores
The general usage for listing stores in templates is described as:
```
canvas store list [user:]template[@version]
```

```
canvas store list firnsy:htpc
```

#### Removing Stores
The general usage for removing stores from templates is described as:
```
canvas store rm [user:]template[@version] store_name
```

The following example will remove the `movies` store from the template `htpc` owned by `firnsy`.
```
canvas store rm firnsy:htpc movies
```

#### Downloading Objects from Stores
The general usage for downloading objects from stores is described as:
```
canvas store get [user:]template[@version][/store_name] name1 name2 ... nameN
```

The `store_name` is an optional argument, ommission indicates the object will be retrieved from the internal template store.
```
canvas store get firnsy:htpc/movies foo my-bar
canvas store get firnsy:htpc startup-script
```

#### Uploading Objects to Stores
The general usage for uploading objects to stores is described as:
```
canvas store put [user:]template[@version][/store_name] file1[:name1] file2[:name1] ... fileN[:nameN]
```

By default, the object name will have the same basename as the file uploaded. This can be overridden by appending an alternative `:name` after the path. For example the following command will upload to the `movies` store the local file at `/path/to/foo` with the name `foo` and a second local file at `/path/to/bar` with the name `my-bar`.
```
canvas store put firnsy:htpc/movies /path/to/foo /path/to/bar:my-bar
```

The `store_name` is an optional argument, ommission indicates the object will be inserted from the internal template store. The internal store can store a total of 32 files each with a maximum size of 100kB each. Due to storage consraints, using the internal store is only recommended for small files (e.g. start/stop scripts and configuration files).
```
canvas store put firnsy:htpc /path/to/script:startup-script
```


### Machines
The following commands allow adding, removing and updating Canvas machines that are assigned templates. Machines are your configured Canvas systems that can be managed and easily synchronised with your latest configurations.

Machines have a 1-to-1 link with a Canvas template. For example, you may assign your HTPC to a personalised template called `htpc`. Alternatively you may assign your laptop and desktop to your `all-my-favourite-things` template, any changes you make to the template would then be easily reflected on both your laptop and desktop computer.

#### Command Overview
The following commands are available for the management of Canvas machines:
```
canvas machine add|update [user:]name[@version] [--description=] [--location=] [--name=] [--version] [--template=]
canvas machine rm [user:]name[@version]
canvas machine diff [user:]name[@version] [--output=path]
canvas machine sync [user:]name[@version] [--pull [[user:]template[@version]]] | --push [user:]template[@version]]
canvas machine cmd [user:]name[@version] command arg1 arg2 ... argN
```

#### Adding Machines
The general usage for adding a new managed machine to a Canvas user is described as:
```
canvas machine add [user:]name [--description=] [--location=] [--name=] [--version=] [--template=]
```

To add the current system as a managed machine named `odin` to the Canvas user `firnsy` linked to the `htpc` template from the same Canvas user is as follows:
```
canvas machine add firnsy:odin --template firnsy:htpc
```

#### Updating Machines
The general usage for updating an existing managed machine of a Canvas user is described as:
```
canvas machine update [user:]name [--description=] [--name=] [--version=] [--template=]
```

For example to change the recently added machine from the `htpc` template to the `steam` template from Canvas user `firnsy` we can simply invoke:
```
canvas machine update firnsy:odin --template firnsy:steam
```

#### Removing Machines
The general usage for removing an existing managed machine to a Canvas user is described as:
```
canvas machine rm [user:]name[@version]
```

For example:
```
canvas machine rm firnsy:odin
```

#### Diff Machines
To determine the state of a machine with respect to it's assigned template. Can be used to determine whether a machine requires re-sync with the template or not.

The general usage for diff'ing an existing managed machine of a Canvas user is described as:
```
canvas machine diff [user:]name[@version] [--output=path]
```

For example to view the diff status of the machine `odin` of Canvas user `firnsy` relative to its assigned template can be done with the following command:
```
canvas machine diff firnsy:odin
```

You can use the `--output` option to save the diff information to a file in the specified path. If the file already exists, it will be replaced.
```
canvas machine diff firnsy:odin --output=/home/firnsy/templates/odin
```

#### Synchronising Machines
The general usage for synchronising an existing managed machine of a Canvas user is described as:
```
canvas machine sync [user:]name[@version] [--pull [[user:]template[@version]]] | --push [user:]template[@version]]
```

For example synchronising machine `odin` of Canvas user `firnsy` is done with the following command:
```
canvas machine sync firnsy:odin
```

To create a new template `custom` from machine `odin` of Canvas user `firnsy` to the same account, you can do:
```
canvas machine sync firnsy:odin --push firnsy:custom
```

To revert the machine `odin` of Canvas user `firnsy` to the time of last sync, you can do:
```
canvas machine sync firnsy:odin --pull
```

To reset the machine `odin` of Canvas user `firnsy` to the template `htpc` of Canvas user `firnsy`, simply:
```
canvas machine sync firnsy:odin --pull firnsy:htpc
```

#### Commanding Machines
The general usage for sending a command to an existing managed machine of a Canvas user is described as:
```
canvas machine cmd [user:]name[@version] command arg1 arg2 ... argN
```

Examples of running remote commands on the machine `odin` of Canvas user `firnsy` are shown below.
```
canvas machine cmd firnsy:odin cat /etc/passwd
canvas machine cmd firnsy:odin ls /home
canvas machine cmd firnsy:odin shutdown -h now
canvas machine cmd firnsy:odin bash
```

## Unit tests
Running the unit tests requires python3 nose:

```
dnf install python3-nose
```

Unit tests should be run from the lib/canvas/test directory:

```
cd lib/canvas/test/
python3 -m "nose"
```
